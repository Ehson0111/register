from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Contact
from .serializers import ContactListSerializer, ContactDetailSerializer
from .permissions import IsManager

class ContactListView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactListSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsManager]
    search_fields = ['first_name', 'last_name', 'email', 'company']  # добавил поля для поиска

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):  # ← исправил на RetrieveUpdateDestroyAPIView
    queryset = Contact.objects.all()
    permission_classes = [IsManager]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContactDetailSerializer  # тот же сериализатор для обновления
        return ContactDetailSerializer  # и для просмотра