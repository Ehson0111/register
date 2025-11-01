# from rest_framework import generics, filters
# from rest_framework.permissions import IsAuthenticated
# from django_filters.rest_framework import DjangoFilterBackend

# from .models import Contact
# from .serializers import ContactSerializer
# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
# from .models import Contact
# from .serializers import ContactSerializer
# from .permissions import IsManager

# class ContactViewSet(viewsets.ModelViewSet):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     # Доступ только аутентифицированным менеджерам
#     permission_classes = [IsAuthenticated, IsManager]
    
# class ContactListCreateView(generics.ListCreateAPIView):
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = Contact.objects.all()
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['status', 'assigned_manager_id', 'tags']
#     search_fields = ['full_name', 'email', 'phone', 'company']
#     ordering_fields = ['created_at', 'full_name']

#     def get_queryset(self):
#         """
#         Пользователь видит только свои контакты.
#         """
#         return Contact.objects.filter(owner_id=self.request.user.id)

#     def perform_create(self, serializer):
#         """
#         Автоматически заполняем владельца из токена.
#         """
#         serializer.save(owner_id=self.request.user.id)


# class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = ContactSerializer
#     queryset = Contact.objects.all()
#     # permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Contact.objects.filter(owner_id=self.request.user.id)
from rest_framework import viewsets,generics,status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Contact
from .serializers import ContactListSerializer
from .permissions import IsManager, IsOwner

class ContactlistView(generics.ListCreateAPIView):
    queryset= Contact.objects.all()
    serializer_class=ContactListSerializer
    filter_backends=[filters.SearchFilter]
    # search_fields = ['first_name', 'last_name']
    



class ContactViewSet(generics.CreateAPIView):
    serializer_class = ContactListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
   
    # if request.role=

    def get_queryset(self):
        """
        Пользователь видит только свои контакты.
        Менеджеры видят все контакты.
        """
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Contact.objects.all()
        return Contact.objects.filter(owner=user)

    # def get_permissions(self):
    #     """
    #     Разные права для разных действий.
    #     """
    #     if self.action in ['update', 'partial_update', 'destroy']:
    #         return [IsAuthenticated(), IsOwner()]
    #     elif self.action in ['create']:
    #         return [IsAuthenticated()]
    #     return super().get_permissions()

    def perform_create(self, serializer):
        """
        Автоматически назначаем владельца при создании.
        """
        serializer.save(owner=self.request.user)