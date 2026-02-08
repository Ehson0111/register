from rest_framework import serializers
from django.urls import reverse
from .models import ClientDocument


class ClientDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ClientDocument # Переводи модели ClientDocument
        fields = [  #   только эти поля"
            'id', 'client_id', 'original_filename', 'content_type',
            'file_size', 'uploaded_by', 'uploaded_at', 'download_url'
        ]
        read_only_fields = ['id', 'uploaded_at', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(reverse('document-download', kwargs={'pk': obj.pk}))
        return reverse('document-download', kwargs={'pk': obj.pk})


class UploadDocumentSerializer(serializers.Serializer):
    client_id = serializers.IntegerField(required=True)
    file = serializers.FileField(required=True)