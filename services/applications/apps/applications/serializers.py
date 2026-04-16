from rest_framework import serializers 
from .models import Applications, ApplicationAudit, MailboxEmail 

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


class MailboxEmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailboxEmail
        fields = [
            "id",
            "external_id",
            "message_id",
            "subject",
            "sender_name",
            "sender_email",
            "recipients",
            "date",
            "preview",
            "is_read",
            "is_important",
            "in_inbox",
            "in_sent",
            "in_trash",
            "primary_folder",
        ]


class MailboxEmailDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailboxEmail
        fields = [
            "id",
            "external_id",
            "message_id",
            "subject",
            "sender_name",
            "sender_email",
            "recipients",
            "cc",
            "date",
            "body_text",
            "body_html",
            "preview",
            "is_read",
            "is_important",
            "in_inbox",
            "in_sent",
            "in_trash",
            "primary_folder",
            "raw_flags",
            "created_at",
            "updated_at",
        ]


class SendMailboxEmailSerializer(serializers.Serializer):
    to = serializers.CharField(max_length=1000)
    subject = serializers.CharField(max_length=500)
    body = serializers.CharField()
    cc = serializers.CharField(max_length=1000, required=False, allow_blank=True)