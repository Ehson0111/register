from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.CalendarTaskViewSet, basename='calendar-tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('daily/', views.DailyTasksView.as_view(), name='daily-tasks'),
    path('monthly/', views.MonthlyCalendarView.as_view(), name='monthly-calendar'),
]