import json
import logging

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ProxyView(View):

    def dispatch(self, request, *args, **kwargs):
        logger.info("gateway request: %s %s", request.method, request.path)
        service_name = self.get_service_name(request)
        if not service_name:
            logger.error('service not found for path: %s', request.path)

        service_url = settings.MICROSERVICES.get(service_name)
        if not service_url:
            logger.error("Service %s not configured", service_name)
            return JsonResponse({'error': f'Service {service_name} not configured'}, status=500)

        target_path = self.get_target_path(request)
        target_url = f"{service_url}{target_path}"
        return self.proxy_request(request, target_url)

    def get_service_name(self, request):
        path = request.path

        if path.startswith('/api/auth/') or path.startswith('/api/users/'):
            return 'user-service'
        if (path.startswith('/api/contacts/') or
            path.startswith('/api/deal-stages/') or
            path.startswith('/api/services/') or
            path.startswith('/api/deals/') or
            path.startswith('/api/audit-trail/')):
            return 'contact-service'

        if path.startswith('/api/marketing/'):
            return 'marketing'

        if path.startswith('/api/documents/'):
            return 'documents'

        if path.startswith('/api/chat/'):
            return 'chat-service'

        if path.startswith('/api/payment/'):
            return 'payments'

        if path.startswith('/api/tasks'):
            return 'tasks-service'
        return None

    def get_target_path(self, request):
        return request.path

    def proxy_request(self, request, target_url):
        try:
            headers = {}
            important_headers = [
                'Authorization', 'Content-Type', 'Accept', 'User-Agent',
                'Accept-Language', 'Accept-Encoding',
            ]

            for header_name in important_headers:
                header_value = request.headers.get(header_name)
                if header_value:
                    headers[header_name] = header_value

            data = None
            json_data = None

            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    try:
                        if request.body:
                            json_data = json.loads(request.body.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        logger.error("failed to parse json: %s", exc)
                        data = request.body
                else:
                    data = request.body

            params = dict(request.GET.items())

            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=json_data,
                data=data if json_data is None else None,
                params=params,
                stream=True,
                timeout=60,
            )

            django_response = StreamingHttpResponse(
                streaming_content=response.iter_content(chunk_size=8192),
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/octet-stream'),
            )

            for header, value in response.headers.items():
                if header.lower() not in [
                    'content-length', 'transfer-encoding', 'content-encoding', 'connection',
                    'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'upgrade',
                ]:
                    django_response[header] = value

            if 'Content-Disposition' in response.headers:
                django_response['Content-Disposition'] = response.headers['Content-Disposition']

            return django_response

        except requests.exceptions.Timeout:
            logger.error("timeout when calling %s", target_url)
            return JsonResponse({'error': 'service timeout'}, status=504)

        except requests.exceptions.ConnectionError as exc:
            logger.error("connection error when calling %s: %s", target_url, exc)
            return JsonResponse({'error': 'service unavailable'}, status=503)

        except Exception as exc:
            logger.error("error proxying request to %s: %s", target_url, exc)
            return JsonResponse({'error': 'internal server error'}, status=500)


proxy_view = ProxyView.as_view()

