from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .campaign_helpers import aggregate_campaign_stats, dispatch_campaign_send
from .contact_gateway import fetch_contacts_map
from .models import Campaign, Template
from .serializers import (
    CampaignSerializer,
    QuickMessageSerializer,
    SendCampaignSerializer,
    TemplateSerializer,
)

# Эндпоинты, которые вызывает frontend/vue-project (marketingService.ts):
# GET  templates/, campaigns/, campaigns/stats/
# POST send-campaign/, send-quick-message/


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """Список шаблонов менеджера (только чтение — UI не создаёт шаблоны через API)."""

    permission_classes = [IsAuthenticated]
    serializer_class = TemplateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    
    
    # filter_backends — какие механизмы фильтрации использовать

    search_fields = ["name", "description", "subject"]
    #Позволяет делать запрос GET /templates/?search=договор
    filterset_fields = ["template_type", "is_active"]

    def get_queryset(self):
        return Template.objects.filter(manager_id=self.request.user.id)


class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """История рассылок и агрегированная статистика."""

    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["name", "subject"]
    filterset_fields = ["campaign_type", "status"]
    ordering_fields = ["sent_at", "created_at", "success_count"]
    ordering = ["-sent_at", "-created_at"]

    def get_queryset(self):
        return Campaign.objects.filter(manager_id=self.request.user.id)

    @action(detail=False, methods=["GET"])
    def stats(self, request):
        return Response(aggregate_campaign_stats(self.get_queryset()))


class SendCampaignView(APIView):
    """POST: рассылка по шаблону (один или много получателей)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendCampaignSerializer(data=request.data)  
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user

        try:
            template = Template.objects.get(
                id=data["template_id"], manager_id=user.id
            )
        except Template.DoesNotExist:
            return Response({"error": "Шаблон не найден"}, status=status.HTTP_404_NOT_FOUND)

        recipient_ids = data.get("recipient_ids") or []
        if data.get("send_to_all"):
            recipient_ids = recipient_ids or []
        if not recipient_ids:
            return Response(
                {"error": "Нет получателей для отправки"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign_name = data.get(
            "campaign_name",
            f"Рассылка от {timezone.now().strftime('%d.%m.%Y %H:%M')}",
        )
        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type="bulk" if len(recipient_ids) > 1 else "individual",
            status="sending",
            template=template,
            subject=data.get("subject") or template.subject,
            content=data.get("content") or template.content,
            recipients=recipient_ids,
            recipient_count=len(recipient_ids),
            manager_id=user.id,
        )

        # Контакты из contact-service (email для SMTP)
        client_info_map = fetch_contacts_map(request, recipient_ids)
        common_variables = {
            **data.get("variables", {}),
            "manager_id": user.id,
            "date": timezone.now().strftime("%d.%m.%Y"),
            "company": campaign_name,
        }

        result = dispatch_campaign_send(
            campaign=campaign,
            recipient_ids=recipient_ids,
            client_info_map=client_info_map,
            template_variables=common_variables,
            quick=False,
        )

        if result == "async":
            return Response(
                {
                    "success": True,
                    "message": f"Рассылка запущена для {len(recipient_ids)} получателей",
                    "campaign_id": campaign.id,
                    "status": "sending",
                    "common_variables": common_variables,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        success, error_msg, variables_used = result
        if success:
            return Response(
                {
                    "success": True,
                    "message": "Сообщение отправлено успешно",
                    "campaign_id": campaign.id,
                    "variables_used": variables_used,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": error_msg,
                "campaign_id": campaign.id,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class QuickMessageView(APIView):
    """POST: быстрое письмо без готового шаблона (создаётся временный Template)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuickMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = request.user

        recipient_ids = data["recipient_ids"]
        campaign_name = data.get(
            "campaign_name",
            f"Быстрая рассылка от {timezone.now().strftime('%d.%m.%Y %H:%M')}",
        )

        temp_template = Template.objects.create(
            name=f"Быстрый шаблон - {timezone.now().strftime('%H:%M:%S')}",
            template_type=data.get("message_type", "email"),
            subject=data.get("subject", "Сообщение от менеджера"),
            content=data["message"],
            manager_id=user.id,
            is_active=False,
        )

        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type="bulk" if len(recipient_ids) > 1 else "individual",
            status="sending",
            template=temp_template,
            subject=temp_template.subject,
            content=temp_template.content,
            recipients=recipient_ids,
            recipient_count=len(recipient_ids),
            manager_id=user.id,
        )

        client_info_map = fetch_contacts_map(request, recipient_ids)
        result = dispatch_campaign_send(
            campaign=campaign,
            recipient_ids=recipient_ids,
            client_info_map=client_info_map,
            quick=True,
        )

        if result == "async":
            return Response(
                {
                    "success": True,
                    "message": f"Быстрая рассылка запущена для {len(recipient_ids)} получателей",
                    "campaign_id": campaign.id,
                    "status": "sending",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        success, error_msg, _ = result
        if success:
            return Response(
                {
                    "success": True,
                    "message": "Быстрое сообщение отправлено успешно",
                    "campaign_id": campaign.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": error_msg,
                "campaign_id": campaign.id,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
