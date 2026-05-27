import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text
from django.utils import timezone

from .models import CampaignRecipient
from .template_vars import build_recipient_variables, content_is_html, render_placeholders

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP Yandex: отправка письма и подстановка {переменных} в шаблон."""

    def __init__(self):
        self.smtp_server = "smtp.yandex.ru"
        self.smtp_port = 465
        self.smtp_username = "ehsonboboev7@yandex.ru"
        self.smtp_password = "hbewwdgiloviutid"

    def send_email(self, to_email, subject, content, is_html=False):
        try:
            if is_html:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(content, "html", "utf-8"))
                msg.attach(MIMEText(self._strip_html(content), "plain", "utf-8"))
            else:
                msg = MIMEText(content, "plain", "utf-8")

            msg["Subject"] = subject
            msg["From"] = self.smtp_username
            msg["To"] = to_email

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            return True
        except smtplib.SMTPException as exc:
            logger.error("SMTP: %s", exc)
            return False

    @staticmethod
    def _strip_html(html_content):
        return html2text.html2text(html_content or "").strip()

    def send_template_email(self, to_email, template, variables=None):
        variables = variables or {}
        content = render_placeholders(template.content, variables)
        subject = render_placeholders(template.subject, variables)
        is_html = template.template_type == "email" and content_is_html(content)
        return self.send_email(to_email, subject, content, is_html=is_html)


class MarketingService:
    def __init__(self):
        self.email_service = EmailService()

    def send_to_recipient(
        self, campaign, recipient_id, client_info=None, template_variables=None
    ):
        """Одно письмо одному контакту + запись CampaignRecipient."""
        try:
            recipient, _ = CampaignRecipient.objects.get_or_create(
                campaign=campaign,
                recipient_id=recipient_id,
                defaults={
                    "recipient_email": (client_info or {}).get("email", ""),
                    "recipient_phone": (client_info or {}).get("phone", ""),
                },
            )

            if template_variables is not None:
                variables = template_variables
            else:
                variables = build_recipient_variables(
                    client_info,
                    {},
                    recipient_id,
                    campaign.manager_id,
                    campaign.name,
                )

            success = False
            error_msg = ""

            if campaign.template.template_type == "email":
                if not recipient.recipient_email and client_info:
                    recipient.recipient_email = client_info.get("email", "")
                    recipient.save()

                if recipient.recipient_email:
                    success = self.email_service.send_template_email(
                        recipient.recipient_email,
                        campaign.template,
                        variables,
                    )
                    if not success:
                        error_msg = "Ошибка отправки email"
                else:
                    error_msg = "Email получателя отсутствует"

            if success:
                recipient.status = "sent"
                recipient.sent_at = timezone.now()
                recipient.error_message = ""
            else:
                recipient.status = "failed"
                recipient.error_message = error_msg or "Ошибка отправки"
            recipient.save()
            return success, error_msg

        except Exception as exc:
            logger.exception("Recipient %s: %s", recipient_id, exc)
            return False, str(exc)

    def _finalize_bulk(self, campaign, recipient_ids, success_count, failed_count, errors):
        campaign.success_count = success_count
        campaign.failed_count = failed_count
        campaign.recipient_count = len(recipient_ids)
        if success_count > 0:
            campaign.status = "sent"
            campaign.sent_at = timezone.now()
        else:
            campaign.status = "failed"
        campaign.save()
        return {
            "total": len(recipient_ids),
            "success": success_count,
            "failed": failed_count,
            "errors": errors,
        }

    def _send_bulk(self, campaign, recipient_ids, client_info_map, extra_variables=None):
        """Цикл по получателям: для каждого — send_to_recipient."""
        success_count = failed_count = 0
        errors = []
        client_info_map = client_info_map or {}

        for recipient_id in recipient_ids:
            client_info = client_info_map.get(recipient_id)
            variables = build_recipient_variables(
                client_info,
                extra_variables,
                recipient_id,
                campaign.manager_id,
                campaign.name,
            )
            variables.setdefault("campaign_name", campaign.name)

            success, error_msg = self.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_id,
                client_info=client_info,
                template_variables=variables,
            )
            if success:
                success_count += 1
            else:
                failed_count += 1
                errors.append({"recipient_id": recipient_id, "error": error_msg})

        return self._finalize_bulk(
            campaign, recipient_ids, success_count, failed_count, errors
        )

    def send_campaign(
        self, campaign, recipient_ids, client_info_map=None, template_variables=None
    ):
        return self._send_bulk(
            campaign, recipient_ids, client_info_map, template_variables
        )

    def send_quick_message_campaign(self, campaign, recipient_ids, client_info_map=None):
        return self._send_bulk(campaign, recipient_ids, client_info_map, None)
