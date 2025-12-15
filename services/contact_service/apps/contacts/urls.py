# from django.urls import path
# from . import views 

# urlpatterns = [
#     path('contacts/', views.ContactListView.as_view(), name='contact-list'),
#     path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),  
#     path('contacts/remove/<int:item_id>/', views.ContactDeleteViews, name='contact-delete'),
#     path('contacts/add/', views.add_to_contact, name='contact-add')  # Добавление контакта
# ]

from django.urls import path
from . import views 

urlpatterns = [
    # Контакты
    path('contacts/', views.ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),  
    path('contacts/remove/<int:item_id>/', views.ContactDeleteViews, name='contact-delete'),
    path('contacts/add/', views.add_to_contact, name='contact-add'),
    
    # Услуги
    path('services/', views.ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    
    # Сделки
    path('deals/', views.DealListView.as_view(), name='deal-list'),
    path('deals/<int:pk>/', views.DealDetailView.as_view(), name='deal-detail'),
    path('contacts/<int:contact_id>/deals/stats/', views.contact_deals_stats, name='contact-deals-stats'),
    path('deals/<int:deal_id>/change-status/', views.change_deal_status, name='change-deal-status'), 


     
    # НОВЫЕ URL - безопасное добавление
    path('services/add/', views.create_service, name='service-add'),
    path('services/remove/<int:service_id>/', views.delete_service, name='service-delete'),
    path('deals/add/', views.create_deal, name='deal-add'),
    path('deals/remove/<int:deal_id>/', views.delete_deal, name='deal-delete'),
    path('contacts/select/', views.get_contacts_for_select, name='contacts-select'),
    path('services/select/', views.get_services_for_select, name='services-select'),
]