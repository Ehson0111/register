from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, UserProfile
from .serializers import (
    UserWithProfileSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer
)

import logging
logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info(f"Registration attempt with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email}")
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Registration validation errors: {serializer.errors}")
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserWithProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
