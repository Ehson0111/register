"""Общая логика кампаний: переменные шаблона, статистика, фоновая отправка."""

import logging
import threading
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from .models import Campaign
from .template_vars import build_recipient_variables

logger = logging.getLogger(__name__)


def aggregate_campaign_stats(queryset) -> dict:
    """Агрегаты для экрана маркетинга (ORM вместо циклов по queryset)."""
    last_30_days = timezone.now() - timedelta(days=30)
    recent = queryset.filter(created_at__gte=last_30_days)

    totals = queryset.aggregate(
        total_campaigns=Count("id"),
        total_recipients=Sum("recipient_count"),
        total_sent=Sum("success_count"),
    )
    recent_totals = recent.aggregate(
        recent_campaigns=Count("id"),
        recent_recipients=Sum("recipient_count"),
        recent_sent=Sum("success_count"),
    )

    def _zero(d, keys):
        return {k: d.get(k) or 0 for k in keys}

    return {
        **_zero(totals, ("total_campaigns", "total_recipients", "total_sent")),
        **_zero(recent_totals, ("recent_campaigns", "recent_recipients", "recent_sent")),
        "by_type": {
            "individual": queryset.filter(campaign_type="individual").count(),
            "bulk": queryset.filter(campaign_type="bulk").count(),
        },
        "by_status": {
            status: queryset.filter(status=status).count()
            for status in ("draft", "sent", "sending", "failed")
        },
    }


def _run_async(target, *args) -> None:
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()


def send_campaign_async(
    campaign_id,
    recipient_ids,
    client_info_map=None,
    template_variables=None,
) -> None:
    """Массовая рассылка в фоне — HTTP-ответ уже отдан клиенту."""
    from .services import MarketingService

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        result = MarketingService().send_campaign(
            campaign,
            recipient_ids,
            client_info_map,
            template_variables=template_variables,
        )
        logger.info(
            "Campaign %s: %s ok, %s failed",
            campaign_id,
            result["success"],
            result["failed"],
        )
    except Exception:
        logger.exception("Async campaign %s failed", campaign_id)


def send_quick_message_async(campaign_id, recipient_ids, client_info_map=None) -> None:
    from .services import MarketingService

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        result = MarketingService().send_quick_message_campaign(
            campaign, recipient_ids, client_info_map
        )
        logger.info(
            "Quick campaign %s: %s ok, %s failed",
            campaign_id,
            result["success"],
            result["failed"],
        )
    except Exception:
        logger.exception("Async quick campaign %s failed", campaign_id)


def dispatch_campaign_send(
    *,
    campaign,
    recipient_ids,
    client_info_map,
    template_variables=None,
    quick=False,
):
    """
    >1 получателя — поток с SMTP-отправкой;
    один получатель — сразу в этом запросе.
    """
    if len(recipient_ids) > 1:
        runner = send_quick_message_async if quick else send_campaign_async
        args = (campaign.id, recipient_ids, client_info_map)
        if not quick:
            args = (campaign.id, recipient_ids, client_info_map, template_variables)
        _run_async(runner, *args)
        return "async"

    from .services import MarketingService

    service = MarketingService()
    rid = recipient_ids[0]
    client_info = (client_info_map or {}).get(rid)
    if quick:
        variables = {
            "client_id": rid,
            "name": (client_info or {}).get("name", f"Клиент #{rid}"),
            "client_name": (client_info or {}).get("name", f"Клиент #{rid}"),
            "date": timezone.now().strftime("%d.%m.%Y"),
            "manager_id": campaign.manager_id,
        }
    else:
        variables = build_recipient_variables(
            client_info,
            template_variables,
            rid,
            campaign.manager_id,
            campaign.name,
        )

    success, error_msg = service.send_to_recipient(
        campaign=campaign,
        recipient_id=rid,
        client_info=client_info,
        template_variables=variables,
    )
    if success:
        campaign.status = "sent"
        campaign.sent_at = timezone.now()
        campaign.success_count = 1
    else:
        campaign.status = "failed"
        campaign.failed_count = 1
    campaign.save()
    return success, error_msg, variables if not quick else None
