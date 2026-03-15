 


from django.http import HttpResponse
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
import requests
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import datetime, timedelta
import json
import threading
import logging
import os

from .models import Template, Campaign, CampaignRecipient
from .serializers import (
    TemplateSerializer, CampaignSerializer,
    SendCampaignSerializer, IndividualSendSerializer,
    QuickMessageSerializer
)
from .services import MarketingService

logger = logging.getLogger(__name__)

# Used for internal calls to contact-service via gateway.
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")


class TemplateViewSet(viewsets.ModelViewSet):
    """ViewSet для шаблонов"""
    permission_classes = [IsAuthenticated]
    serializer_class = TemplateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'subject']
    filterset_fields = ['template_type', 'is_active']
    
    def get_queryset(self):
        """Только шаблоны текущего пользователяsdd"""
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


def send_campaign_async(campaign_id, recipient_ids, client_info_map=None, template_variables=None):
    """Асинхронная отправка кампании"""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        service = MarketingService()
        
        result = service.send_campaign(
            campaign, 
            recipient_ids, 
            client_info_map,
            template_variables=template_variables
        )
        
        logger.info(f"Кампания {campaign_id} отправлена: {result['success']} успешно, {result['failed']} с ошибками")
        
    except Exception as e:
        logger.error(f"Ошибка при асинхронной отправке кампании {campaign_id}: {str(e)}")


def send_quick_message_async(campaign_id, recipient_ids, client_info_map=None):
    """Асинхронная отправка быстрого сообщения"""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        service = MarketingService()
        
        result = service.send_quick_message_campaign(campaign, recipient_ids, client_info_map)
        
        logger.info(f"Быстрая рассылка {campaign_id} отправлена: {result['success']} успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при быстрой рассылке {campaign_id}: {str(e)}")


class SendCampaignView(APIView):
    """Отправка рассылки с шаблоном (массовая или индивидуальная)"""
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
            print(recipient_ids)
            # recipient_ids = []  # Заглушка
        
        # Проверяем, есть ли получатели
        if not recipient_ids:
            return Response(
                {'error': 'Нет получателей для отправки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем кампанию
        campaign_name = data.get('campaign_name', f'Рассылка от {timezone.now().strftime("%d.%m.%Y %H:%M")}')
        
        # Используем контент из запроса или из шаблона
        content = data.get('content', template.content)
        subject = data.get('subject', template.subject)
        
        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type='bulk' if len(recipient_ids) > 1 else 'individual',
            status='sending',
            template=template,
            subject=subject,
            content=content,
            recipients=recipient_ids,
            recipient_count=len(recipient_ids),
            manager_id=user.id
        )
        
        # Получаем информацию о всех клиентах
        client_info_map = self._get_clients_info(request, recipient_ids)
        
        # Собираем общие переменные для всех получателей
        common_variables = data.get('variables', {})
        
        # Добавляем системные переменные
        common_variables.update({
            'manager_id': user.id,
            'date': timezone.now().strftime('%d.%m.%Y'),
            'company': campaign_name,
        })
        
        # Запускаем отправку в отдельном потоке (для массовых рассылок)
        if len(recipient_ids) > 1:
            # Запускаем в отдельном потоке
            thread = threading.Thread(
                target=send_campaign_async,
                args=(campaign.id, recipient_ids, client_info_map, common_variables)
            )
            thread.daemon = True
            thread.start()
            
            return Response({
                'success': True,
                'message': f'Рассылка запущена для {len(recipient_ids)} получателей',
                'campaign_id': campaign.id,
                'status': 'sending',
                'common_variables': common_variables
            }, status=status.HTTP_202_ACCEPTED)
        
        else:
            # Для одного получателя отправляем сразу
            client_info = client_info_map.get(recipient_ids[0]) if client_info_map else {}
            
            # Собираем полный набор переменных для этого получателя
            recipient_variables = self._build_recipient_variables(
                client_info, common_variables, recipient_ids[0], user.id, campaign_name
            )
            
            service = MarketingService()
            success, error_msg = service.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_ids[0] if recipient_ids else None,
                client_info=client_info,
                template_variables=recipient_variables
            )
            
            if success:
                campaign.status = 'sent'
                campaign.sent_at = timezone.now()
                campaign.success_count = 1
                campaign.save()
                
                return Response({
                    'success': True,
                    'message': 'Сообщение отправлено успешно',
                    'campaign_id': campaign.id,
                    'variables_used': recipient_variables
                }, status=status.HTTP_201_CREATED)
            else:
                campaign.status = 'failed'
                campaign.failed_count = 1
                campaign.save()
                
                return Response({
                    'success': False,
                    'error': error_msg,
                    'campaign_id': campaign.id
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_recipient_variables(self, client_info, common_variables, recipient_id, manager_id, campaign_name):
        """Собирает переменные для конкретного получателя"""
        variables = {}
        
        # 1. Добавляем информацию о клиенте из БД
        if client_info:
            variables.update({
                'client_id': client_info.get('id', recipient_id),
                'client_name': client_info.get('name', '') or client_info.get('client_name', ''),
                'name': client_info.get('name', '') or client_info.get('client_name', ''),
                'client_email': client_info.get('email', ''),
                'phone': client_info.get('phone', ''),
                'company': client_info.get('company', ''),
            })
        
        # 2. Добавляем общие переменные из запроса
        variables.update(common_variables)
        
        # 3. Добавляем системные переменные
        variables.update({
            'manager_id': manager_id,
            'date': timezone.now().strftime('%d.%m.%Y'),
            'campaign_name': campaign_name,
        })
        
        return variables
    
    def _get_clients_info(self, request, client_ids):
        """Получить информацию о клиенте"""
        try:
            client_info_map = {}

            # Проходим по всем client_ids
            for client_id in client_ids:
                headers = {}
                important_headers = [
                    'Authorization', 'Content-Type', 'Accept', 'User-Agent',
                    'Accept-Language', 'Accept-Encoding'
                ]

                # Переносим важные заголовки из запроса
                for header_name in important_headers:
                    header_value = request.headers.get(header_name)
                    if header_value:
                        headers[header_name] = header_value

                # Пример URL для получения информации о клиенте
                target_url = f'{GATEWAY_URL}/api/contacts/{client_id}/'
                params = dict(request.GET.items())  # Получаем query параметры (если есть)

                # Логируем запрос для отладки
                logger.info(f"Получаем информацию о клиенте: {target_url}")

                # Делаем GET-запрос к API для получения информации о клиенте
                response = requests.get(
                    target_url,
                    headers=headers,
                    params=params,
                    timeout=30
                )

                # Проверяем успешность ответа
                if response.status_code == 200 or response.status_code==201:
                    # Если запрос успешен, сохраняем данные клиента
                    client_info_map[client_id] = response.json()
                
                else:
                    # Если ошибка, логируем и добавляем заглушку
                    logger.error(f"Ошибка при получении информации о клиенте {client_id}: {response.status_code}")
                    client_info_map[client_id] = {
                        'id': client_id,
                        'name': f'Информация о клиенте #{client_id} не найдена',
                        'email': f'client{client_id}@example.com',
                        'phone': '+7999000' + str(client_id).zfill(4)
                    }

            return client_info_map

        except Exception as e:
            logger.error(f"Ошибка при запросе информации о клиенте: {e}")

            # Возвращаем заглушки для всех запрошенных client_ids
            result = {}
            for client_id in client_ids:
                result[client_id] = {
                    'id': client_id,
                    'name': f'Ошибка при запросе информации о клиенте #{client_id}',
                    'email': f'client{client_id}@example.com',
                    'phone': '+7999000' + str(client_id).zfill(4)
                }
            return result


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
        
        recipient_id = data['recipient_id']
        
        # Получаем информацию о клиенте из БД
        client_info = self._get_client_info(request, recipient_id)
        
        # СОБИРАЕМ ВСЕ ПЕРЕМЕННЫЕ В ОДИН СЛОВАРЬ
        variables = {}
        
        # 1. Сначала добавляем базовую информацию из БД (клиент)
        if client_info:
            variables.update({
                'client_id': client_info.get('id', recipient_id),
                'client_name': client_info.get('name', '') or client_info.get('client_name', ''),
                'name': client_info.get('name', '') or client_info.get('client_name', ''),
                'client_email': client_info.get('email', ''),
                'phone': client_info.get('phone', ''),
                'company': client_info.get('company', '')
            })
        
        # 2. Затем добавляем переменные из запроса (они имеют приоритет)
        if 'variables' in data and data['variables']:
            variables.update(data['variables'])
        
        # 3. Добавляем системные переменные
        variables.update({
            'manager_id': user.id,
            'date': timezone.now().strftime('%d.%m.%Y'),
        })
        
        # 4. Создаем имя кампании
        campaign_name = f"Индивидуальная рассылка клиенту #{recipient_id}"
        if variables.get('client_name'):
            campaign_name = f"Рассылка для {variables['client_name']}"
        elif variables.get('name'):
            campaign_name = f"Рассылка для {variables['name']}"
        
        # Создаем кампанию
        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type='individual',
            status='sending',
            template=template,
            subject=template.subject,
            content=template.content,
            recipients=[recipient_id],
            recipient_count=1,
            manager_id=user.id
        )
        
        # Отправляем сообщение с собранными переменными
        service = MarketingService()
        
        # Передаем variables в send_to_recipient
        success, error_msg = service.send_to_recipient(
            campaign=campaign,
            recipient_id=recipient_id,
            client_info=client_info,
            template_variables=variables
        )
        
        if success:
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
            campaign.success_count = 1
            campaign.save()
            
            return Response({
                'success': True,
                'message': f'Сообщение отправлено клиенту #{recipient_id}',
                'campaign_id': campaign.id,
                'variables_used': variables,
                'recipient': {
                    'id': recipient_id,
                    'info': client_info
                }
            }, status=status.HTTP_201_CREATED)
        else:
            campaign.status = 'failed'
            campaign.failed_count = 1
            campaign.save()
            
            return Response({
                'success': False,
                'error': error_msg,
                'campaign_id': campaign.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_info(self, request, client_id):
        """Получить информацию о клиенте"""
        try:
            headers = {}
            important_headers = [
                'Authorization', 'Content-Type', 'Accept', 'User-Agent',
                'Accept-Language', 'Accept-Encoding'
            ]
            
            # Переносим важные заголовки из запроса
            for header_name in important_headers:
                header_value = request.headers.get(header_name)
                if header_value:
                    headers[header_name] = header_value

            # Пример URL для получения информации о клиенте
            target_url = f'{GATEWAY_URL}/api/contacts/{client_id}/'
            params = dict(request.GET.items())

            # Логируем запрос для отладки
            logger.info(f"Получаем информацию о клиенте: {target_url}")

            # Делаем GET-запрос к API для получения информации о клиенте
            response = requests.get(
                target_url,
                headers=headers,
                params=params,
                timeout=30
            )

            # Проверяем успешность ответа
            if response.status_code == 200 or response.status_code==201:
                return response.json()
            else:
                logger.error(f"Ошибка при получении информации о клиенте: {response.status_code}")
                return {
                    'id': client_id,
                    'name': f'Информация о клиенте #{client_id} не найдена',
                    'email': f'client{client_id}@example.com',
                    'phone': '+7999000' + str(client_id).zfill(4)
                }

        except Exception as e:
            logger.error(f"Ошибка при запросе информации о клиенте: {e}")
            return {
                'id': client_id,
                'name': f'Ошибка при запросе информации о клиенте #{client_id}',
                'email': f'client{client_id}@example.com',
                'phone': '+7999000' + str(client_id).zfill(4)
            }


class QuickMessageView(APIView):
    """Быстрая отправка сообщения без шаблона"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = QuickMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        user = request.user
        
        recipient_ids = data.get('recipient_ids', [])
        
        if not recipient_ids:
            return Response(
                {'error': 'Нет получателей для отправки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем кампанию без шаблона
        campaign_name = data.get('campaign_name', f'Быстрая рассылка от {timezone.now().strftime("%d.%m.%Y %H:%M")}')
        
        # Создаем временный шаблон
        temp_template = Template.objects.create(
            name=f"Быстрый шаблон - {timezone.now().strftime('%H:%M:%S')}",
            template_type=data.get('message_type', 'email'),
            subject=data.get('subject', 'Сообщение от менеджера'),
            content=data['message'],
            manager_id=user.id,
            is_active=False  # Помечаем как неактивный
        )
        
        campaign = Campaign.objects.create(
            name=campaign_name,
            campaign_type='bulk' if len(recipient_ids) > 1 else 'individual',
            status='sending',
            template=temp_template,
            subject=temp_template.subject,
            content=temp_template.content,
            recipients=recipient_ids,
            recipient_count=len(recipient_ids),
            manager_id=user.id
        )
        
        # Получаем информацию о всех клиентах
        client_info_map = self._get_clients_info(request, recipient_ids)
        
        if len(recipient_ids) > 1:
            # Запускаем в отдельном потоке
            thread = threading.Thread(
                target=send_quick_message_async,
                args=(campaign.id, recipient_ids, client_info_map)
            )
            thread.daemon = True
            thread.start()
            
            return Response({
                'success': True,
                'message': f'Быстрая рассылка запущена для {len(recipient_ids)} получателей',
                'campaign_id': campaign.id,
                'status': 'sending'
            }, status=status.HTTP_202_ACCEPTED)
        else:
            # Для одного получателя отправляем сразу
            client_info = client_info_map.get(recipient_ids[0]) if client_info_map else {}
            
            service = MarketingService()
            success, error_msg = service.send_to_recipient(
                campaign=campaign,
                recipient_id=recipient_ids[0],
                client_info=client_info,
                # Для быстрых сообщений передаем базовые переменные
                template_variables={
                    'client_id': recipient_ids[0],
                    'name': client_info.get('name', f'Клиент #{recipient_ids[0]}'),
                    'client_name': client_info.get('name', f'Клиент #{recipient_ids[0]}'),
                    'date': timezone.now().strftime('%d.%m.%Y'),
                    'manager_id': user.id,
                }
            )
            
            if success:
                campaign.status = 'sent'
                campaign.sent_at = timezone.now()
                campaign.success_count = 1
                campaign.save()
                
                return Response({
                    'success': True,
                    'message': 'Быстрое сообщение отправлено успешно',
                    'campaign_id': campaign.id
                }, status=status.HTTP_201_CREATED)
            else:
                campaign.status = 'failed'
                campaign.failed_count = 1
                campaign.save()
                
                return Response({
                    'success': False,
                    'error': error_msg,
                    'campaign_id': campaign.id
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_clients_info(self, request, client_ids):
        """Получить информацию о клиенте (копия метода из SendCampaignView)"""
        try:
            client_info_map = {}
            
            for client_id in client_ids:
                headers = {}
                important_headers = ['Authorization', 'Content-Type', 'Accept']
                
                for header_name in important_headers:
                    header_value = request.headers.get(header_name)
                    if header_value:
                        headers[header_name] = header_value

                target_url = f'{GATEWAY_URL}/api/contacts/{client_id}/'
                
                response = requests.get(
                    target_url,
                    headers=headers,
                    timeout=30
                )

                if response.status_code == 200 or response.status_code==201:
                    client_info_map[client_id] = response.json()
                else:
                    logger.error(f"Ошибка при получении информации о клиенте {client_id}: {response.status_code}")
                    client_info_map[client_id] = {
                        'id': client_id,
                        'name': f'Клиент #{client_id}',
                        'email': f'client{client_id}@example.com',
                        'phone': '+7999000' + str(client_id).zfill(4)
                    }

            return client_info_map

        except Exception as e:
            logger.error(f"Ошибка при запросе информации о клиенте: {e}")
            result = {}
            for client_id in client_ids:
                result[client_id] = {
                    'id': client_id,
                    'name': f'Клиент #{client_id}',
                    'email': f'client{client_id}@example.com',
                    'phone': '+7999000' + str(client_id).zfill(4)
                }
            return result


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