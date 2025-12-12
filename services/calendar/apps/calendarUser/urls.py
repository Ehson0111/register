from django.urls import path
from . import views

urlpatterns = [
        path('calendar/', views.CalendarListView.as_view(), name='calendar-list')

]

#wwwwwe