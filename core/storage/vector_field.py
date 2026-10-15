from django.conf import settings
from django.db import models

try:
    from pgvector.django import VectorField
except Exception:  # pragma: no cover
    VectorField = None


if VectorField and settings.DATABASES['default']['ENGINE'].endswith('postgresql'):
    EmbeddingVectorField = VectorField
else:
    EmbeddingVectorField = models.JSONField
