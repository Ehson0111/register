from rest_framework import serializers
from .models import CalendarTask
from datetime import datetime
from django.utils import timezone

class CalendarTaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач календаря"""
    is_overdue = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    
    class Meta:
        model = CalendarTask
        fields = [
            'id',
            'title',
            'description',
            'task_type',
            'task_type_display',
            'date',
            'formatted_date',
            'time',
            'formatted_time',
            'priority',
            'priority_display',
            'completed',
            'manager_id',
            'location',
            'color',
            'is_recurring',
            'recurrence_rule',
            'is_overdue',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue', 'manager_id']
    
    def get_is_overdue(self, obj):
        """Проверка, просрочена ли задача"""
        if obj.completed:
            return False
        
        today = timezone.now().date()
        if obj.date < today:
            return True
        
        if obj.time and obj.date == today:
            current_time = datetime.now().time()
            return obj.time < current_time
        
        return False
    
    def get_formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    
    def get_formatted_time(self, obj):
        if obj.time:
            return obj.time.strftime('%H:%M')
        return None


class CalendarTaskCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания задачи"""
    class Meta:
        model = CalendarTask
        fields = [
            'title',
            'description',
            'task_type',
            'date',
            'time',
            'priority',
            'location',
            'color',
            'is_recurring',
            'recurrence_rule'
        ]
    
    def validate_date(self, value):
        """Валидация даты"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Нельзя создать задачу на прошедшую дату")
        return value
    
    def create(self, validated_data):
        """Автоматически добавляем manager_id из текущего пользователя"""
        request = self.context.get('request')
        
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['manager_id'] = request.user.id
        else:
            # Если пользователь не аутентифицирован, можно вернуть ошибку
            # или установить значение по умолчанию
            raise serializers.ValidationError({
                "detail": "Пользователь не аутентифицирован"
            })
        
        return super().create(validated_data)


class CalendarTaskUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления задачи"""
    class Meta:
        model = CalendarTask
        fields = [
            'title',
            'description',
            'task_type',
            'date',
            'time',
            'priority',
            'completed',
            'location',
            'color',
            'is_recurring',
            'recurrence_rule'
        ]
    
    def validate(self, data):
        """Валидация при обновлении"""
        if 'date' in data and data['date'] < datetime.now().date():
            raise serializers.ValidationError({
                "date": "Дата не может быть в прошлом"
            })
        return data


class CalendarStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    high_priority_tasks = serializers.IntegerField()
    today_tasks = serializers.IntegerField()
    upcoming_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()