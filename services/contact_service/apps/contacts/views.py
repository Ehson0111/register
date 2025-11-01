from rest_framework.decorators import api_view,permission_classes
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
    search_fields = ['first_name', 'last_name', 'email', 'company']  # добавил поля для поиска

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):  # ← исправил на RetrieveUpdateDestroyAPIView
    queryset = Contact.objects.all()
    permission_classes = [IsManager]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContactDetailSerializer  # тот же сериализатор для обновления
        return ContactDetailSerializer  # и для просмотра

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def ContactDeleteViews(request,item_id):
    """Удаление клиента из контаков"""
    contact=get_object_or_404(Contact,id=item_id)
    contact.delete()

    return Response({
        'message': 'Item removed from cart successfully'
    }, status=status.HTTP_204_NO_CONTENT)

@api_view(['ADD'])
@permission_classes([IsAuthenticated])
def add_to_contact(request):
    """Добавление товара в корзину"""
    logger.info(f"Add to cart request from user {request.user_id}: {request.data}")
     
    seriazer=add