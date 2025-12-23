from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import EmailCampaign, EmailTemplate, ContactSegment, CampaignStatistic
from .serializers import (
    EmailCampaignSerializer,
    EmailCampaignCreateSerializer,
    EmailTemplateSerializer,
    ContactSegmentSerializer,
    CampaignStatisticSerializer,
    MarketingOverviewSerializer,
    CampaignPerformanceSerializer
)
import logging

logger = logging.getLogger(__name__)


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet для email рассылок"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EmailCampaignCreateSerializer
        return EmailCampaignSerializer
    
    def get_queryset(self):
        """Только кампании текущего пользователя"""
        user = self.request.user
        queryset = EmailCampaign.objects.filter(created_by=user)
        
        # Фильтры
        status = self.request.query_params.get('status')
        campaign_type = self.request.query_params.get('type')
        search = self.request.query_params.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(subject__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Автоматически назначаем создателя"""
        serializer.save(created_by=self.request.user)
        logger.info(f"Campaign created: {serializer.instance.name} by {self.request.user.email}")
    
    @action(detail=False, methods=['GET'])
    def active(self, request):
        """Активные рассылки"""
        queryset = self.get_queryset().filter(
            status__in=[EmailCampaign.STATUS_SCHEDULED, EmailCampaign.STATUS_SENDING]
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def schedule(self, request, pk=None):
        """Запланировать рассылку"""
        campaign = self.get_object()
        
        scheduled_for = request.data.get('scheduled_for')
        if not scheduled_for:
            return Response(
                {'error': 'Требуется дата и время планирования'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            scheduled_date = datetime.fromisoformat(scheduled_for)
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = EmailCampaign.STATUS_SCHEDULED
        campaign.scheduled_for = scheduled_date
        campaign.save()
        
        logger.info(f"Campaign scheduled: {campaign.name} for {scheduled_date}")
        
        return Response(self.get_serializer(campaign).data)
    
    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk=None):
        """Отменить рассылку"""
        campaign = self.get_object()
        
        if campaign.status not in [EmailCampaign.STATUS_SCHEDULED, EmailCampaign.STATUS_SENDING]:
            return Response(
                {'error': 'Можно отменить только запланированные или отправляющиеся рассылки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.status = EmailCampaign.STATUS_CANCELLED
        campaign.save()
        
        logger.info(f"Campaign cancelled: {campaign.name}")
        
        return Response(self.get_serializer(campaign).data)
    
    @action(detail=True, methods=['GET'])
    def statistics(self, request, pk=None):
        """Статистика по кампании"""
        campaign = self.get_object()
        stats = campaign.daily_stats.all().order_by('date')[:30]
        serializer = CampaignStatisticSerializer(stats, many=True)
        
        return Response({
            'campaign': self.get_serializer(campaign).data,
            'statistics': serializer.data
        })


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet для шаблонов email"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Только шаблоны текущего пользователя"""
        user = self.request.user
        queryset = EmailTemplate.objects.filter(created_by=user)
        
        # Фильтры
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Автоматически назначаем создателя"""
        serializer.save(created_by=self.request.user)
        logger.info(f"Template created: {serializer.instance.name} by {self.request.user.email}")


class ContactSegmentViewSet(viewsets.ModelViewSet):
    """ViewSet для сегментов контактов"""
    serializer_class = ContactSegmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Только сегменты текущего пользователя"""
        user = self.request.user
        return ContactSegment.objects.filter(created_by=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Автоматически назначаем создателя"""
        serializer.save(created_by=self.request.user)
        logger.info(f"Segment created: {serializer.instance.name} by {self.request.user.email}")
    
    @action(detail=True, methods=['POST'])
    def calculate(self, request, pk=None):
        """Пересчитать количество контактов в сегменте"""
        segment = self.get_object()
        
        # Здесь будет запрос к contact-service для подсчета контактов
        # Пока используем заглушку
        contact_count = 500  # Заглушка
        
        segment.contact_count = contact_count
        segment.last_calculated_at = timezone.now()
        segment.save()
        
        return Response({
            'message': f'Сегмент пересчитан: {contact_count} контактов',
            'contact_count': contact_count
        })


class MarketingAnalyticsView(generics.GenericAPIView):
    """Аналитика маркетинга"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Общая статистика маркетинга"""
        user = request.user
        
        # Статистика кампаний
        campaigns = EmailCampaign.objects.filter(created_by=user)
        total_campaigns = campaigns.count()
        active_campaigns = campaigns.filter(
            status__in=[EmailCampaign.STATUS_SCHEDULED, EmailCampaign.STATUS_SENDING]
        ).count()
        
        # Суммарная статистика
        total_recipients = campaigns.aggregate(total=Sum('recipient_count'))['total'] or 0
        total_opens = campaigns.aggregate(total=Sum('opens_count'))['total'] or 0
        total_clicks = campaigns.aggregate(total=Sum('clicks_count'))['total'] or 0
        
        # Средние показатели
        sent_campaigns = campaigns.filter(status=EmailCampaign.STATUS_SENT)
        avg_open_rate = sent_campaigns.aggregate(avg=Avg('opens_count'))['avg'] or 0
        avg_click_rate = sent_campaigns.aggregate(avg=Avg('clicks_count'))['avg'] or 0
        
        if sent_campaigns.count() > 0:
            avg_open_rate = round(avg_open_rate / sent_campaigns.count(), 2)
            avg_click_rate = round(avg_click_rate / sent_campaigns.count(), 2)
        
        # Количество шаблонов и сегментов
        template_count = EmailTemplate.objects.filter(created_by=user).count()
        segment_count = ContactSegment.objects.filter(created_by=user).count()
        
        data = {
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'total_recipients': total_recipients,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'average_open_rate': avg_open_rate,
            'average_click_rate': avg_click_rate,
            'template_count': template_count,
            'segment_count': segment_count
        }
        
        serializer = MarketingOverviewSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def performance(self, request):
        """Производительность кампаний за период"""
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        date_from = timezone.now() - timedelta(days=days)
        
        # Кампании за период
        campaigns = EmailCampaign.objects.filter(
            created_by=user,
            created_at__gte=date_from,
            status=EmailCampaign.STATUS_SENT
        )
        
        performance_data = []
        for campaign in campaigns:
            # Статистика по кампании
            stats = campaign.daily_stats.all().aggregate(
                total_sent=Sum('sent'),
                total_opens=Sum('opened'),
                total_clicks=Sum('clicked'),
                total_unsubscribes=Sum('unsubscribed')
            )
            
            sent = stats['total_sent'] or 0
            opens = stats['total_opens'] or 0
            clicks = stats['total_clicks'] or 0
            unsubscribes = stats['total_unsubscribes'] or 0
            
            open_rate = round((opens / sent * 100), 2) if sent > 0 else 0
            click_rate = round((clicks / sent * 100), 2) if sent > 0 else 0
            
            # ROI (заглушка - в реальном проекте будет связь со сделками)
            revenue = sent * 100  # Заглушка: 100 руб с каждого письма
            cost = sent * 10      # Заглушка: 10 руб на отправку
            roi = round(((revenue - cost) / cost) * 100, 2) if cost > 0 else 0
            
            performance_data.append({
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'sent': sent,
                'opens': opens,
                'clicks': clicks,
                'open_rate': open_rate,
                'click_rate': click_rate,
                'unsubscribes': unsubscribes,
                'revenue': revenue,
                'roi': roi
            })
        
        return Response(performance_data)
    
    @action(detail=False, methods=['GET'])
    def timeline(self, request):
        """Временная шкала активности"""
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        date_from = timezone.now() - timedelta(days=days)
        
        # Статистика по дням
        daily_stats = CampaignStatistic.objects.filter(
            campaign__created_by=user,
            date__gte=date_from
        ).values('date').annotate(
            total_sent=Sum('sent'),
            total_opens=Sum('opened'),
            total_clicks=Sum('clicked')
        ).order_by('date')
        
        timeline_data = []
        for stat in daily_stats:
            sent = stat['total_sent'] or 0
            opens = stat['total_opens'] or 0
            clicks = stat['total_clicks'] or 0
            
            open_rate = round((opens / sent * 100), 2) if sent > 0 else 0
            click_rate = round((clicks / sent * 100), 2) if sent > 0 else 0
            
            timeline_data.append({
                'date': stat['date'].isoformat(),
                'sent': sent,
                'opens': opens,
                'clicks': clicks,
                'open_rate': open_rate,
                'click_rate': click_rate
            })
        
        return Response(timeline_data)