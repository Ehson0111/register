from django.urls import path
from . import views 

urlpatterns = [
    path('contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),  
    path('contacts/remove/<int:item_id>/', views.ContactDeleteViews, name='contact-delete'),
    path('contacts/add/', views.add_to_contact, name='contact-add')  # Добавление контакта
]