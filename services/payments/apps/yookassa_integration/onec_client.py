import subprocess
import time
from decimal import Decimal
from urllib.parse import quote, urljoin
from xml.etree import ElementTree as ET

import requests
from django.conf import settings
from django.utils import timezone


class OneCError(RuntimeError):
    pass


def _to_odata_payload(data):
    if isinstance(data, dict):
        if "value" in data and isinstance(data["value"], list):
            return data["value"]
        if "d" in data:
            nested = data["d"]
            if isinstance(nested, dict) and "results" in nested:
                return nested["results"]
            return nested
    return data


def _escape_odata_string(value):
    return str(value).replace("'", "''")


def _extract_entity(data):
    payload = _to_odata_payload(data)
    if isinstance(payload, list):
        return payload[0] if payload else None
    return payload


def _parse_datetime(value):
    if not value:
        return None
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    return str(value)


def _parse_atom_response(xml_text):
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
        "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
    }

    def parse_entry(entry):
        properties = entry.find("atom:content/m:properties", ns)
        if properties is None:
            return {}
        data = {}
        for child in list(properties):
            tag = child.tag.split("}", 1)[-1]
            data[tag] = child.text
        return data

    root = ET.fromstring(xml_text)
    tag = root.tag.split("}", 1)[-1]
    if tag == "feed":
        entries = [parse_entry(entry) for entry in root.findall("atom:entry", ns)]
        return {"value": entries}
    if tag == "entry":
        return parse_entry(root)
    return {}


class OneCClient:
    def __init__(self):
        self.transport_mode = getattr(settings, "ONEC_TRANSPORT_MODE", "direct")

    def ensure_customer(self, invoice):
        customer = self._get_single(
            "Catalog_Клиенты",
            **{"$filter": f"CRM_ID eq '{_escape_odata_string(invoice.contact_id)}'"},
        )
        if customer:
            return customer["Ref_Key"]

        payload = {
            "Description": invoice.contact_name or f"Клиент CRM #{invoice.contact_id}",
            "CRM_ID": str(invoice.contact_id or ""),
            "Email": invoice.contact_email or "",
            "Телефон": invoice.contact_phone or "",
            "ТипКлиента": getattr(settings, "ONEC_DEFAULT_CUSTOMER_TYPE", "crm"),
        }
        created = self._request("POST", "Catalog_Клиенты", json=payload)
        entity = _extract_entity(created)
        if not entity or not entity.get("Ref_Key"):
            raise OneCError("1С не вернула Ref_Key для клиента.")
        return entity["Ref_Key"]

    def ensure_service(self, invoice):
        crm_service_id = invoice.service_id or invoice.id
        service = self._get_single(
            "Catalog_Услуги",
            **{"$filter": f"crm_id eq '{_escape_odata_string(crm_service_id)}'"},
        )
        if service:
            return service["Ref_Key"]

        amount = int(Decimal(invoice.amount))
        payload = {
            "Description": invoice.service_name or f"Услуга CRM #{crm_service_id}",
            "crm_id": str(crm_service_id),
            "Цена": amount,
            "Единица": getattr(settings, "ONEC_SERVICE_UNIT", "шт"),
            "Активность": getattr(settings, "ONEC_SERVICE_ACTIVITY", "Активна"),
        }
        created = self._request("POST", "Catalog_Услуги", json=payload)
        entity = _extract_entity(created)
        if not entity or not entity.get("Ref_Key"):
            raise OneCError("1С не вернула Ref_Key для услуги.")
        return entity["Ref_Key"]

    def get_organization_key(self):
        configured_key = getattr(settings, "ONEC_ORGANIZATION_KEY", "")
        if configured_key:
            return configured_key
        organization = self._get_single("Catalog_Организации", **{"$top": 1})
        if not organization or not organization.get("Ref_Key"):
            raise OneCError("В 1С не найдена организация для выставления счета.")
        return organization["Ref_Key"]

    def create_invoice_document(self, invoice):
        organization_key = self.get_organization_key()
        customer_key = self.ensure_customer(invoice)
        service_key = self.ensure_service(invoice)
        amount = float(invoice.amount)

        payload = {
            "Date": timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "CRM_Invoice_ID": str(invoice.id),
            "CRM_Deal_ID": str(invoice.deal_id),
            "Организация_Key": organization_key,
            "Клиент_Key": customer_key,
            "EmailКлиента": invoice.contact_email or "",
            "СтатусСчета": getattr(settings, "ONEC_STATUS_UNPAID_VALUE", "НеОплачен"),
            "СуммаДокумента": amount,
            "Комментарий": invoice.comment or invoice.deal_title or "",
            "Состав": [
                {
                    "LineNumber": 1,
                    "Услуга_Key": service_key,
                    "Количество": 1,
                    "Цена": amount,
                    "Сумма": amount,
                }
            ],
        }
        created = self._request("POST", "Document_СчетПокупателю", json=payload)
        entity = _extract_entity(created)
        if not entity or not entity.get("Ref_Key"):
            raise OneCError("1С не вернула Ref_Key для документа счета.")

        if getattr(settings, "ONEC_AUTO_POST_DOCUMENTS", False):
            self.post_document("Document_СчетПокупателю", entity["Ref_Key"])

        return {
            "external_id_1c": entity["Ref_Key"],
            "invoice_number_1c": entity.get("Number", ""),
        }

    def register_payment(self, invoice, payment_payload):
        if not invoice.onec_document_id:
            raise OneCError("Нельзя зарегистрировать оплату без документа счета в 1С.")

        paid_at = _parse_datetime(invoice.paid_at or payment_payload.get("captured_at") or timezone.now())
        payment_id = payment_payload.get("id") or invoice.payment_id or f"invoice-{invoice.id}"
        payment_method = payment_payload.get("payment_method", {})
        invoice_link_field = getattr(settings, "ONEC_PAYMENT_INVOICE_FIELD", "Счет_Key")

        payload = {
            invoice_link_field: invoice.onec_document_id,
            "CRM_Payment_ID": str(payment_id),
            "YooKassaPaymentID": str(payment_id),
            "СуммаОплаты": float(invoice.amount),
            "ДатаПодтвержденияОплаты": paid_at,
            "СпособОплаты": payment_method.get("type") or getattr(settings, "ONEC_DEFAULT_PAYMENT_METHOD", "yookassa"),
            "Комментарий": f"Оплата по счету CRM #{invoice.id} / сделка #{invoice.deal_id}",
        }
        created = self._request("POST", "Document_ОплатаПоСчету", json=payload)
        entity = _extract_entity(created)
        if not entity or not entity.get("Ref_Key"):
            raise OneCError("1С не вернула Ref_Key для документа оплаты.")

        if getattr(settings, "ONEC_AUTO_POST_DOCUMENTS", False):
            self.post_document("Document_ОплатаПоСчету", entity["Ref_Key"])

        self._request(
            "PATCH",
            self._entity_path("Document_СчетПокупателю", invoice.onec_document_id),
            json={"СтатусСчета": getattr(settings, "ONEC_STATUS_PAID_VALUE", "Оплачен")},
        )

        return {
            "payment_document_id_1c": entity["Ref_Key"],
            "invoice_status": getattr(settings, "ONEC_STATUS_PAID_VALUE", "Оплачен"),
        }

    def post_document(self, entity_set, ref_key):
        post_path = f"{self._entity_path(entity_set, ref_key)}/Post"
        return self._request(
            "POST",
            post_path,
            params={"PostingModeOperational": str(getattr(settings, "ONEC_POSTING_MODE_OPERATIONAL", False)).lower()},
        )

    def _get_single(self, entity_set, **params):
        response = self._request("GET", entity_set, params=params)
        payload = _to_odata_payload(response)
        if isinstance(payload, list):
            return payload[0] if payload else None
        return payload

    def _request(self, method, path, params=None, json=None):
        if self.transport_mode == "bridge":
            return self._request_via_bridge(method, path, params=params, json=json)
        return self._request_direct(method, path, params=params, json=json)

    def _request_direct(self, method, path, params=None, json=None):
        self._prepare_direct_request()
        response = requests.request(
            method=method,
            url=urljoin(f"{settings.ONEC_ODATA_BASE_URL.rstrip('/')}/", path),
            params=params,
            json=json,
            timeout=settings.ONEC_TIMEOUT_SECONDS,
            auth=self._direct_auth(),
            headers={"Accept": "application/json"},
        )
        return self._handle_response(response, path)

    def _request_via_bridge(self, method, path, params=None, json=None):
        headers = {"Accept": "application/json"}
        secret = getattr(settings, "ONEC_BRIDGE_SECRET", "")
        if secret:
            headers["X-Bridge-Secret"] = secret
        response = requests.post(
            settings.ONEC_BRIDGE_URL,
            json={
                "method": method,
                "path": path,
                "params": params or {},
                "json": json,
                "timeout": settings.ONEC_TIMEOUT_SECONDS,
                "restart_before_request": getattr(settings, "ONEC_RESTART_EACH_REQUEST", True),
            },
            timeout=settings.ONEC_BRIDGE_TIMEOUT_SECONDS,
            headers=headers,
        )
        return self._handle_response(response, path)

    def _prepare_direct_request(self):
        if not getattr(settings, "ONEC_RESTART_EACH_REQUEST", True):
            return
        restart_command = getattr(settings, "ONEC_RESTART_COMMAND", "").strip()
        if restart_command:
            completed = subprocess.run(
                restart_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=settings.ONEC_RESTART_TIMEOUT_SECONDS,
            )
            if completed.returncode != 0:
                raise OneCError(
                    f"Не удалось выполнить перезапуск 1С/IIS: {completed.stderr.strip() or completed.stdout.strip()}"
                )
        self._wait_until_available()

    def _wait_until_available(self):
        deadline = time.monotonic() + settings.ONEC_HEALTH_TIMEOUT_SECONDS
        health_url = urljoin(f"{settings.ONEC_ODATA_BASE_URL.rstrip('/')}/", settings.ONEC_HEALTHCHECK_PATH.lstrip("/"))
        last_error = None
        while time.monotonic() < deadline:
            try:
                response = requests.get(
                    health_url,
                    timeout=settings.ONEC_HEALTHCHECK_TIMEOUT_SECONDS,
                    auth=self._direct_auth(),
                    headers={"Accept": "application/json"},
                )
                if response.status_code < 500:
                    return
                last_error = f"status={response.status_code}"
            except requests.RequestException as exc:
                last_error = str(exc)
            time.sleep(settings.ONEC_HEALTHCHECK_INTERVAL_SECONDS)
        raise OneCError(f"1С/IIS не восстановилась после перезапуска: {last_error or 'таймаут'}")

    def _direct_auth(self):
        if settings.ONEC_USERNAME and settings.ONEC_PASSWORD:
            return (settings.ONEC_USERNAME, settings.ONEC_PASSWORD)
        return None

    def _handle_response(self, response, path):
        content_type = response.headers.get("Content-Type", "")
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = response.text
            raise OneCError(f"1С запрос {path} вернул {response.status_code}: {payload}")

        if "json" in content_type or response.text.strip().startswith("{"):
            try:
                return response.json()
            except ValueError:
                pass
        if "xml" in content_type or response.text.lstrip().startswith("<?xml"):
            try:
                return _parse_atom_response(response.text)
            except ET.ParseError:
                pass
        if not response.text:
            return {}
        return {"raw": response.text}

    def _entity_path(self, entity_set, ref_key):
        encoded_set = quote(entity_set, safe="_")
        return f"{encoded_set}(guid'{ref_key}')"
