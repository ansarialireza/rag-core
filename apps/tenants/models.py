import hashlib
import secrets

from django.conf import settings
from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ApiClient(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='api_clients')
    name = models.CharField(max_length=255)
    key_prefix = models.CharField(max_length=24, default='rag_')
    key_hash = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.tenant.name})'

    @classmethod
    def generate_key(cls, tenant_name: str):
        prefix = getattr(settings, 'API_KEY_PREFIX', 'rag_')
        token = secrets.token_urlsafe(getattr(settings, 'API_KEY_LENGTH', 32))
        raw_key = f'{prefix}{token}'
        return raw_key, hashlib.sha256(raw_key.encode()).hexdigest()

    @classmethod
    def hash_key(cls, raw_key: str):
        return hashlib.sha256(raw_key.encode()).hexdigest()
