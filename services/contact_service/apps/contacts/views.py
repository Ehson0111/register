from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Contact
from .serializers import ContactSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contact
from .serializers import ContactSerializer
from .permissions import IsManager

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # Доступ только аутентифицированным менеджерам
    permission_classes = [IsAuthenticated, IsManager]
    
class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    queryset = Contact.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_manager_id', 'tags']
    search_fields = ['full_name', 'email', 'phone', 'company']
    ordering_fields = ['created_at', 'full_name']

    def get_queryset(self):
        """
        Пользователь видит только свои контакты.
        """
        return Contact.objects.filter(owner_id=self.request.user.id)

    def perform_create(self, serializer):
        """
        Автоматически заполняем владельца из токена.
        """
        serializer.save(owner_id=self.request.user.id)


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(owner_id=self.request.user.id)
