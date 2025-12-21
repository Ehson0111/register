from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Contact, Deal, Service 

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import logging
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from .models import Contact, Service, Deal
from .serializers import (
    ContactListSerializer, ContactDetailSerializer, AddContactSerializer,
    ServiceSerializer, DealListSerializer, DealDetailSerializer, CreateDealSerializer
    ,SimpleContactSerializer,SimpleServiceSerializer
)
from .permissions import IsManager

logger = logging.getLogger(__name__)

# Контакты (оставляем как есть, но добавляем фильтры)
class ContactListView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactListSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    permission_classes = [IsManager]
    search_fields = ['first_name', 'last_name', 'email', 'company']
    filterset_fields = ['status', 'company']

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    permission_classes = [IsManager]
    
    def get_serializer_class(self):
        return ContactDetailSerializer

@api_view(['DELETE'])
@permission_classes([IsManager])
def ContactDeleteViews(request, item_id):
    """Удаление контакта"""
    contact = get_object_or_404(Contact, id=item_id)
    contact.delete()

    return Response({
        'message': 'Контакт успешно удален'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsManager])
def add_to_contact(request):
    """Добавление нового контакта"""
    logger.info(f"Add contact request from user {request.user}: {request.data}")
    
    serializer = AddContactSerializer(data=request.data)
    
    if serializer.is_valid():
        contact = serializer.save()
        logger.info(f"Contact created: {contact.id} by user {request.user}")
        
        return Response({
            'message': 'Контакт успешно создан',
            'contact': ContactListSerializer(contact).data
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Contact creation failed: {serializer.errors}")
    return Response({
        'message': 'Ошибка при создании контакта',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# Новые View для услуг
class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsManager]

#   View для сделок
class DealListView(generics.ListCreateAPIView):
    queryset = Deal.objects.all()
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'contact__first_name', 'contact__last_name']
    filterset_fields = ['status', 'service', 'contact']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateDealSerializer
        return DealListSerializer
    
    def get_queryset(self):
        queryset = Deal.objects.all()
        # Фильтр по контакту
        contact_id = self.request.query_params.get('contact_id')
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        return queryset.select_related('contact', 'service')

class DealDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deal.objects.all()
    permission_classes = [IsManager]
    
    def get_serializer_class(self):
        return DealDetailSerializer
    
    def get_queryset(self):
        return Deal.objects.select_related('contact', 'service')

@api_view(['GET'])
@permission_classes([IsManager])
def contact_deals_stats(request, contact_id):
    """Статистика сделок по контакту"""
    contact = get_object_or_404(Contact, id=contact_id)
    
    deals = contact.deals.all()
    total_deals = deals.count()
    won_deals = deals.filter(status=Deal.DEAL_WON).count()
    total_amount = sum(deal.amount for deal in deals.filter(status=Deal.DEAL_WON))
    
    return Response({
        'contact': contact.get_full_name(),
        'total_deals': total_deals,
        'won_deals': won_deals,
        'active_deals': total_deals - won_deals - deals.filter(status=Deal.DEAL_LOST).count(),
        'total_amount': total_amount,
        'success_rate': (won_deals / total_deals * 100) if total_deals > 0 else 0
    })

@api_view(['POST'])
@permission_classes([IsManager])
def change_deal_status(request, deal_id):
    """Изменение статуса сделки"""
    deal = get_object_or_404(Deal, id=deal_id)
    
    new_status = request.data.get('status')
    if new_status not in dict(Deal.DEAL_STATUS_CHOICES):
        return Response({
            'error': 'Неверный статус'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    old_status = deal.status
    deal.status = new_status
    
    # Автоматическое обновление даты закрытия
    if new_status in [Deal.DEAL_WON, Deal.DEAL_LOST] and not deal.actual_close_date:
        from django.utils import timezone
        deal.actual_close_date = timezone.now().date()
    
    deal.save()
    
    logger.info(f"Deal {deal_id} status changed from {old_status} to {new_status} by {request.user}")
    
    return Response({
        'message': 'Статус сделки обновлен',
        'deal': DealDetailSerializer(deal).data
    })






# для создание услуги 

@api_view(['POST'])
@permission_classes([IsManager])
def create_service(request):
    """Создание новой услуги"""
    logger.info(f"Create service request from user {request.user}")
    
    serializer = ServiceSerializer(data=request.data)
    
    if serializer.is_valid():
        service = serializer.save()
        logger.info(f"Service created: {service.id} - {service.name}")
        
        return Response({
            'message': 'Услуга успешно создана',
            'service': ServiceSerializer(service).data
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Service creation failed: {serializer.errors}")
    return Response({
        'message': 'Ошибка при создании услуги',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_service(request, service_id):
    """Удаление услуги (мягкое удаление - деактивация)"""
    service = get_object_or_404(Service, id=service_id)
    
    # Проверяем, нет ли активных сделок с этой услугой
    active_deals = service.deals.exclude(status__in=[Deal.DEAL_WON, Deal.DEAL_LOST]).count()
    
    if active_deals > 0:
        return Response({
            'message': f'Невозможно удалить услугу. Есть активные сделки: {active_deals}',
            'active_deals': active_deals
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Мягкое удаление - деактивация
    service.is_active = False
    service.save()
    
    logger.info(f"Service deactivated: {service.id} - {service.name} by {request.user}")
    
    return Response({
        'message': 'Услуга успешно деактивирована'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsManager])
def create_deal(request):
    """Создание новой сделки"""
    logger.info(f"Create deal request from user {request.user}")
    
    serializer = CreateDealSerializer(data=request.data)
    
    if serializer.is_valid():
        deal = serializer.save()
        logger.info(f"Deal created: {deal.id} - {deal.title}")
        
        return Response({
            'message': 'Сделка успешно создана',
            'deal': DealListSerializer(deal).data
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Deal creation failed: {serializer.errors}")
    return Response({
        'message': 'Ошибка при создании сделки',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_deal(request, deal_id):
    """Удаление сделки"""
    deal = get_object_or_404(Deal, id=deal_id)
    
    deal_title = deal.title
    deal.delete()
    
    logger.info(f"Deal deleted: {deal_id} - {deal_title} by {request.user}")
    
    return Response({
        'message': 'Сделка успешно удалена'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsManager])
def get_services_for_select(request):
    """Получение списка услуг для выпадающего списка"""
    services = Service.objects.filter(is_active=True)
    serializer = SimpleServiceSerializer(services, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsManager])
def get_contacts_for_select(request):
    """Получение списка контактов для выпадающего списка"""
    contacts = Contact.objects.all()
    serializer = SimpleContactSerializer(contacts, many=True)
    return Response(serializer.data)

 

@api_view(['GET'])
@permission_classes([IsManager])
def analytics_overview(request):
    """Общая аналитика по CRM"""
    user = request.user
    
    # Общие данные
    total_contacts = Contact.objects.count()
    total_deals = Deal.objects.count()
    total_services = Service.objects.filter(is_active=True).count()
    
    # Сделки по статусам
    deals_by_status = Deal.objects.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )
    
    # Контакты по статусам
    contacts_by_status = Contact.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Сумма всех успешных сделок
    total_revenue = Deal.objects.filter(status=Deal.DEAL_WON).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Средняя стоимость сделки
    avg_deal_amount = Deal.objects.aggregate(
        avg=Avg('amount')
    )['avg'] or 0
    
    # Конверсия (процент выигранных сделок от всех сделок)
    won_deals = Deal.objects.filter(status=Deal.DEAL_WON).count()
    conversion_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
    
    return Response({
        'overview': {
            'total_contacts': total_contacts,
            'total_deals': total_deals,
            'total_services': total_services,
            'total_revenue': float(total_revenue),
            'avg_deal_amount': float(avg_deal_amount),
            'conversion_rate': round(conversion_rate, 2)
        },
        'deals_by_status': list(deals_by_status),
        'contacts_by_status': list(contacts_by_status)
    })

@api_view(['GET'])
@permission_classes([IsManager])
def analytics_timeline(request):
    """Аналитика по времени (последние 30 дней)"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Сделки за последние 30 дней
    recent_deals = Deal.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('date')
    
    # Контакты за последние 30 дней
    recent_contacts = Contact.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Выигранные сделки за последние 30 дней
    won_deals = Deal.objects.filter(
        status=Deal.DEAL_WON,
        created_at__gte=thirty_days_ago
    ).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('date')
    
    return Response({
        'deals_timeline': list(recent_deals),
        'contacts_timeline': list(recent_contacts),
        'won_deals_timeline': list(won_deals)
    })

@api_view(['GET'])
@permission_classes([IsManager])
def analytics_top_contacts(request):
    """Топ контактов по количеству сделок и сумме"""
    # Топ контактов по количеству сделок
    contacts_by_deal_count = Contact.objects.annotate(
        deal_count=Count('deals'),
        total_deal_amount=Sum('deals__amount'),
        won_deals=Count('deals', filter=Q(deals__status=Deal.DEAL_WON)),
        won_amount=Sum('deals__amount', filter=Q(deals__status=Deal.DEAL_WON))
    ).filter(deal_count__gt=0).order_by('-deal_count')[:10]
    
    # Топ контактов по сумме сделок
    contacts_by_deal_amount = Contact.objects.annotate(
        total_deal_amount=Sum('deals__amount'),
        deal_count=Count('deals'),
        won_amount=Sum('deals__amount', filter=Q(deals__status=Deal.DEAL_WON))
    ).filter(total_deal_amount__gt=0).order_by('-total_deal_amount')[:10]
    
    return Response({
        'by_deal_count': [
            {
                'id': contact.id,
                'full_name': contact.get_full_name(),
                'company': contact.company,
                'deal_count': contact.deal_count,
                'total_deal_amount': float(contact.total_deal_amount or 0),
                'won_deals': contact.won_deals,
                'won_amount': float(contact.won_amount or 0)
            }
            for contact in contacts_by_deal_count
        ],
        'by_deal_amount': [
            {
                'id': contact.id,
                'full_name': contact.get_full_name(),
                'company': contact.company,
                'total_deal_amount': float(contact.total_deal_amount or 0),
                'deal_count': contact.deal_count,
                'won_amount': float(contact.won_amount or 0)
            }
            for contact in contacts_by_deal_amount
        ]
    })

@api_view(['GET'])
@permission_classes([IsManager])
def analytics_top_services(request):
    """Топ услуг по популярности и доходу"""
    # Топ услуг по количеству сделок
    services_by_deal_count = Service.objects.filter(is_active=True).annotate(
        deal_count=Count('deals'),
        total_amount=Sum('deals__amount'),
        won_deals=Count('deals', filter=Q(deals__status=Deal.DEAL_WON)),
        won_amount=Sum('deals__amount', filter=Q(deals__status=Deal.DEAL_WON))
    ).filter(deal_count__gt=0).order_by('-deal_count')[:10]
    
    # Топ услуг по доходу
    services_by_revenue = Service.objects.filter(is_active=True).annotate(
        total_amount=Sum('deals__amount'),
        deal_count=Count('deals'),
        won_amount=Sum('deals__amount', filter=Q(deals__status=Deal.DEAL_WON))
    ).filter(total_amount__gt=0).order_by('-total_amount')[:10]
    
    return Response({
        'by_popularity': [
            {
                'id': service.id,
                'name': service.name,
                'price': float(service.price),
                'deal_count': service.deal_count,
                'total_amount': float(service.total_amount or 0),
                'won_deals': service.won_deals,
                'won_amount': float(service.won_amount or 0)
            }
            for service in services_by_deal_count
        ],
        'by_revenue': [
            {
                'id': service.id,
                'name': service.name,
                'price': float(service.price),
                'total_amount': float(service.total_amount or 0),
                'deal_count': service.deal_count,
                'won_amount': float(service.won_amount or 0)
            }
            for service in services_by_revenue
        ]
    })

@api_view(['GET'])
@permission_classes([IsManager])
def analytics_deal_performance(request):
    """Анализ эффективности сделок"""
    # Анализ по месяцам
    current_year = timezone.now().year
    monthly_performance = []
    
    for month in range(1, 13):
        month_deals = Deal.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        )
        
        total_deals = month_deals.count()
        won_deals = month_deals.filter(status=Deal.DEAL_WON).count()
        lost_deals = month_deals.filter(status=Deal.DEAL_LOST).count()
        total_amount = month_deals.filter(status=Deal.DEAL_WON).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        conversion_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
        
        monthly_performance.append({
            'month': month,
            'total_deals': total_deals,
            'won_deals': won_deals,
            'lost_deals': lost_deals,
            'total_amount': float(total_amount),
            'conversion_rate': round(conversion_rate, 2)
        })
    
    # Анализ по вероятности
    probability_analysis = []
    for prob_range in [(0, 25), (26, 50), (51, 75), (76, 100)]:
        deals = Deal.objects.filter(
            probability__gte=prob_range[0],
            probability__lte=prob_range[1]
        )
        
        won_deals = deals.filter(status=Deal.DEAL_WON).count()
        conversion_rate = (won_deals / deals.count() * 100) if deals.count() > 0 else 0
        
        probability_analysis.append({
            'range': f"{prob_range[0]}-{prob_range[1]}%",
            'total_deals': deals.count(),
            'won_deals': won_deals,
            'conversion_rate': round(conversion_rate, 2)
        })
    
    return Response({
        'monthly_performance': monthly_performance,
        'probability_analysis': probability_analysis
    })