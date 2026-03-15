from rest_framework import serializers 
from .models import Applications 

class ApplicationsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications 
        fields = [
            'id',
            'subject',
            'date',
            'text',
            'sender_email',
            'is_processed',
            'created_at',
            'updated_at',
        ] 
        read_only_fields = ['created_at', 'updated_at']