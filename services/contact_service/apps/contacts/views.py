 

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