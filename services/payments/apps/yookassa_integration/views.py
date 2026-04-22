import json
import uuid

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from yookassa import Configuration, Payment

from .invoice_sync import create_invoice_in_onec, register_payment_in_onec, retry_due_invoice_sync
from .models import Invoice
from .permissions import IsManagerOrAdmin
from .serializers import InvoiceSerializer

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


def _public_payment_url(invoice_id):
    base = settings.PUBLIC_PAYMENTS_BASE_URL.rstrip("/")
    return f"{base}/payment/pay/{invoice_id}/"


def _generate_invoice_number(deal_id):
    return f"СЧЕТ-{deal_id:06d}"


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
            existing = Invoice.objects.filter(deal_id=deal_id).first()
            if existing:
                return Response(InvoiceSerializer(existing).data, status=status.HTTP_200_OK)

            deal, contact = _fetch_deal_context(request, deal_id)
            if deal.get("status") != "won":
                return Response(
                    {"detail": "Счёт можно выставить только по успешно закрытой сделке."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            invoice = Invoice.objects.create(
                deal_id=deal["id"],
                deal_title=deal.get("title", ""),
                contact_id=contact.get("id"),
                contact_name=contact.get("full_name") or f'{contact.get("first_name", "")} {contact.get("last_name", "")}'.strip(),
                contact_email=contact.get("email", ""),
                contact_phone=contact.get("phone", ""),
                service_id=deal.get("service"),
                service_name=deal.get("service_name", ""),
                comment=deal.get("description", "") or deal.get("title", ""),
                invoice_number=_generate_invoice_number(deal["id"]),
                amount=deal.get("amount") or 0,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Не удалось получить данные сделки или контакта: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            invoice.payment_url = _public_payment_url(invoice.id)
            invoice.save(update_fields=["payment_url"])
            create_invoice_in_onec(invoice)
            try:
                _send_payment_link(invoice)
            except Exception as mail_exc:
                invoice.crm_sync_status = Invoice.SyncStatus.ERROR
                invoice.last_crm_error = str(mail_exc)
            invoice.save()
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
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
                invoice.payment_url = invoice.payment_url or _public_payment_url(invoice.id)
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
    if invoice.status == Invoice.Status.PAID:
        return redirect(f"{settings.PUBLIC_PAYMENTS_BASE_URL.rstrip('/')}/payment/result/{invoice.id}/")
    if not invoice.sent_to_1c or invoice.onec_sync_status != Invoice.SyncStatus.SYNCED:
        return HttpResponse(
            """
            <h1>Счет еще не готов к оплате</h1>
            <p>CRM еще не подтвердила создание документа в 1С. Повторите попытку позже.</p>
            """,
            status=409,
        )

    idempotence_key = str(uuid.uuid4())
    payment = Payment.create(
        {
            "amount": {
                "value": str(invoice.amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{settings.PUBLIC_PAYMENTS_BASE_URL.rstrip('/')}/payment/result/{invoice.id}/"
            },
            "capture": True,
            "description": f"Оплата счёта №{invoice.onec_invoice_number or invoice.invoice_number}",
            "metadata": {
                "invoice_id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "deal_id": str(invoice.deal_id),
                "cms_name": "crm_payments_service"
            }
        },
        idempotence_key
    )

    invoice.payment_id = payment.id
    invoice.status = Invoice.Status.WAITING
    invoice.save(update_fields=["payment_id", "status"])
    return redirect(payment.confirmation.confirmation_url)


def payment_result(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
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
        print(f"📩 Получено уведомление: {event_json}")

        if event_json.get('event') != 'payment.succeeded':
            return JsonResponse({'status': 'ignored'})

        payment_payload = event_json.get('object', {})
        metadata = payment_payload.get('metadata', {})
        invoice_id = metadata.get('invoice_id')
        if not invoice_id:
            return JsonResponse({'status': 'ignored'})

        invoice = Invoice.objects.get(id=invoice_id)
        invoice.payment_id = payment_payload.get('id') or invoice.payment_id
        captured_at = payment_payload.get('captured_at')
        parsed_paid_at = parse_datetime(captured_at) if captured_at else None
        invoice.paid_at = parsed_paid_at or timezone.now()

        try:
            register_payment_in_onec(invoice, payment_payload)
            print(f"✅ Счёт №{invoice.invoice_number} оплачен и синхронизирован с 1С")
        except Exception as exc:
            invoice.mark_retry(error_text=str(exc), onec=True)
            invoice.save()
            print(f"⚠️ Ошибка отправки в 1С: {exc}")

        return JsonResponse({'status': 'ok'})
    except Exception as exc:
        print(f"❌ Ошибка: {exc}")
        return JsonResponse({'error': str(exc)}, status=400)