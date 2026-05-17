
from uuid import uuid4  
from django.db.models import Q
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Applications, ApplicationAudit, MailboxEmail
from .serializers import (
    ApplicationsListSerializer,
    ApplicationAuditSerializer,
    MailboxEmailListSerializer,
    MailboxEmailDetailSerializer,
    SendMailboxEmailSerializer,
)
from .email_parser import YandexMailParser
from .mail_client import YandexMailboxClient


class ApplicationsViewSet(viewsets.ModelViewSet): 
    """
    Минимальный CRUD по заявкам.

    - GET /api/applications/ — список с фильтром по is_processed и поиском по subject/text
      (query-параметры: is_processed=true|false, search=текст)
    - GET /api/applications/{id}/ — детальная заявка
    """

    queryset = Applications.objects.all()
    serializer_class = ApplicationsListSerializer

   
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_processed']
    search_fields = ['subject', 'text']

    def get_queryset(self): 
        queryset = super().get_queryset()

        is_processed = self.request.query_params.get('is_processed')
        if is_processed is not None:
            is_processed = is_processed.lower() == 'true'
            queryset = queryset.filter(is_processed=is_processed)

        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        was_processed = instance.is_processed
        response = super().partial_update(request, *args, **kwargs)
        instance.refresh_from_db()

        if not was_processed and instance.is_processed:
            # actor/action могут приходить либо через headers (старый вариант),
            # либо через body (новый вариант — безопасно для кириллицы в браузере).
            actor = request.headers.get("X-Audit-Actor", "") or (request.data.get("audit_actor", "") if isinstance(request.data, dict) else "")
            action = (request.headers.get("X-Audit-Action", "") or (request.data.get("audit_action", "") if isinstance(request.data, dict) else "") or "").lower()
            if action not in {
                ApplicationAudit.ACTION_APPROVED,
                ApplicationAudit.ACTION_REJECTED,
                ApplicationAudit.ACTION_PROCESSED,
            }:
                action = ApplicationAudit.ACTION_PROCESSED
            ApplicationAudit.objects.create(
                application=instance,
                actor=actor,
                action=action,
                metadata={"source": "applications_api"},
            )
        return response

    @action(detail=False, methods=["get"])
    def audit_trail(self, request):
        queryset = ApplicationAudit.objects.select_related("application").all()[:200]
        serializer = ApplicationAuditSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def fetch_from_mail(self, request):
        """
        Забрать все письма из Яндекс.Почты и сохранить как заявки.
        POST /api/applications/fetch_from_mail/
        """
        from django.conf import settings

        parser = YandexMailParser(
            settings.YANDEX_EMAIL,
            settings.YANDEX_PASSWORD,
            imap_host=getattr(settings, 'YANDEX_IMAP_HOST', 'imap.yandex.ru'),
            target_sender=getattr(settings, 'YANDEX_TARGET_SENDER', None),
        )
        result = parser.parse_and_save()
        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class MailboxEmailListView(generics.ListAPIView):
    serializer_class = MailboxEmailListSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ["subject", "sender_email", "sender_name", "recipients", "body_text", "preview"]

    def get_queryset(self):
        queryset = MailboxEmail.objects.all()
        folder = (self.request.query_params.get("folder") or MailboxEmail.FOLDER_ALL).lower()
        if folder == MailboxEmail.FOLDER_INBOX:
            queryset = queryset.filter(in_inbox=True, in_trash=False)
        elif folder == MailboxEmail.FOLDER_SENT:
            queryset = queryset.filter(in_sent=True)
        elif folder == MailboxEmail.FOLDER_IMPORTANT:
            queryset = queryset.filter(is_important=True, in_trash=False)
        elif folder == MailboxEmail.FOLDER_TRASH:        
            queryset = queryset.filter(in_trash=True)

        search = (self.request.query_params.get("search") or "").strip() #/mail/?search=
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search)
                | Q(sender_email__icontains=search)
                | Q(sender_name__icontains=search)
                | Q(recipients__icontains=search)
                | Q(body_text__icontains=search)
            )
        return queryset.order_by("-date", "-id")


class MailboxEmailDetailView(generics.RetrieveAPIView):
    queryset = MailboxEmail.objects.all()
    serializer_class = MailboxEmailDetailSerializer


class MailboxFoldersView(APIView):
    def get(self, request):
        return Response(
            {
                "all": MailboxEmail.objects.count(),
                "inbox": MailboxEmail.objects.filter(in_inbox=True, in_trash=False).count(),
                "sent": MailboxEmail.objects.filter(in_sent=True).count(),
                "important": MailboxEmail.objects.filter(is_important=True, in_trash=False).count(),
                "trash": MailboxEmail.objects.filter(in_trash=True).count(),
            }
        )


class MailboxSyncView(APIView):
    def post(self, request):
        from django.conf import settings

        client = YandexMailboxClient(
            settings.YANDEX_EMAIL,
            settings.YANDEX_PASSWORD,
            imap_host=getattr(settings, "YANDEX_IMAP_HOST", "imap.yandex.ru"),
            smtp_host=getattr(settings, "YANDEX_SMTP_HOST", "smtp.yandex.ru"),
            smtp_port=getattr(settings, "YANDEX_SMTP_PORT", 465),
            smtp_use_ssl=getattr(settings, "YANDEX_SMTP_USE_SSL", True),
        )
        result = client.sync_mailbox()
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class MailboxSendView(APIView):
    def post(self, request):
        from django.conf import settings 

        serializer = SendMailboxEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = YandexMailboxClient(
            settings.YANDEX_EMAIL,
            settings.YANDEX_PASSWORD,
            imap_host=getattr(settings, "YANDEX_IMAP_HOST", "imap.yandex.ru"),
            smtp_host=getattr(settings, "YANDEX_SMTP_HOST", "smtp.yandex.ru"),
            smtp_port=getattr(settings, "YANDEX_SMTP_PORT", 465),
            smtp_use_ssl=getattr(settings, "YANDEX_SMTP_USE_SSL", True),
        )

        payload = serializer.validated_data
        #  
        try:
            result = client.send_email(
                to=payload["to"],
                subject=payload["subject"],
                body=payload["body"],
                cc=payload.get("cc", ""),
            )
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        # {
        #     "to": "user@example.com",
        #     "subject": "Встреча",
        #     "body": "Привет, давай встретимся завтра",
        #     "cc": "boss@example.com"
        # }
        # И сохраняем отправленное письмо в БД для отображения в списке
        item = MailboxEmail.objects.create(
            external_id=f"sent-{uuid4().hex}", #уникальный id
            subject=result["subject"],
            sender_email=settings.YANDEX_EMAIL,
            recipients=result["recipients"],
            cc=result["cc"],
            body_text=result["body_text"],
            preview=(result["body_text"] or "")[:180],
            is_read=True,
            in_sent=True,
            primary_folder=MailboxEmail.FOLDER_SENT,
        )
        return Response(MailboxEmailDetailSerializer(item).data, status=status.HTTP_201_CREATED)