import hashlib

from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ApiClient


class ApiKeyAuthentication(authentication.BaseAuthentication):
    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            raise AuthenticationFailed('Authorization header must use the Api-Key scheme.')

        raw_key = parts[1]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        try:
            api_client = ApiClient.objects.select_related('tenant').get(key_hash=key_hash, is_active=True)
        except ApiClient.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        request.tenant = api_client.tenant
        request.user = api_client
        api_client.is_authenticated = True
        api_client.is_anonymous = False
        return (api_client, None)

    def authenticate_header(self, request):
        return 'Api-Key'
