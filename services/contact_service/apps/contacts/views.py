from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import logging
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from .models import Contact
from .serializers import ContactListSerializer, ContactDetailSerializer, AddContactSerializer
from .permissions import IsManager

logger = logging.getLogger(__name__)

class ContactListView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactListSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsManager]
    search_fields = ['first_name', 'last_name', 'email', 'company']

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    permission_classes = [IsManager]
    
    def get_serializer_class(self):
        return ContactDetailSerializer

@api_view(['DELETE'])
@permission_classes([IsManager])  # Исправил на IsManager
def ContactDeleteViews(request, item_id):
    """Удаление контакта"""
    contact = get_object_or_404(Contact, id=item_id)
    contact.delete()

    return Response({
        'message': 'Контакт успешно удален'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])  # Исправил на POST (не ADD)
@permission_classes([IsManager])  # Исправил на IsManager
def add_to_contact(request):
    """Добавление нового контакта"""
    logger.info(f"Add contact request from user {request.user}: {request.data}")
    
    serializer = AddContactSerializer(data=request.data)
    
    if serializer.is_valid():
        contact = serializer.save()
        logger.info(f"Contact created: {contact.id} by user {request.user}")
        
        return Response({
            'message': 'Контакт успешно создан',
            'contact': ContactListSerializer(contact).data
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Contact creation failed: {serializer.errors}")
    return Response({
        'message': 'Ошибка при создании контакта',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)