import requests
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View


logger=logging.getLogger(__name__)

@method_decorator(csrf_exempt,name='dispatch')
class ProxyView(View):

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"gateway request: {request.method} { request.path}")   
        logger.info(f"headers: {dict(request.headers)}")
        logger.info(f"body: {request.body.decode('utf-8') if request.body else 'no body'}")
        # print(f"{request.method} { request.path}")
        # print(f" {dict(request.headers)}")
        service_name= self.get_service_name(request)
        
        if not service_name:
            logger.error(f'service not found for path:{ request.path}')
        
        print(f" {service_name}")


        service_url=settings.MICROSERVICES.get(service_name)
        print(f" {service_name} {service_url}")

        if not service_url :
            logger.error(f"Service { service_name } not configured")
            return JsonResponse({'eror': f'Servicc {service_name} not configured'}, status=500)


        target_path= self.get_target_path(request)

        target_url= f"{service_url}{target_path}"

        print(f"  target_url {target_url}")

        logger.info(f"Proxying to: {target_path}")

        return self.proxy_request(request, target_url)
    
    def get_service_name(self, request):
        path = request.path
        
        if path.startswith('/api/auth/') or path.startswith('/api/users/'):
            return 'user-service'

        if (path.startswith('/api/contacts/') or 
            path.startswith('/api/services/') or 
            path.startswith('/api/deals/')):
            return 'contact-service'
        return None       

    def get_target_path(self, request):
        path = request.path
        logger.info(f"Proxying to: {path}")
        
        if path.startswith('/api/'):  
            return path
        
        return path
    
    def proxy_request(self,request,target_url):

        try: 
            headers={}

            important_headers=[
                'Authorization', 'Content-Type', 'Accept', 'User-Agent',
                'Accept-Language', 'Accept-Encoding'
            ]

            for header_name in important_headers:
                header_value=request.headers.get(header_name)
                if header_value:
                    print(header_value)
                    headers[header_name]=header_value
            
            logger.info(f"forward headers: {headers}")

            
            data=None
            json_data=None 

            if request.method in ['POST','PUT','PATCH']:
                content_type=request.headers.get('Content-Type','')

                if 'application/json' in content_type:
                    try:
                        if request.body:
                            json_data=json.loads(request.body.decode('utf-8'))
                            logger.info(f"Json data: {json_data}")
                    except (json.JSONDecodeError,UnicodeDecodeError) as e:
                        logger.error(f"failed to parse json: {e}")
                        data=request.body 

                else:
                    data=request.body 
                    logger.info(f"Non-JSON data: {data[:500]}...")  # Логируем первые 500 символов
            # Добавляем query parameters
           
            params=dict(request.GET.items())

            if params:
                logger.info(f"Query params: {params} ")            
            he = {
                'method':request.method,
                'url': target_url,
                'headers':  headers,
                'json':json_data,
                'data' :  data if json_data is None else None,
                'params':params
            }
            print(f"resonse --------------------------------------------------------------------------- ")            
            print(json.dumps(he, indent=2, ensure_ascii=False))

            response =requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=json_data,
                data= data if json_data is None else None,
                params=params,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")
            # Возвращаем ответ
            django_response =HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('content-type', 'application/json')
            )
            
            print(f"django {django_response}")
       
            return django_response

        except requests.exceptions.Timeout:
            logger.error(f"timeout when calling {target_url}")
            return JsonResponse({'error':'service timeout'}, status=504)
        

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error when calling {target_url}:{e}")
            return JsonResponse({'error':'service unavailable'}, status=503)

        except Exception as e :
            logger.error(f"Error proxying request to {target_url} : {e}")
            return JsonResponse({'error':'internal server error'}, status=500)

proxy_view = ProxyView.as_view()
