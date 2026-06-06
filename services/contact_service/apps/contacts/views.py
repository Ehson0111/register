from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Contact, Deal, DealStage, Service, AuditTrail, ContactCompanyDetails

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import logging
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from .models import Contact, Service, Deal, DealStage
from .serializers import (
    ContactListSerializer, ContactDetailSerializer, AddContactSerializer,
    ServiceSerializer, DealStageSerializer, DealListSerializer, DealDetailSerializer, CreateDealSerializer
    ,SimpleContactSerializer,SimpleServiceSerializer, AuditTrailSerializer
)
from .permissions import IsManager,IsClient
from .inn_lookup import fetch_company_by_inn, map_company_data, normalize_inn

logger = logging.getLogger(__name__)


def _actor_name(request):
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        full = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
        return full or getattr(user, "email", "") or getattr(user, "username", "") or "manager"
    return "system"


def _audit(request, action, entity_type, entity_id=None, metadata=None):
    AuditTrail.objects.create(
        actor=_actor_name(request),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata or {},
    )


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

    def perform_update(self, serializer):
        contact = serializer.save()
        _audit(
            self.request,
            AuditTrail.ACTION_CONTACT_UPDATED,
            "contact",
            contact.id,
            {"email": contact.email, "status": contact.status},
        )

    def perform_destroy(self, instance):
        contact_id = instance.id
        email = instance.email
        instance.delete()
        _audit(
            self.request,
            AuditTrail.ACTION_CONTACT_DELETED,
            "contact",
            contact_id,
            {"email": email},
        )

@api_view(['DELETE'])
@permission_classes([IsManager])
def ContactDeleteViews(request, item_id):
    """Удаление контакта"""
    contact = get_object_or_404(Contact, id=item_id)
    contact_email = contact.email
    contact.delete()
    _audit(
        request,
        AuditTrail.ACTION_CONTACT_DELETED,
        "contact",
        item_id,
        {"email": contact_email},
    )

    return Response({
        'message': 'Контакт успешно удален'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST']) 
@permission_classes([IsManager])
def load_company_data_by_inn(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)

    try:
        inn = normalize_inn(request.data.get('inn') or contact.inn)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        raw_data = fetch_company_by_inn(inn)
        mapped = map_company_data(raw_data)

        details, _ = ContactCompanyDetails.objects.update_or_create(
            contact=contact,
            defaults=mapped,
        )

        if not contact.inn:
            contact.inn = inn
            contact.save(update_fields=['inn'])

        _audit(
            request,
            AuditTrail.ACTION_CONTACT_UPDATED,
            "contact",
            contact.id,
            {"inn_lookup": inn, "company_name": details.company_name},
        )

        return Response({
            'message': 'Данные по ИНН загружены',
            'company_details': {
                'company_name': details.company_name,
                'inn': details.inn,
                'kpp': details.kpp,
                'ogrn': details.ogrn,
                'status_text': details.status_text,
                'address': details.address,
                'okved': details.okved,
                'director': details.director,
                'updated_at': details.updated_at,
            }
        })
    except Exception as exc:
        details, _ = ContactCompanyDetails.objects.update_or_create(
            contact=contact,
            defaults={
                'company_name': 'Не найдено',
                'inn': inn,
                'kpp': 'Не найдено',
                'ogrn': 'Не найдено',
                'status_text': 'Не найдено',
                'address': 'Не найдено',
                'okved': 'Не найдено',
                'director': 'Не найдено',
                'raw_data': {'error': str(exc)},
            },
        )
        return Response({
            'message': 'Данные по ИНН не найдены',
            'company_details': {
                'company_name': details.company_name,
                'inn': details.inn,
                'kpp': details.kpp,
                'ogrn': details.ogrn,
                'status_text': details.status_text,
                'address': details.address,
                'okved': details.okved,
                'director': details.director,
                'updated_at': details.updated_at,
            }
        })


# @api_view(['GET'])
# @permission_classes([IsClient])
# def client_profile(request):
#     try:
#         contact =get_object_or_404(Contact,email=request.user.email)

#         serializer=ContactDetailSerializer(contact)
#         return Response(
#             serializer.data
#         )
#     except Contact.DoesNotExist:
#         return Response({
#             'error':'Контакт не найден ',
#             'detail': f'Контакт с email {request.user.email} не найден в базе'
#         },status=404)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsClient])
# def client_profile(request):
#     """
#     Профиль клиента
#     - Если Contact есть - возвращаем
#     - Если нет - создаём из данных User
#     """
#     try:
#         # Пробуем найти по email
#         contact = Contact.objects.get(email=request.user.email)
#     except Contact.DoesNotExist:
#         # Создаём новый Contact из User
#         contact = Contact.objects.create(
#             email=request.user.email,
#             first_name=request.user.first_name or '',
#             last_name=request.user.last_name or '',
#             status='client'  # Важно!
#         )
    
#     serializer = ContactDetailSerializer(contact)
#     return Response(serializer.data)
         
 
 
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_profile(request):
    """
    Профиль клиента.
    Возвращает данные контакта по email из JWT.
    Если контакт не найден — создаёт его автоматически из данных пользователя.
    """
    try:
        # Ищем контакт по email из токена
        contact = Contact.objects.get(email=request.user.email)
    except Contact.DoesNotExist:
        # Создаём новый контакт, если его нет
        contact = Contact.objects.create(
            email=request.user.email,
            first_name=request.user.first_name or '',
            last_name=request.user.last_name or '',
            status='client',  # Важно: сразу делаем клиентом
        )
    
    serializer = ContactDetailSerializer(contact)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_deals(request):
    """
    Список сделок клиента.
    Фильтруется по контакту  и опционально по статусу.
    """
    try:
        # Находим контакт клиента
        contact = get_object_or_404(Contact, email=request.user.email)
        
        # Все сделки этого контакта
        deals = Deal.objects.filter(contact=contact).select_related('service')
        
        # Фильтр по статусу, если передан
        status_filter = request.query_params.get('status')
        if status_filter:
            deals = deals.filter(status=status_filter)
        
        # Сортировка по дате создания (новые сверху)
        deals = deals.order_by('-created_at')
        
        serializer = DealListSerializer(deals, many=True)
        
        return Response({
            'contact': {
                'id': contact.id,
                'full_name': contact.get_full_name(),
                'email': contact.email
            },
            'total_deals': deals.count(),
            'deals': serializer.data
        })
    
    except Contact.DoesNotExist:
        return Response({
            'error': 'Контакт не найден',
            'detail': f'Контакт с email {request.user.email} не найден'
        }, status=404)
    except Exception as e:
        return Response({
            'error': 'Ошибка сервера',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsClient])
def client_services_list(request):
    """Список активных услуг для клиента (выбор при создании заявки)."""
    services = Service.objects.filter(is_active=True).order_by('name')
    serializer = SimpleServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsClient])
def create_client_request(request):
    """
    Создание запроса (сделки) от клиента.
    Требует service_id и опционально message и budget.
    """
    # Находим контакт клиента
    contact = get_object_or_404(Contact, email=request.user.email)
    
    # Обязательный параметр — ID услуги
    service_id = request.data.get('service_id')
    if not service_id:
        return Response({
            'error': 'Поле service_id обязательно'
        }, status=400)
    
    # Проверяем, что услуга существует и активна
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    # Создаём сделку-запрос
    deal = Deal.objects.create(
        contact=contact,
        service=service,
        title=f"Запрос: {service.name}",
        description=request.data.get('message', ''),
        amount=request.data.get('budget', service.price),  # Можно переопределить бюджет
        status='new'
    )
    
    return Response({
        'deal_id': deal.id,
        'message': 'Запрос успешно создан',
        'deal': DealListSerializer(deal).data  # Опционально возвращаем данные сделки
    }, status=201)
# э      

@api_view(['POST'])
@permission_classes([IsManager])
def add_to_contact(request):
    """Добавление нового контакта"""
    # logger.info(f"Add contact request from user {request.user}: {request.data}")

    serializer = AddContactSerializer(data=request.data)

    if serializer.is_valid():
        contact = serializer.save()
        logger.info(f"Contact created: {contact.id} by user {request.user}")
        _audit(
            request,
            AuditTrail.ACTION_CONTACT_CREATED,
            "contact",
            contact.id,
            {"email": contact.email, "status": contact.status},
        )

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


class DealStageListCreateView(generics.ListCreateAPIView):
    queryset = DealStage.objects.all().order_by("order", "id")
    serializer_class = DealStageSerializer
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

#   View для сделок
class DealListView(generics.ListCreateAPIView):
    queryset = Deal.objects.all()
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description', 'contact__first_name', 'contact__last_name']
    filterset_fields = ['status', 'service', 'contact', 'stage']

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
        return queryset.select_related('contact', 'service', 'stage')

class DealDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deal.objects.all()
    permission_classes = [IsManager]

    def get_serializer_class(self):
        return DealDetailSerializer

    def get_queryset(self):
        return Deal.objects.select_related('contact', 'service', 'stage')

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
    _audit(
        request,
        AuditTrail.ACTION_DEAL_STATUS_CHANGED,
        "deal",
        deal.id,
        {"old_status": old_status, "new_status": new_status},
    )

    logger.info(f"Deal {deal_id} status changed from {old_status} to {new_status} by {request.user}")
    return Response({
        'message': 'Статус сделки обновлен',
        'deal': DealDetailSerializer(deal).data
    })


@api_view(["POST"])
@permission_classes([IsManager])
def change_deal_stage(request, deal_id):
    deal = get_object_or_404(Deal, id=deal_id)
    stage_id = request.data.get("stage_id")

    if stage_id in (None, "", -1, "-1"):
        stage = None
    else:
        stage = get_object_or_404(DealStage, id=stage_id)
    previous_stage = deal.stage.name if deal.stage else None
    deal.stage = stage
    deal.save(update_fields=["stage", "updated_at"])

    _audit(
        request,
        AuditTrail.ACTION_DEAL_STATUS_CHANGED,
        "deal",
        deal.id,
        {
            "old_stage": previous_stage,
            "new_stage": stage.name if stage else None,
        },
    )

    return Response({
        "message": "Этап сделки обновлен",
        "deal": DealDetailSerializer(deal).data,
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
        _audit(
            request,
            AuditTrail.ACTION_DEAL_CREATED,
            "deal",
            deal.id,
            {"status": deal.status, "contact_id": deal.contact_id},
        )

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


class AuditTrailListView(generics.ListAPIView):
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer
    permission_classes = [IsManager]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["actor", "action", "entity_type"]
    filterset_fields = ["action", "entity_type", "entity_id"]



def _parse_analytics_period(request):
    """
    Период аналитики:
    - ?days=30 (0 — всё время)
    - ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD (свой диапазон)
    """
    date_from_raw = request.query_params.get('date_from')
    date_to_raw = request.query_params.get('date_to')
    if date_from_raw:
        try:
            date_from = datetime.fromisoformat(date_from_raw)
            if timezone.is_naive(date_from):
                date_from = timezone.make_aware(
                    date_from.replace(hour=0, minute=0, second=0, microsecond=0),
                    timezone.get_current_timezone(),
                )
            date_to = timezone.now()
            if date_to_raw:
                date_to = datetime.fromisoformat(date_to_raw)
                if timezone.is_naive(date_to):
                    date_to = timezone.make_aware(
                        date_to.replace(hour=23, minute=59, second=59, microsecond=999999),
                        timezone.get_current_timezone(),
                    )
            return date_from, date_to
        except (TypeError, ValueError):
            pass

    raw = request.query_params.get('days', '30')
    try:
        days = int(raw)
    except (TypeError, ValueError):
        days = 30
    if days <= 0:
        return None, None
    return timezone.now() - timedelta(days=days), None


def _apply_period_filter(qs, since, until=None):
    if since:
        qs = qs.filter(created_at__gte=since)
    if until:
        qs = qs.filter(created_at__lte=until)
    return qs


def _deals_period_q(since, until=None):
    period_deals = Q()
    if since:
        period_deals &= Q(deals__created_at__gte=since)
    if until:
        period_deals &= Q(deals__created_at__lte=until)
    return period_deals


@api_view(['GET'])
@permission_classes([IsManager])
def analytics_overview(request):
    """Общая аналитика по CRM"""
    since, until = _parse_analytics_period(request)
    contacts_qs = _apply_period_filter(Contact.objects.all(), since, until)
    deals_qs = _apply_period_filter(Deal.objects.all(), since, until)

    total_contacts = contacts_qs.count()
    total_deals = deals_qs.count()
    total_services = Service.objects.filter(is_active=True).count()

    deals_by_status = deals_qs.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    )

    contacts_by_status = contacts_qs.values('status').annotate(
        count=Count('id')
    )

    total_revenue = deals_qs.filter(status=Deal.DEAL_WON).aggregate(
        total=Sum('amount')
    )['total'] or 0

    avg_deal_amount = deals_qs.aggregate(
        avg=Avg('amount')
    )['avg'] or 0

    won_deals = deals_qs.filter(status=Deal.DEAL_WON).count()
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
    """Аналитика по времени за выбранный период (?days=)"""
    since, until = _parse_analytics_period(request)
    if not since:
        since = timezone.now() - timedelta(days=30)

    recent_deals = _apply_period_filter(Deal.objects.all(), since, until).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id'),
        total_amount=Sum('amount')
    ).order_by('date')

    # Контакты за последние 30 дней
    recent_contacts = _apply_period_filter(Contact.objects.all(), since, until).extra({
        'date': "DATE(created_at)"
    }).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    # Выигранные сделки за последние 30 дней
    won_deals = _apply_period_filter(
        Deal.objects.filter(status=Deal.DEAL_WON),
        since,
        until,
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
    since, until = _parse_analytics_period(request)
    period_deals = _deals_period_q(since, until)

    contacts_by_deal_count = Contact.objects.annotate(
        deal_count=Count('deals', filter=period_deals),
        total_deal_amount=Sum('deals__amount', filter=period_deals),
        won_deals=Count('deals', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
        won_amount=Sum('deals__amount', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
    ).filter(deal_count__gt=0).order_by('-deal_count')[:10]

    contacts_by_deal_amount = Contact.objects.annotate(
        total_deal_amount=Sum('deals__amount', filter=period_deals),
        deal_count=Count('deals', filter=period_deals),
        won_amount=Sum('deals__amount', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
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
    since, until = _parse_analytics_period(request)
    period_deals = _deals_period_q(since, until)

    services_by_deal_count = Service.objects.filter(is_active=True).annotate(
        deal_count=Count('deals', filter=period_deals),
        total_amount=Sum('deals__amount', filter=period_deals),
        won_deals=Count('deals', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
        won_amount=Sum('deals__amount', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
    ).filter(deal_count__gt=0).order_by('-deal_count')[:10]

    services_by_revenue = Service.objects.filter(is_active=True).annotate(
        total_amount=Sum('deals__amount', filter=period_deals),
        deal_count=Count('deals', filter=period_deals),
        won_amount=Sum('deals__amount', filter=period_deals & Q(deals__status=Deal.DEAL_WON)),
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
    since, until = _parse_analytics_period(request)
    current_year = timezone.now().year
    monthly_performance = []

    for month in range(1, 13):
        month_deals = Deal.objects.filter(
            created_at__year=current_year,
            created_at__month=month
        )
        month_deals = _apply_period_filter(month_deals, since, until)

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