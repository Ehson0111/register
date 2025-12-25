# services/marketing/apps/marketing/views.py
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Template, Campaign, CampaignRecipient
from .serializers import (
    TemplateSerializer, CampaignSerializer,
    SendCampaignSerializer, IndividualSendSerializer
)

import logging
logger = logging.getLogger(__name__)


class TemplateViewSet(viewsets.ModelViewSet):
    """ViewSet для шаблонов"""
    permission_classes = [IsAuthenticated]
    serializer_class = TemplateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'subject']
    filterset_fields = ['template_type', 'is_active']
    
    def get_queryset(self):
        """Только шаблоны текущего пользователя"""
        user = self.request.user
        return Template.objects.filter(manager_id=user.id)
    
    @action(detail=False, methods=['GET'])
    def by_type(self, request):
        """Получить шаблоны по типу"""
        template_type = request.query_params.get('type', 'email')
        
        templates = self.get_queryset().filter(
            template_type=template_type,
            is_active=True
        )
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def duplicate(self, request, pk=None):
        """Дублировать шаблон"""
        template = self.get_object()
        
        # Создаем копию
        new_template = Template.objects.create(
            name=f"{template.name} (Копия)",
            template_type=template.template_type,
            subject=template.subject,
            content=template.content,
            sms_content=template.sms_content,
            variables=template.variables,
            description=template.description,
            manager_id=request.user.id,
            is_active=True
        )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet для истории рассылок"""
    permission_classes = [IsAuthenticated]
    serializer_class = CampaignSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'subject']
    filterset_fields = ['campaign_type', 'status']
    ordering_fields = ['sent_at', 'created_at', 'success_count']
    ordering = ['-sent_at', '-created_at']
    
    def get_queryset(self):
        """Только кампании текущего пользователя"""
        user = self.request.user
        return Campaign.objects.filter(manager_id=user.id)
    
    @action(detail=True, methods=['GET'])
    def recipients(self, request, pk=None):
        """Получить детальную информацию о получателях"""
        campaign = self.get_object()
        
        # Получаем получателей с пагинацией
        recipients = campaign.campaign_recipients.all()
        
        from .serializers import CampaignRecipientSerializer
        serializer = CampaignRecipientSerializer(recipients, many=True)
        
        # Статистика по статусам
        status_stats = {}
        for status_code, status_name in CampaignRecipient.STATUS_CHOICES:
            count = recipients.filter(status=status_code).count()
            if count > 0:
                status_stats[status_code] = {
                    'name': status_name,
                    'count': count,
                    'percentage': round((count / recipients.count()) * 100, 2)
                }
        
        return Response({
            'campaign': campaign.name,
            'total_recipients': recipients.count(),
            'status_stats': status_stats,
            'recipients': serializer.data
        })
    
    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Статистика по всем кампаниям"""
        user = request.user
        
        # Все кампании пользователя
        campaigns = self.get_queryset()
        
        # Кампании за последние 30 дней
        last_30_days = timezone.now() - timedelta(days=30)
        recent_campaigns = campaigns.filter(created_at__gte=last_30_days)
        
        stats = {
            'total_campaigns': campaigns.count(),
            'total_recipients': sum(c.recipient_count for c in campaigns),
            'total_sent': sum(c.success_count for c in campaigns),
            
            'recent_campaigns': recent_campaigns.count(),
            'recent_recipients': sum(c.recipient_count for c in recent_campaigns),
            'recent_sent': sum(c.success_count for c in recent_campaigns),
            
            'by_type': {
                'individual': campaigns.filter(campaign_type='individual').count(),
                'bulk': campaigns.filter(campaign_type='bulk').count(),
            },
            
            'by_status': {
                'draft': campaigns.filter(status='draft').count(),
                'sent': campaigns.filter(status='sent').count(),
                'sending': campaigns.filter(status='sending').count(),
                'failed': campaigns.filter(status='failed').count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['GET'])
    def recent(self, request):
        """Последние 10 кампаний"""
        campaigns = self.get_queryset().filter(
            status='sent'
        ).order_by('-sent_at')[:10]
        
        serializer = self.get_serializer(campaigns, many=True)
        return Response(serializer.data)


class SendCampaignView(APIView):
    """Отправка рассылки (индивидуальной или массовой)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SendCampaignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user = request.user
        
        # Получаем шаблон
        try:
            template = Template.objects.get(
                id=data['template_id'],
                manager_id=user.id
            )
        except Template.DoesNotExist:
            return Response(
                {'error': 'Шаблон не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Определяем получателей
        recipient_ids = data.get('recipient_ids', [])
        
        # Если выбрано "отправить всем", нужно получить список всех клиентов
        if data.get('send_to_all'):
            # Здесь нужно интегрироваться с сервисом контактов
            # Пока используем пустой список
            recipient_ids = []  # Заглушка
        
        # Проверяем, есть ли получатели
        if not recipient_ids:
            return Response(
                {'error': 'Нет получателей для отправки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем кампанию
        campaign_name = data.get('campaign_name', f'Рассылка от {timezone.now().strftime("%d.%m.%Y %H:%M")}')
        
        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type='bulk' if len(recipient_ids) > 1 else 'individual',
            status='sending',
            template=template,
            subject=data.get('subject', template.subject),
            content=data.get('content', template.content),
            recipients=recipient_ids,
            recipient_count=len(recipient_ids),
            manager_id=user.id
        )
        
        # Создаем записи для каждого получателя
        for recipient_id in recipient_ids:
            CampaignRecipient.objects.create(
                campaign=campaign,
                recipient_id=recipient_id,
                status='pending'
            )
        
        # Здесь должна быть реальная логика отправки
        # Пока просто имитируем успешную отправку
        self._simulate_sending(campaign)
        
        # Обновляем статус кампании
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.success_count = len(recipient_ids)
        campaign.save()
        
        # Возвращаем результат
        campaign_serializer = CampaignSerializer(campaign)
        return Response({
            'success': True,
            'message': f'Рассылка отправлена {len(recipient_ids)} получателям',
            'campaign': campaign_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def _simulate_sending(self, campaign):
        """Имитация отправки (заглушка)"""
        # В реальности здесь должна быть интеграция с email/SMS сервисами
        for recipient in campaign.campaign_recipients.all():
            recipient.status = 'sent'
            recipient.sent_at = timezone.now()
            recipient.save()
            
            # Имитация случайных открытий
            import random
            if random.random() > 0.3:  # 70% шанс открытия
                recipient.status = 'opened'
                recipient.opened_at = timezone.now() + timedelta(minutes=random.randint(1, 60))
                recipient.save()


class IndividualSendView(APIView):
    """Индивидуальная отправка одному клиенту"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = IndividualSendSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user = request.user
        
        # Получаем шаблон
        try:
            template = Template.objects.get(
                id=data['template_id'],
                manager_id=user.id
            )
        except Template.DoesNotExist:
            return Response(
                {'error': 'Шаблон не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Создаем кампанию для одного получателя
        recipient_id = data['recipient_id']
        
        campaign = Campaign.objects.create(
            name=f"Индивидуальная рассылка клиенту #{recipient_id}",
            campaign_type='individual',
            status='sent',
            template=template,
            subject=template.subject,
            content=template.content,
            recipients=[recipient_id],
            recipient_count=1,
            success_count=1,
            sent_at=timezone.now(),
            manager_id=user.id
        )
        
        # Создаем запись о получателе
        recipient = CampaignRecipient.objects.create(
            campaign=campaign,
            recipient_id=recipient_id,
            status='sent',
            sent_at=timezone.now()
        )
        
        # Здесь должна быть реальная логика отправки
        # Пока просто логируем
        logger.info(f"Индивидуальная отправка: менеджер {user.id} -> клиент {recipient_id}, шаблон {template.name}")
        
        # Получаем данные клиента из сервиса контактов (заглушка)
        client_info = self._get_client_info(recipient_id, user.id)
        
        return Response({
            'success': True,
            'message': f'Сообщение отправлено клиенту #{recipient_id}',
            'campaign_id': campaign.id,
            'recipient': {
                'id': recipient_id,
                'info': client_info
            },
            'template': TemplateSerializer(template).data
        }, status=status.HTTP_201_CREATED)
    
    def _get_client_info(self, client_id, manager_id):
        """Получить информацию о клиенте (заглушка)"""
        # В реальности нужно делать запрос к сервису контактов
        return {
            'id': client_id,
            'name': f'Клиент #{client_id}',
            'email': f'client{client_id}@example.com',
            'phone': '+7999000' + str(client_id).zfill(4)
        }


class CampaignHistoryView(APIView):
    """История рассылок с фильтрами"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Параметры фильтрации
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        campaign_type = request.query_params.get('type')
        status = request.query_params.get('status')
        
        # Базовый запрос
        campaigns = Campaign.objects.filter(manager_id=user.id)
        
        # Применяем фильтры
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                campaigns = campaigns.filter(created_at__gte=start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                campaigns = campaigns.filter(created_at__lte=end)
            except ValueError:
                pass
        
        if campaign_type:
            campaigns = campaigns.filter(campaign_type=campaign_type)
        
        if status:
            campaigns = campaigns.filter(status=status)
        
        # Пагинация
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        
        total_count = campaigns.count()
        campaigns = campaigns[(page-1)*page_size : page*page_size]
        
        serializer = CampaignSerializer(campaigns, many=True)
        
        return Response({
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': serializer.data
        })