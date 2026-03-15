from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Applications
from .serializers import ApplicationsListSerializer
from .email_parser import YandexMailParser


class ApplicationsViewSet(viewsets.ModelViewSet):
    """
    Минимальный CRUD по заявкам.

    - GET /api/applications/ — список с фильтром по is_processed и поиском по subject/text
      (query-параметры: is_processed=true|false, search=текст)
    - GET /api/applications/{id}/ — детальная заявка
    """

    queryset = Applications.objects.all()
    serializer_class = ApplicationsListSerializer

    # Фильтры и поиск (из ТЗ)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_processed']
    search_fields = ['subject', 'text']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Дополнительный удобный фильтр по статусу через is_processed=true|false
        is_processed = self.request.query_params.get('is_processed')
        if is_processed is not None:
            is_processed = is_processed.lower() == 'true'
            queryset = queryset.filter(is_processed=is_processed)

        return queryset

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