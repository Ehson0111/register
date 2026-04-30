import json
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone


class OneCErrorV2(RuntimeError):
    pass


class OneCClientV2:
    """
    Новый клиент для работы с 1С через обновленный bridge сервис
    Поддерживает бизнес-логику CRM-1С интеграции
    """
    
    def __init__(self):
        self.bridge_url = settings.ONEC_BRIDGE_URL
        self.bridge_secret = getattr(settings, "ONEC_BRIDGE_SECRET", "")
        self.timeout = getattr(settings, "ONEC_BRIDGE_TIMEOUT_SECONDS", 60)

    def _request_bridge(self, endpoint, payload):
        """Отправляет запрос в bridge сервис"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.bridge_secret:
            headers["X-Bridge-Secret"] = self.bridge_secret
        
        url = f"{self.bridge_url.rstrip('/')}/{endpoint}"
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get("success", True):
                raise OneCErrorV2(result.get("message", "Ошибка выполнения операции в 1С"))
                
            return result
            
        except requests.RequestException as e:
            raise OneCErrorV2(f"Ошибка связи с bridge сервисом: {e}")
        except json.JSONDecodeError as e:
            raise OneCErrorV2(f"Ошибка парсинга ответа bridge: {e}")

    def create_invoice(self, invoice):
        """
        Создание счета в 1С
        
        Args:
            invoice: объект Invoice модели
            
        Returns:
            dict: {
                "document_id": "ID документа в 1С",
                "document_number": "Номер счета в 1С",
                "crm_invoice_id": "ID счета в CRM",
                "crm_deal_id": "ID сделки в CRM"
            }
        """
        payload = {
            "crm_invoice_id": invoice.id,
            "crm_deal_id": invoice.deal_id,
            "customer_name": invoice.contact_name or f"Клиент #{invoice.contact_id}",
            "customer_email": invoice.contact_email or "",
            "service_name": invoice.service_name or f"Услуга #{invoice.service_id}",
            "amount": float(invoice.amount),
            "comment": invoice.comment or invoice.deal_title or ""
        }
        
        result = self._request_bridge("invoice/create", payload)
        
        return {
            "external_id_1c": result["document_id"],
            "invoice_number_1c": result["document_number"],
            "crm_invoice_id": result["crm_invoice_id"],
            "crm_deal_id": result["crm_deal_id"]
        }

    def register_payment(self, invoice, payment_payload):
        """
        Регистрация оплаты в 1С
        
        Args:
            invoice: объект Invoice модели
            payment_payload: данные от YooKassa
            
        Returns:
            dict: {
                "payment_document_id_1c": "ID документа оплаты в 1С",
                "invoice_status": "Оплачен"
            }
        """
        if not invoice.onec_document_id:
            raise OneCErrorV2("Нельзя зарегистрировать оплату без документа счета в 1С")
        
        # Извлекаем данные из YooKassa payload
        yookassa_payment_id = payment_payload.get("id") or invoice.payment_id
        amount = payment_payload.get("amount", {}).get("value") or float(invoice.amount)
        captured_at = payment_payload.get("captured_at")
        payment_method = payment_payload.get("payment_method", {}).get("type", "yookassa")
        
        payload = {
            "crm_invoice_id": invoice.id,
            "onec_document_id": invoice.onec_document_id,
            "yookassa_payment_id": yookassa_payment_id,
            "amount": float(amount),
            "payment_date": captured_at or timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payment_method": payment_method,
            "comment": f"Оплата по счету CRM #{invoice.id} / сделка #{invoice.deal_id}"
        }
        
        result = self._request_bridge("payment/register", payload)
        
        return {
            "payment_document_id_1c": result["payment_document_id"],
            "invoice_status": "Оплачен"
        }

    def health_check(self):
        """Проверка доступности bridge сервиса"""
        try:
            response = requests.get(
                self.bridge_url.replace("/invoke", "/health") if "/invoke" in self.bridge_url else f"{self.bridge_url}/health",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
