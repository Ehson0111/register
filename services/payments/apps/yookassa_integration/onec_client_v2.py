import os
import uuid
import subprocess
import time
import ctypes
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

import requests
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime


class OneCErrorV2(RuntimeError):
    pass


# Значения перечисления 1С «СтатусыСчконета» — только ASCII в исходнике, без риска

ONEC_INVOICE_STATUS_PAID = "\u041e\u043f\u043b\u0430\u0447\u0435\u043d"  # Оплачен
ONEC_INVOICE_STATUS_UNPAID = "\u041d\u0435\u041e\u043f\u043b\u0430\u0447\u0435\u043d"  # НеОплачен
ONEC_PAYMENT_INVOICE_LINK_FIELD = "\u0421\u0447\u0435\u0442_Key"  # Счет_Key
# UTF-8 «Оплачен», ошибочно прочитанный как cp1252 (то, что видит 1С в ошибке OData).
ONEC_INVOICE_STATUS_PAID_MOJIBAKE = ONEC_INVOICE_STATUS_PAID.encode("utf-8").decode("cp1252")


def _coerce_payment_invoice_field(value):
    normalized = str(value or "").strip()
    if not normalized or "?" in normalized:
        return ONEC_PAYMENT_INVOICE_LINK_FIELD
    return normalized


def _coerce_invoice_status_value(value, *, default):
    if not value:
        return default
    normalized = str(value).strip()
    if normalized in (ONEC_INVOICE_STATUS_PAID, ONEC_INVOICE_STATUS_UNPAID):
        return normalized
    if normalized == ONEC_INVOICE_STATUS_PAID_MOJIBAKE:
        return ONEC_INVOICE_STATUS_PAID
    try:
        repaired = normalized.encode("cp1252").decode("utf-8")
        if repaired in (ONEC_INVOICE_STATUS_PAID, ONEC_INVOICE_STATUS_UNPAID):
            return repaired
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return default if normalized == ONEC_INVOICE_STATUS_PAID_MOJIBAKE else normalized


def is_admin():
    """Проверка, запущен ли процесс от имени администратора (только Windows)."""
    try:
        if os.name != "nt":
            return False
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def restart_iis():
    """Перезапуск IIS/пула 1С для учебной версии """
    command = getattr(settings, "ONEC_RESTART_COMMAND", "").strip()
    timeout = int(getattr(settings, "ONEC_RESTART_TIMEOUT_SECONDS", 30))

    if not command:
        if os.name == "nt":
            command = "iisreset"
        else:
            return False

    if os.name == "nt" and command.lower().startswith("iisreset") and not is_admin():
        return False

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return False
        time.sleep(3)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


class OneCClientV2:
    """
    Клиент для работы с 1С через OData API
    """
    
    def __init__(self):
        self.base_url = getattr(
            settings,
            "ONEC_ODATA_BASE_URL",
            "http://host.docker.internal/1c/odata/standard.odata",
        ).rstrip("/")
        self.use_auth = bool(getattr(settings, "ONEC_USERNAME", "") and getattr(settings, "ONEC_PASSWORD", ""))
        self.login = getattr(settings, "ONEC_USERNAME", "")
        self.password = getattr(settings, "ONEC_PASSWORD", "")
        self.timeout = getattr(settings, "ONEC_TIMEOUT_SECONDS", 60)
        self.auto_restart = getattr(settings, "ONEC_RESTART_EACH_REQUEST", False)
        self.max_retries = int(getattr(settings, "ONEC_MAX_RETRIES", 3))
        self.is_docker_runtime = os.path.exists("/.dockerenv")
        self.base_url_candidates = self._build_base_url_candidates()
        self.paid_status_value = _coerce_invoice_status_value(
            getattr(settings, "ONEC_STATUS_PAID_VALUE", ONEC_INVOICE_STATUS_PAID),
            default=ONEC_INVOICE_STATUS_PAID,
        )
        self.unpaid_status_value = _coerce_invoice_status_value(
            getattr(settings, "ONEC_STATUS_UNPAID_VALUE", ONEC_INVOICE_STATUS_UNPAID),
            default=ONEC_INVOICE_STATUS_UNPAID,
        )
        self.payment_invoice_field = _coerce_payment_invoice_field(
            getattr(settings, "ONEC_PAYMENT_INVOICE_FIELD", ONEC_PAYMENT_INVOICE_LINK_FIELD),
        )

    def _invoice_entity_path(self, invoice_guid):
        guid = str(invoice_guid).strip()
        return f"Document_СчетПокупателю(guid'{guid}')"

    def _get_session(self):
        """Создаёт сессию с авторизацией если нужно"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        if self.use_auth and self.login and self.password:
            session.auth = (self.login, self.password)
        return session

    def _is_retriable_error(self, response=None, exception=None):
        if exception is not None:
            return True
        if response is None:
            return False
        if response.status_code >= 500:
            return True
        text = (response.text or "").lower()
        if response.status_code in (400, 408, 429):
            return "ограничен" in text or "подключен" in text or "timeout" in text
        return False

    def _build_base_url_candidates(self):
        configured = self.base_url.rstrip("/")
        configured = configured.replace("host.docker.inrenal", "host.docker.internal")
        configured = configured.replace("standart.odata", "standard.odata")
        if not configured:
            configured = "http://host.docker.internal/1c/odata/standard.odata"

        parsed = urlsplit(configured)
        host = parsed.hostname or ""
        candidate_hosts = [host]
        if host in ("localhost", "127.0.0.1"):
            # Если явно настроили localhost/127.0.0.1, пробуем и host.docker.internal
           
            if self.is_docker_runtime:
                candidate_hosts = ["host.docker.internal", host]
            else:
                candidate_hosts.append("host.docker.internal")
        else:
            # В Docker НЕЛЬЗЯ падать на localhost/127.0.0.1 как на "fallback":
            candidate_hosts.append("host.docker.internal")
            if not self.is_docker_runtime:
                candidate_hosts.extend(["localhost", "127.0.0.1"])

        seen = set()
        candidates = []
        for candidate_host in candidate_hosts:
            if not candidate_host:
                continue
            netloc = candidate_host
            if parsed.port:
                netloc = f"{candidate_host}:{parsed.port}"
            candidate_url = urlunsplit((parsed.scheme or "http", netloc, parsed.path, "", "")).rstrip("/")
            if candidate_url not in seen:
                seen.add(candidate_url)
                candidates.append(candidate_url)
        return candidates

    def _request_with_retry(self, method, endpoint, *, params=None, json=None):
        last_error = None
        session = self._get_session()

        for base_url in self.base_url_candidates:
            url = f"{base_url}/{endpoint.lstrip('/')}"
            try:
                for attempt in range(self.max_retries):
                    if self.auto_restart:
                        restart_iis()
                    try:
                        response = session.request(
                            method,
                            url,
                            timeout=self.timeout,
                            params=params,
                            json=json,
                        )
                    except requests.RequestException as exc:
                        last_error = exc
                        if attempt < self.max_retries - 1 and self._is_retriable_error(exception=exc):
                            restart_iis()
                            continue
                        break

                    if response.ok:
                        return response

                    last_error = requests.HTTPError(
                        f"{response.status_code} {response.reason}: {response.text}",
                        response=response,
                    )
                    if attempt < self.max_retries - 1 and self._is_retriable_error(response=response):
                        restart_iis()
                        continue
                    break
            except Exception as exc:
                last_error = exc
                continue

        raise OneCErrorV2(f"Ошибка запроса к 1С: {last_error}")

    def _load_catalog_items_with_fallback(self, catalog_name, params=None):
        """
        Некоторые инсталляции 1С за reverse-proxy не принимают $top/$filter.
        В этом случае пробуем запрос без query-параметров.
        """
        try:
            response = self._request_with_retry("GET", catalog_name, params=params)
            return response.json().get("value", [])
        except OneCErrorV2:
            response = self._request_with_retry("GET", catalog_name)
            return response.json().get("value", [])

    def _extract_crm_id(self, item):
        for key in ("CRM_ID", "crm_id", "Crm_Id", "crmId", "CRMId"):
            value = item.get(key)
            if value is not None and str(value).strip() != "":
                return value
        return None

    def _get_by_guid(self, catalog_name, filter_field, filter_value):
        """Получает запись из справочника по GUID"""
        params = {
            "$filter": f"{filter_field} eq guid'{filter_value}'",
            "$top": 1
        }
        items = self._load_catalog_items_with_fallback(catalog_name, params=params)
        filter_value_str = str(filter_value).lower()
        for item in items:
            current = str(item.get(filter_field, "")).lower()
            if current == filter_value_str:
                return item
        return items[0] if items else None

    def _get_by_crm_id(self, catalog_name, crm_id):
        """Получает запись из справочника по CRM_ID"""
        params = {
            "$filter": f"CRM_ID eq {crm_id}",
            "$top": 1
        }
        items = self._load_catalog_items_with_fallback(catalog_name, params=params)
        for item in items:
            value = self._extract_crm_id(item)
            if value is None:
                continue
            try:
                if int(value) == int(crm_id):
                    return item
            except (TypeError, ValueError):
                if str(value).strip() == str(crm_id).strip():
                    return item
        return None

    def _create_service(self, invoice):
        service_guid = str(uuid.uuid4())
        service_name = (invoice.service_name or f"Услуга CRM #{invoice.service_id}").strip()
        payload = {
            "Ref_Key": service_guid,
            "Description": service_name,
            "Цена": int(float(invoice.amount)),
            "Единица": "шт",
            "Активность": "Да",
            "DeletionMark": False,
            "crm_id": str(invoice.service_id),
            "CRM_ID": str(invoice.service_id),
        }
        response = self._request_with_retry("POST", "Catalog_Услуги", json=payload)
        if response.status_code not in (200, 201):
            raise OneCErrorV2(f"Не удалось создать услугу в 1С для CRM_ID={invoice.service_id}")
        return self._get_by_crm_id("Catalog_Услуги", invoice.service_id) or {"Ref_Key": service_guid, "Цена": payload["Цена"]}

    def _create_client(self, invoice):
        client_guid = str(uuid.uuid4())
        client_name = (invoice.contact_name or f"Клиент CRM #{invoice.contact_id}").strip()
        payload = {
            "Ref_Key": client_guid,
            "Description": client_name,
            "DeletionMark": False,
            "Predefined": False,
            "ТипКлиента": "Физическое лицо",
            "CRM_ID": str(invoice.contact_id),
            "crm_id": str(invoice.contact_id),
        }
        if invoice.contact_email:
            payload["Email"] = invoice.contact_email
        if invoice.contact_phone:
            payload["Телефон"] = invoice.contact_phone

        response = self._request_with_retry("POST", "Catalog_Клиенты", json=payload)
        if response.status_code not in (200, 201):
            raise OneCErrorV2(f"Не удалось создать клиента в 1С для CRM_ID={invoice.contact_id}")
        return self._get_by_crm_id("Catalog_Клиенты", invoice.contact_id) or {"Ref_Key": client_guid}

    def _build_invoice_payload(self, invoice, client_guid, service_guid, service_price):
        base_payload = {
            "Ref_Key": str(uuid.uuid4()),
            # "Date": datetime.now().isoformat(),
            "Date": timezone.now().replace(microsecond=0).isoformat(),

            # "Организация_Key": org_guid,
            "Клиент_Key": client_guid,
            "СуммаДокумента": float(invoice.amount),
            "СтатусСчета": self.unpaid_status_value,
            "Состав": [
                {
                    "LineNumber": 1,
                    "Услуга_Key": service_guid,
                    "Количество": 1,
                    "Цена": int(service_price),
                    "Сумма": float(invoice.amount),
                }
            ],
        }
        # Пишем CRM-поля в отдельные реквизиты документа (как в тестовом скрипте).
        base_payload["CRM_Invoice_ID"] = str(invoice.id)
        base_payload["CRM_Deal_ID"] = str(invoice.deal_id)
        if invoice.contact_email:
            base_payload["EmailКлиента"] = invoice.contact_email
        if invoice.comment:
            base_payload["Комментарий"] = invoice.comment[:300]
        return base_payload

    def _build_invoice_payload_variants(self, invoice, client_guid, service_guid, service_price):
        """
        1С-конфигурации могут отличаться по доступным реквизитам.
        Пытаемся от полного набора полей к базовому.
        """
        full_payload = self._build_invoice_payload(invoice, client_guid, service_guid, service_price)

        no_custom_crm_fields = dict(full_payload)
        no_custom_crm_fields.pop("CRM_Invoice_ID", None)
        no_custom_crm_fields.pop("CRM_Deal_ID", None)

        minimal_payload = dict(no_custom_crm_fields)
        minimal_payload.pop("EmailКлиента", None)
        
        minimal_payload.pop("Комментарий", None)

        return [full_payload, no_custom_crm_fields, minimal_payload]

    def create_invoice(self, invoice):
        """
        Создание счета в 1С через OData API
        
        Args:
            invoice: объект Invoice модели
            
        Returns:
            dict: {
                "external_id_1c": "GUID документа в 1С",
                "invoice_number_1c": "Номер счета в 1С"
            }
        """
        if not invoice.service_id:
            raise OneCErrorV2("У счета отсутствует service_id из CRM.")
        if not invoice.contact_id:
            raise OneCErrorV2("У счета отсутствует contact_id из CRM.")

        # Получаем GUID услуги по service_id из CRM
        service = self._get_by_crm_id("Catalog_Услуги", invoice.service_id)
        if not service:
            service = self._create_service(invoice)
        if not service:
            raise OneCErrorV2(f"Услуга с CRM_ID={invoice.service_id} не найдена и не создана в 1С")
        service_guid = service['Ref_Key']
        service_price = service.get('Цена', float(invoice.amount))
        
        # Получаем GUID клиента по contact_id из CRM
        client = self._get_by_crm_id("Catalog_Клиенты", invoice.contact_id)
        if not client:
            client = self._create_client(invoice)
        if not client:
            raise OneCErrorV2(f"Клиент с CRM_ID={invoice.contact_id} не найден и не создан в 1С")
        client_guid = client['Ref_Key']
        
        # # Получаем первую организацию (можно настроить выбор по ID)
        # orgs = self._load_catalog_items_with_fallback("Catalog_Организации", params={"$top": 1})
        # if not orgs:
        #     raise OneCErrorV2("Нет организаций в справочнике 1С")
        # org_guid = orgs[0]['Ref_Key']
        
        variants = self._build_invoice_payload_variants(
            invoice, client_guid, service_guid, service_price
        )
        resp = None
        invoice_guid = ""
        last_error = None
        for invoice_data in variants:
            invoice_guid = invoice_data["Ref_Key"]
            try:
                resp = self._request_with_retry("POST", "Document_СчетПокупателю", json=invoice_data)
                break
            except OneCErrorV2 as exc:
                last_error = exc
                continue

        if resp is None:
            raise OneCErrorV2(f"Не удалось создать счёт в 1С: {last_error}")
        
        if resp.status_code not in (200, 201):
            raise OneCErrorV2(f"Ошибка создания счета в 1С: {resp.status_code} - {resp.text}")
        
        # Проводим счёт
        post_resp = self._request_with_retry(
            "POST",
            f"Document_СчетПокупателю('{invoice_guid}')/Post",
            json={"PostingModeOperational": True},
        )
        
        if post_resp.status_code not in (200, 204):
            raise OneCErrorV2(f"Счёт создан но не проведён: {post_resp.status_code} - {post_resp.text}")
        
        return {
            "external_id_1c": invoice_guid,
            "invoice_number_1c": invoice.invoice_number
        }

    def register_payment(self, invoice, payment_payload):
        """
        Регистрация оплаты в 1С через OData API
        
        Args:
            invoice: объект Invoice модели
            payment_payload: данные от YooKassa
            
        Returns:
            dict: {
                "payment_document_id_1c": "GUID документа оплаты в 1С",
                "invoice_status": "Оплачен"
            }
        """
        if not invoice.onec_document_id:
            raise OneCErrorV2("Нельзя зарегистрировать оплату без документа счета в 1С")

        # Защита от разных состояний документа: перед оплатой повторно проводим счёт.
        # Это повторяет рабочий сценарий из ручных тестов 1С и безопасно для уже проведённого документа.
        post_invoice_resp = self._request_with_retry(
            "POST",
            f"{self._invoice_entity_path(invoice.onec_document_id)}/Post",
            json={"PostingModeOperational": True},
        )
        if post_invoice_resp.status_code not in (200, 204):
            raise OneCErrorV2(
                f"Не удалось провести счёт перед регистрацией оплаты: "
                f"{post_invoice_resp.status_code} - {post_invoice_resp.text}"
            )

        # Извлекаем данные из YooKassa payload
        amount = payment_payload.get("amount", {}).get("value") or float(invoice.amount)
        captured_raw = payment_payload.get("captured_at") or ""
        parsed_captured = parse_datetime(captured_raw) if captured_raw else None
        now_iso = timezone.now().replace(microsecond=0).isoformat()
        confirmed_at = (parsed_captured.replace(microsecond=0).isoformat() if parsed_captured else None) or now_iso
        yk_payment_id = (payment_payload.get("id") or invoice.payment_id or "").strip()

        invoice_link_field = self.payment_invoice_field
        paid_status_value = self.paid_status_value

        # Создаём оплату
        payment_guid = str(uuid.uuid4())
        payment_data = {
            "Ref_Key": payment_guid,
            "Date": now_iso,
            "СуммаОплаты": float(amount),
            "СпособОплаты": "Банковская карта",
            "ДатаПодтвержденияОплаты": confirmed_at,
            "CRM_Payment_ID": str(invoice.id),
            "YooKassaPaymentID": yk_payment_id,
            "Счет_Key": invoice.onec_document_id,
        }

        if invoice_link_field and invoice_link_field != "Счет_Key":
            payment_data[invoice_link_field] = invoice.onec_document_id
        
        resp = self._request_with_retry("POST", "Document_ОплатаПоСчету", json=payment_data)
        
        if resp.status_code not in (200, 201):
            raise OneCErrorV2(f"Ошибка создания оплаты в 1С: {resp.status_code} - {resp.text}")
        
        # Проводим оплату
        post_resp = self._request_with_retry(
            "POST",
            f"Document_ОплатаПоСчету('{payment_guid}')/Post",
            json={"PostingModeOperational": True},
        )
        
        if post_resp.status_code not in (200, 204):
            raise OneCErrorV2(f"Оплата создана но не проведена: {post_resp.status_code} - {post_resp.text}")

        # Во многих конфигурациях 1С создание документа оплаты не меняет статус счёта автоматически.
        # После успешного проведения оплаты пробуем явно пометить счёт как оплаченный.
        # ВАЖНО: если обновить статус счёта не удалось, НЕ падаем с ошибкой (иначе ретрай создаст дубль оплаты).
        payment_date_invoice = getattr(settings, "ONEC_PAYMENT_DATE_USE_CAPTURED", "false").lower() == "true"
        invoice_payment_date = confirmed_at if payment_date_invoice else now_iso
        update_variants = [
            {"СтатусСчета": paid_status_value},
            {"СтатусСчета": paid_status_value, "ДатаОплаты": invoice_payment_date},
        ]
        update_error = None
        invoice_path = self._invoice_entity_path(invoice.onec_document_id)
        for payload in update_variants:
            try:
                self._request_with_retry("PATCH", invoice_path, json=payload)
                update_error = None
                break
            except OneCErrorV2 as exc:
                update_error = exc
                continue

        status_updated = update_error is None
        if not status_updated and self.is_invoice_paid_in_onec(invoice.onec_document_id):
            status_updated = True
            update_error = None

        return {
            "payment_document_id_1c": payment_guid,
            "invoice_status": self.paid_status_value,
            "invoice_status_updated": status_updated,
            "invoice_status_update_error": (str(update_error) if update_error is not None else ""),
        }

    def ensure_invoice_paid_status(self, invoice):
        """
        Пытается обновить статус счёта в 1С на 'Оплачен' без создания повторной оплаты.
        Используется если оплата уже есть, но статус счёта не обновился.
        """
        if not invoice.onec_document_id:
            raise OneCErrorV2("У счета нет onec_document_id для обновления статуса в 1С")
        invoice_path = self._invoice_entity_path(invoice.onec_document_id)
        if self.is_invoice_paid_in_onec(invoice.onec_document_id):
            return True
        self._request_with_retry(
            "PATCH",
            invoice_path,
            json={"СтатусСчета": self.paid_status_value},
        )
        return self.is_invoice_paid_in_onec(invoice.onec_document_id)

    def fetch_invoice(self, onec_document_id):
        response = self._request_with_retry(
            "GET",
            self._invoice_entity_path(onec_document_id),
        )
        return response.json()

    def is_invoice_paid_in_onec(self, onec_document_id):
        try:
            data = self.fetch_invoice(onec_document_id)
        except OneCErrorV2:
            return False
        status = _coerce_invoice_status_value(
            data.get("СтатусСчета"),
            default="",
        )
        return status == self.paid_status_value

    def health_check(self):
        """Проверка доступности OData сервиса 1С"""
        try:
            response = self._request_with_retry("GET", "Catalog_Услуги", params={"$top": 1})
            return response.status_code == 200
        except Exception:
            return False
