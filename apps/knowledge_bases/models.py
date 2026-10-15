from django.conf import settings
from django.db import models

from apps.tenants.models import Tenant


class KnowledgeBase(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='knowledge_bases')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    embedding_provider = models.CharField(max_length=64, default='openai')
    embedding_model = models.CharField(max_length=128, default='text-embedding-3-small')
    embedding_dimensions = models.PositiveIntegerField(default=1536)
    chunk_size = models.PositiveIntegerField(default=500)
    chunk_overlap = models.PositiveIntegerField(default=80)
    top_k = models.PositiveIntegerField(default=5)
    similarity_threshold = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'name'], name='unique_kb_name_per_tenant'),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError('Chunk overlap must be smaller than chunk size.')
        if self.embedding_dimensions <= 0:
            raise ValueError('Embedding dimensions must be positive.')
        if self.top_k <= 0:
            raise ValueError('Top-k must be positive.')
        if self.chunk_size < 100 or self.chunk_size > 4000:
            raise ValueError('Chunk size must be between 100 and 4000 characters.')
