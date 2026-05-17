import json
import logging
import time
import uuid

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from yookassa import Configuration, Payment
from yookassa.domain.exceptions.api_error import ApiError

from .invoice_sync_v2 import create_invoice_in_onec, register_payment_in_onec, retry_due_invoice_sync
from .models import Invoice
from .permissions import IsManagerOrAdmin
from .serializers import InvoiceSerializer

logger = logging.getLogger(__name__)

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def _auth_headers_from_request(request):
    auth = request.headers.get("Authorization", "")
    headers = {"Accept": "application/json"}
    if auth:
        headers["Authorization"] = auth
    return headers


def _contact_service_url(path):
    base = settings.CONTACT_SERVICE_URL.rstrip("/")
    return f"{base}/api{path}"


def _resolve_public_base_url(request=None):
    configured = (getattr(settings, "PUBLIC_PAYMENTS_BASE_URL", "") or "").rstrip("/")
    if configured:
        return configured
    if request:
        return f"{request.scheme}://{request.get_host()}"
    return "http://localhost:8012"


def _public_payment_url(invoice_id, request=None):
    base = _resolve_public_base_url(request=request)
    return f"{base}/payment/pay/{invoice_id}/"


def _generate_invoice_number(deal_id):
    return f"СЧЕТ-{deal_id:06d}"


def _extract_service_context(deal):
    """
    Нормализует service_id/service_name из разных форматов payload сделки:
    - {"service": 4}
    - {"service_id": 4}
    - {"service": {"id": 4, "name": "..."}}
    """
    service_raw = deal.get("service")
    service_id = deal.get("service_id")
    service_name = deal.get("service_name", "")

    if service_id in (None, "", 0):
        if isinstance(service_raw, dict):
            service_id = service_raw.get("id") or service_raw.get("pk")
            service_name = service_name or service_raw.get("name") or service_raw.get("title", "")
        else:
            service_id = service_raw

    if service_id in (None, "", 0):
        raise RuntimeError("У сделки отсутствует service/service_id.")

    try:
        service_id = int(service_id)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Некорректный service_id в сделке: {service_id}") from exc

    return service_id, service_name or ""


def _extract_amount(deal):
    raw_amount = deal.get("amount")
    if raw_amount in (None, ""):
        return 0
    try:
        return float(raw_amount)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"Некорректная сумма сделки: {raw_amount}") from exc


def _apply_crm_context(invoice, deal, contact):
    service_id, service_name = _extract_service_context(deal)
    invoice.deal_title = deal.get("title", "")
    invoice.contact_id = contact.get("id")
    invoice.contact_name = contact.get("full_name") or f'{contact.get("first_name", "")} {contact.get("last_name", "")}'.strip()
    invoice.contact_email = contact.get("email", "")
    invoice.contact_phone = contact.get("phone", "")
    invoice.service_id = service_id
    invoice.service_name = service_name
    invoice.comment = deal.get("description", "") or deal.get("title", "")
    invoice.amount = _extract_amount(deal)


def _fetch_deal_context(request, deal_id):
    headers = _auth_headers_from_request(request)
    deal_response = requests.get(_contact_service_url(f"/deals/{deal_id}/"), headers=headers, timeout=20)
    if deal_response.status_code != 200:
        raise RuntimeError(f"Не удалось получить сделку: {deal_response.status_code}")
    deal = deal_response.json()
    contact_id = deal.get("contact")
    if not contact_id:
        raise RuntimeError("У сделки отсутствует связанный контакт.")

    contact_response = requests.get(_contact_service_url(f"/contacts/{contact_id}/"), headers=headers, timeout=20)
    if contact_response.status_code != 200:
        raise RuntimeError(f"Не удалось получить контакт: {contact_response.status_code}")
    contact = contact_response.json()
    return deal, contact


def _send_payment_link(invoice):
    if not invoice.contact_email:
        invoice.crm_sync_status = Invoice.SyncStatus.ERROR
        invoice.last_crm_error = "У контакта нет email для отправки ссылки на оплату."
        return False

    send_mail(
        subject=f"Ссылка на оплату счёта №{invoice.invoice_number}",
        message=(
            f"Здравствуйте, {invoice.contact_name or 'клиент'}!\n\n"
            f"Для оплаты счёта №{invoice.invoice_number} перейдите по ссылке:\n{invoice.payment_url}\n\n"
            f"Сумма к оплате: {invoice.amount} RUB."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invoice.contact_email],
        fail_silently=False,
    )
    invoice.crm_sync_status = Invoice.SyncStatus.SYNCED
    invoice.last_crm_error = ""
    invoice.pay_link_sent_at = timezone.now()
    return True


def _mark_invoice_paid_from_payment(invoice, payment_payload):
    """
    Сначала фиксируем оплату в 1С, затем статус счёта в сервисе payments (CRM).
    Если 1С недоступна или вернула ошибку — счёт в CRM не переводим в «Оплачен».
    Возвращает True, если счёт в CRM успешно помечен оплаченным.
    """
    yk_id = (payment_payload.get("id") or "").strip()
    if yk_id:
        invoice.payment_id = yk_id
        invoice.save(update_fields=["payment_id"])

    try:
        register_payment_in_onec(invoice, payment_payload)
    except Exception as exc:
        invoice.mark_retry(error_text=str(exc), onec=True)
        invoice.save()
        return False

    invoice.refresh_from_db()
    return invoice.status == Invoice.Status.PAID


class DealInvoiceView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get(self, request, deal_id):
        invoice = Invoice.objects.filter(deal_id=deal_id).first()
        if not invoice:
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            invoice = retry_due_invoice_sync(invoice)
        except Exception:
            pass
        return Response(InvoiceSerializer(invoice).data)

    def post(self, request, deal_id):
        try:
            deal, contact = _fetch_deal_context(request, deal_id)
            if deal.get("status") != "won":
                return Response(
                    {"detail": "Счёт можно выставить только по успешно закрытой сделке."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            invoice = Invoice.objects.filter(deal_id=deal_id).first()
            created_new = invoice is None
            if invoice:
                previous_sync_key = (
                    invoice.contact_id,
                    invoice.service_id,
                    str(invoice.amount),
                    invoice.contact_email,
                    invoice.contact_phone,
                )
                _apply_crm_context(invoice, deal, contact)
                current_sync_key = (
                    invoice.contact_id,
                    invoice.service_id,
                    str(invoice.amount),
                    invoice.contact_email,
                    invoice.contact_phone,
                )
                # Если данные сделки/контакта поменялись, повторно отправляем счёт в 1С с актуальными полями.
                if previous_sync_key != current_sync_key:
                    invoice.sent_to_1c = False
                    invoice.onec_sync_status = Invoice.SyncStatus.PENDING
                    invoice.onec_document_id = ""
                    invoice.onec_invoice_number = ""
                    invoice.last_onec_error = ""
                invoice.save()
            else:
                invoice = Invoice.objects.create(
                    deal_id=deal["id"],
                    invoice_number=_generate_invoice_number(deal["id"]),
                    amount=0,
                )
                _apply_crm_context(invoice, deal, contact)
                invoice.save()
        except Exception as exc:
            return Response(
                {"detail": f"Не удалось получить данные сделки или контакта: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            invoice.payment_url = _public_payment_url(invoice.id, request=request)
            invoice.save(update_fields=["payment_url"])
            if not invoice.sent_to_1c or invoice.onec_sync_status != Invoice.SyncStatus.SYNCED:
                create_invoice_in_onec(invoice)
            try:
                _send_payment_link(invoice)
            except Exception as mail_exc:
                invoice.crm_sync_status = Invoice.SyncStatus.ERROR
                invoice.last_crm_error = str(mail_exc)
            invoice.save()
            response_status = status.HTTP_201_CREATED if created_new else status.HTTP_200_OK
            return Response(InvoiceSerializer(invoice).data, status=response_status)
        except Exception as exc:
            invoice.mark_retry(error_text=str(exc), onec=True)
            invoice.save()
            return Response(
                {
                    "detail": "Не удалось создать счёт в 1С.",
                    "invoice": InvoiceSerializer(invoice).data,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


class RetryInvoiceSyncView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        try:
            if not invoice.sent_to_1c:
                create_invoice_in_onec(invoice)
                invoice.payment_url = invoice.payment_url or _public_payment_url(invoice.id, request=request)
            else:
                register_payment_in_onec(
                    invoice,
                    {
                        "id": invoice.payment_id,
                        "status": "succeeded",
                        "amount": {"value": str(invoice.amount), "currency": "RUB"},
                        "captured_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                        "payment_method": {"type": "yookassa"},
                    },
                )
            invoice.last_onec_error = ""
            invoice.next_retry_at = None
            if invoice.payment_url and not invoice.pay_link_sent_at:
                _send_payment_link(invoice)
            invoice.save()
            return Response(InvoiceSerializer(invoice).data)
        except Exception as exc:
            invoice.mark_retry(error_text=str(exc), onec=True)
            invoice.save()
            return Response(
                {"detail": "Повторная синхронизация не удалась.", "invoice": InvoiceSerializer(invoice).data},
                status=status.HTTP_502_BAD_GATEWAY,
            )


def create_invoice_and_pay(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    public_base_url = _resolve_public_base_url(request=request)
    if invoice.status == Invoice.Status.PAID:
        return redirect(f"{public_base_url}/payment/result/{invoice.id}/")
    if not invoice.sent_to_1c or invoice.onec_sync_status != Invoice.SyncStatus.SYNCED:
        return HttpResponse(
            """
            <h1>Счет еще не готов к оплате</h1>
            <p>CRM еще не подтвердила создание документа в 1С. Повторите попытку позже.</p>
            """,
            status=409,
        )

    idempotence_key = str(uuid.uuid4())
    payment_payload = {
        "amount": {
            "value": str(invoice.amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{public_base_url}/payment/result/{invoice.id}/"
        },
        "capture": True,
        "description": f"Оплата счёта №{invoice.onec_invoice_number or invoice.invoice_number}",
        "metadata": {
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "deal_id": str(invoice.deal_id),
            "cms_name": "crm_payments_service"
        }
    }

    payment = None
    last_error = None
    for attempt in range(3):
        try:
            payment = Payment.create(payment_payload, idempotence_key)
            break
        except ApiError as exc:
            last_error = exc
            if "502" in str(exc) and attempt < 2:
                time.sleep(1.2 * (attempt + 1))
                continue
            break
        except Exception as exc:
            last_error = exc
            break

    if payment is None:
        invoice.last_crm_error = f"Не удалось создать платёж в YooKassa: {last_error}"
        invoice.crm_sync_status = Invoice.SyncStatus.ERROR
        invoice.save(update_fields=["last_crm_error", "crm_sync_status"])
        return HttpResponse(
            """
            <h1>Платёжный шлюз временно недоступен</h1>
            <p>Не удалось открыть страницу оплаты из-за временной ошибки YooKassa (502).</p>
            <p>Пожалуйста, обновите страницу через 20-30 секунд.</p>
            """,
            status=503,
        )

    invoice.payment_id = payment.id
    invoice.status = Invoice.Status.WAITING
    invoice.save(update_fields=["payment_id", "status"])
    return redirect(payment.confirmation.confirmation_url)


def payment_result(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.status != Invoice.Status.PAID and invoice.payment_id:
        try:
            payment = Payment.find_one(invoice.payment_id)
            if getattr(payment, "status", None) == "succeeded":
                payment_payload = payment.json if hasattr(payment, "json") else {}
                _mark_invoice_paid_from_payment(invoice, payment_payload)
                invoice.refresh_from_db()
        except Exception:
            # Не блокируем UX: если запрос к YooKassa не удался, показываем штатный экран ожидания.
            pass

    if invoice.status == Invoice.Status.PAID:
        return HttpResponse(
            f"""
            <h1>✅ Оплата прошла успешно!</h1>
            <p>Счёт №{invoice.onec_invoice_number or invoice.invoice_number} на сумму {invoice.amount} руб. оплачен.</p>
            <p>Статусы в 1С и CRM обновлены.</p>
            """
        )
    return HttpResponse(
        f"""
        <h1>⏳ Оплата ещё обрабатывается</h1>
        <p>Счёт №{invoice.onec_invoice_number or invoice.invoice_number} создан и ожидает подтверждения.</p>
        <p>Если оплата уже списалась, обновите страницу через несколько секунд.</p>
        """
    )


@csrf_exempt
@require_http_methods(['POST'])
def yookassa_webhook(request):
    try:
        event_json = json.loads(request.body)

        if event_json.get('event') != 'payment.succeeded':
            return JsonResponse({'status': 'ignored'})

        payment_payload = event_json.get('object', {})
        metadata = payment_payload.get('metadata', {})
        invoice_id = metadata.get('invoice_id')
        if not invoice_id:
            return JsonResponse({'status': 'ignored'})

        invoice = Invoice.objects.get(id=invoice_id)
        synced = _mark_invoice_paid_from_payment(invoice, payment_payload)
        invoice.refresh_from_db()
        if not synced:
            logger.warning(
                "YooKassa payment succeeded but invoice sync incomplete: invoice=%s",
                invoice.invoice_number,
            )

        return JsonResponse({'status': 'ok' if synced else 'pending_sync'})
    except Exception as exc:
        logger.exception("YooKassa webhook error")
        return JsonResponse({'error': str(exc)}, status=400)