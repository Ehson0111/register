from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import StreamingHttpResponse, Http404
from django.conf import settings
from minio import Minio
from minio.error import S3Error
from .models import ClientDocument
from .serializers import ClientDocumentSerializer, UploadDocumentSerializer
import uuid


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated] # 
    def post(self, request):
        serializer = UploadDocumentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_obj = serializer.validated_data['file']
        client_id = serializer.validated_data['client_id']

        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        bucket = settings.MINIO_BUCKET
#         Bucket (корзина/ведро) — это как папка верхнего уровня, контейнер для файлов.

# python
# bucket = settings.MINIO_BUCKET  # Например: "client-documents"
# if not minio_client.bucket_exists(bucket):  
#     minio_client.make_bucket(bucket)

        if not minio_client.bucket_exists(bucket):  
            minio_client.make_bucket(bucket)

        # Уникальное имя объекта
        object_name = f"{client_id}/{uuid.uuid4()}_{file_obj.name}"

        try:
            # Загрузка в MinIO
            with file_obj.open('rb') as data:
                minio_client.put_object(
                    bucket_name=bucket,
                    object_name=object_name,
                    data=data,
                    length=file_obj.size,
                    content_type=file_obj.content_type or 'application/octet-stream',
                )

            document = ClientDocument.objects.create(
                client_id=client_id,
                original_filename=file_obj.name,
                object_name=object_name,
                content_type=file_obj.content_type or 'application/octet-stream',
                file_size=file_obj.size,
                uploaded_by=request.user.id,
            )

            return Response(ClientDocumentSerializer(document, context={'request': request}).data,
                            status=status.HTTP_201_CREATED)

        except S3Error as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, client_id):
        documents = ClientDocument.objects.filter(client_id=client_id)
        serializer = ClientDocumentSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)
    
              # Генератор для стриминга файла по чанкам (по 1 МБ)
            
            
            # Допустим, файл 2.7 МБ
# file_stream() вызывается Django

# 1-й вызов: yield первые 1 МБ → отдаём клиенту
# 2-й вызов: yield вторые 1 МБ → отдаём клиенту  
# 3-й вызов: yield последние 0.7 МБ → отдаём клиенту
# 4-й вызов: StopIteration → конец файла
# finally: закрываем соединение
class DocumentDownloadView(APIView):
    """
    Скачивание документа по ID.
    Возвращает файл из MinIO с правильным именем, MIME-типом и размером.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Получаем метаданные документа из БД
        try:
            document = ClientDocument.objects.get(pk=pk)
        except ClientDocument.DoesNotExist:
            raise Http404("Документ не найден")

        # Инициализируем клиент MinIO
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        try:
            # Проверяем существование объекта и получаем метаданные (включая размер)
            stat = minio_client.stat_object(settings.MINIO_BUCKET, document.object_name)
            # Получаем объект для стриминга
            obj = minio_client.get_object(settings.MINIO_BUCKET, document.object_name)
   
            def file_stream():
                try:
                    for data in obj.stream(1024 * 1024):
                        if data:
                            yield data
                finally:
                    obj.close()
                    obj.release_conn()
            response = StreamingHttpResponse(
                streaming_content=file_stream(),
                content_type=document.content_type or 'application/octet-stream'
            )
            # Устанавливаем заголовки для скачивания
            response['Content-Disposition'] = f'attachment; filename="{document.original_filename}"'
            response['Content-Length'] = stat.size
            response['Accept-Ranges'] = 'bytes'  # Поддержка range-запросов (опционально)
            return response

        except S3Error as e:
            if e.code == 'NoSuchKey':
                raise Http404("Файл не найден в хранилище")
            return Response({"error": f"Ошибка MinIO: {str(e)}"}, status=500)
        except Exception as e:
            return Response({"error": f"Неизвестная ошибка: {str(e)}"}, status=500)