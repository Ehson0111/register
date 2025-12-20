from django.db import models

class CalendarTask(models.Model):
    """Задача в календаре менеджера"""
    
    # Типы задач
    TYPE_MEETING = 'meeting'
    TYPE_TASK = 'task'
    TYPE_REMINDER = 'reminder'
    TYPE_DEADLINE = 'deadline'
    
    TYPE_CHOICES = [
        (TYPE_MEETING, 'Встреча'),
        (TYPE_TASK, 'Задача'),
        (TYPE_REMINDER, 'Напоминание'),
        (TYPE_DEADLINE, 'Дедлайн'),
    ]
    
    # Приоритеты
    PRIORITY_HIGH = 'high'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_LOW = 'low'
    
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'Высокий'),
        (PRIORITY_MEDIUM, 'Средний'),
        (PRIORITY_LOW, 'Низкий'),
    ]
    
    # Основные поля
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    task_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default=TYPE_TASK,
        verbose_name="Тип задачи"
    )
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(null=True, blank=True, verbose_name="Время")
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default=PRIORITY_MEDIUM,
        verbose_name="Приоритет"
    )
    completed = models.BooleanField(default=False, verbose_name="Выполнено")
    
    # Привязка к менеджеру - ТОЛЬКО ID (обязательное поле)
    manager_id = models.IntegerField(verbose_name="ID менеджера")
    
    # Дополнительные поля
    location = models.CharField(max_length=200, blank=True, verbose_name="Место")
    color = models.CharField(max_length=7, default='#4CAF50', verbose_name="Цвет")
    
    # Для повторяющихся задач
    is_recurring = models.BooleanField(default=False, verbose_name="Повторяющаяся")
    recurrence_rule = models.CharField(max_length=100, blank=True, verbose_name="Правило повторения")
    
    # Автоматические поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'time']
        verbose_name = "Задача календаря"
        verbose_name_plural = "Задачи календаря"
        indexes = [
            models.Index(fields=['manager_id', 'date']),
            models.Index(fields=['manager_id', 'completed']),
            models.Index(fields=['date', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.date}) - Manager #{self.manager_id}"
    
    def get_priority_display(self):
        """Получить отображаемое значение приоритета"""
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)
    
    def get_task_type_display(self):
        """Получить отображаемое значение типа задачи"""
        return dict(self.TYPE_CHOICES).get(self.task_type, self.task_type)