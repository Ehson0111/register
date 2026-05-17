from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q

from .models import CalendarTask
from .serializers import (
    CalendarTaskSerializer, 
    CalendarTaskCreateSerializer,
    CalendarTaskUpdateSerializer,
    CalendarStatsSerializer
)

import logging
logger = logging.getLogger(__name__)


class CalendarTaskViewSet(viewsets.ModelViewSet):
    """ViewSet для задач календаря"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    filterset_fields = ['priority', 'task_type', 'completed', 'date']
    ordering_fields = ['date', 'time', 'priority', 'created_at']
    ordering = ['date', 'time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CalendarTaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CalendarTaskUpdateSerializer
        return CalendarTaskSerializer
    
    def get_queryset(self):
        """Только задачи текущего пользователя"""
        user = self.request.user
        queryset = CalendarTask.objects.filter(manager_id=user.id)
        
        # Фильтры из query params
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        priority = self.request.query_params.get('priority')
        task_type = self.request.query_params.get('task_type')
        completed = self.request.query_params.get('completed')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if priority:
            queryset = queryset.filter(priority=priority)
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Только логирование - manager_id уже установлен в сериализаторе"""
        instance = serializer.save()
        logger.info(f"Task created: {instance.title} by user {self.request.user.id}")
    
    @action(detail=False, methods=['GET'])
    def today(self, request):
        """Задачи на сегодня"""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def upcoming(self, request):
        """Предстоящие задачи (следующие 7 дней)"""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        tasks = self.get_queryset().filter(
            date__gte=today,  # от сегодня
            date__lte=next_week# до через 7 дней
        ).exclude(completed=True) # исключая выполненные
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def overdue(self, request):
        """Просроченные задачи"""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            Q(date__lt=today) |  # дата раньше сегодня
            Q(date=today, time__lt=timezone.now().time()) # сегодня, но время уже прошло
        ).exclude(completed=True)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST'])
    def toggle_complete(self, request, pk=None):
        """Переключить статус выполнения"""
        task = self.get_object()
        
        if task.manager_id != request.user.id:
            return Response(
                {'error': 'Нет доступа к этой задаче'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.completed = not task.completed
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Статистика по задачам"""
        user = request.user
        today = timezone.now().date()
        
        # Получаем задачи пользователя
        user_tasks = CalendarTask.objects.filter(manager_id=user.id)
        
        stats = {
            'total_tasks': user_tasks.count(),
            'completed_tasks': user_tasks.filter(completed=True).count(),
            'high_priority_tasks': user_tasks.filter(
                priority='high', completed=False
            ).count(),
            'today_tasks': user_tasks.filter(date=today).count(),
            'upcoming_tasks': user_tasks.filter(    # Будущие
                date__gt=today, 
                completed=False
            ).count(),
            'overdue_tasks': user_tasks.filter( #Просроченные
                Q(date__lt=today) | 
                Q(date=today, time__lt=timezone.now().time()),
                completed=False
            ).count(),
        }
        
        serializer = CalendarStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_date_range(self, request):
        """Задачи по диапазону дат"""
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Требуются параметры start и end'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(date__gte=start, date__lte=end)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_month(self, request):
        """Задачи по месяцу"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            today = timezone.now().date()
            year = today.year
            month = today.month
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {'error': 'Год и месяц должны быть числами'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(
            date__year=year,
            date__month=month
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class DailyTasksView(generics.ListAPIView):
    """Задачи на конкретный день"""
    serializer_class = CalendarTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        date_str = self.request.query_params.get('date')
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date = timezone.now().date()
        else:
            date = timezone.now().date()
        
        return CalendarTask.objects.filter(
            manager_id=user.id,
            date=date
        ).order_by('time')


class MonthlyCalendarView(APIView):
    """Календарь на месяц"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        if not year or not month:
            today = timezone.now().date()
            year = today.year
            month = today.month
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {'error': 'Год и месяц должны быть числами'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Получаем все задачи на месяц
        tasks = CalendarTask.objects.filter(
            manager_id=request.user.id,
            date__year=year,
            date__month=month
        )
        
        # Группируем по дням
        calendar_data = {}
        for task in tasks:
            day = task.date.day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append(CalendarTaskSerializer(task).data)
        
        return Response({
            'year': year,
            'month': month,
            'tasks_by_day': calendar_data
        })