from rest_framework import serializers 
from .models import Applications, ApplicationAudit 

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


class ApplicationAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationAudit
        fields = ["id", "application", "actor", "action", "metadata", "created_at"]