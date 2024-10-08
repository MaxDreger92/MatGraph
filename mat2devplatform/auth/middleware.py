import os
from dotenv import load_dotenv
from django.http import JsonResponse
import jwt
import hashlib

load_dotenv() 

class APIKeyAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_path = '/api/'

        if request.path.startswith(protected_path):
            api_key = request.META.get('HTTP_API_KEY', '')

            if api_key:
                if self.validate_api_key(api_key):
                    return self.get_response(request)
                else:
                    return self.get_response(request)
                    # return JsonResponse({'error': 'Invalid API key'}, status=403)
            else:
                return self.get_response(request)
                # return JsonResponse({'error': 'API key is missing'}, status=401)

        response = self.get_response(request)
        return response

    def validate_api_key(self, api_key):
        stored_hash = hashlib.sha256(b'secret_key_example').hexdigest()
        return hashlib.sha256(api_key.encode()).hexdigest() == stored_hash

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        api_path = '/api/'
        
        if request.path.startswith(api_path):
            token = request.META.get('HTTP_AUTHORIZATION', '')
            if token:
                token_parts = token.split()
                if len(token_parts) == 2 and token_parts[0].lower() == 'bearer':
                    token = token_parts[1]
                    request.user_token = token
                else:
                    return JsonResponse({'error': 'Invalid token format'}, status=401)
                try:
                    payload = jwt.decode(token, os.getenv('TOKEN_SECRET', 'default_secret'), algorithms=['HS256'])
                    request.user_payload = payload
                except jwt.ExpiredSignatureError:
                    return JsonResponse({'error': 'Token has expired'}, status=401)
                except jwt.InvalidTokenError:
                    return JsonResponse({'error': 'Invalid token'}, status=403)
            else:
                return JsonResponse({'error': 'Authorization header is missing'}, status=401)

        response = self.get_response(request)
        return response
