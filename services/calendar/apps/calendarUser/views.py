from django.shortcuts import render
from .serializers import (CalendarList)
from rest_framework import generics,status,filters
from .models import CalendarUser
# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsManager

import logging
logger = logging.getLogger(__name__)


class CalendarListView(generics.ListAPIView):
    queryset=CalendarUser.objects.all()
    serializer_class = CalendarList
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    permission_classes = [IsManager ] 

