import math
from dataclasses import dataclass

import httpx
from django.conf import settings


@dataclass(frozen=True)
class EmbeddingSettings:
    provider: str
    model: str
    api_url: str
    api_key: str
    dimensions: int
    timeout_seconds: int = 30
    batch_size: int = 16


class EmbeddingProviderError(RuntimeError):
    pass


class EmbeddingDimensionError(EmbeddingProviderError):
    pass


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, settings_obj: EmbeddingSettings):
        self.settings = settings_obj

    def _local_fallback_embedding(self, text: str):
        if not text:
            return [0.0] * self.settings.dimensions
        digest = sum(ord(ch) for ch in text)
        vector = []
        for i in range(self.settings.dimensions):
            value = ((digest * (i + 1)) % 97) / 97.0
            vector.append(value)
        return vector

    def embed_batch(self, texts):
        if not texts:
            return []

        if not self.settings.api_key:
            return [self._local_fallback_embedding(text) for text in texts]

        vectors = []
        for i in range(0, len(texts), self.settings.batch_size):
            batch = texts[i:i + self.settings.batch_size]
            response = httpx.post(
                self.settings.api_url,
                headers={
                    'Authorization': f'Bearer {self.settings.api_key}',
                    'Content-Type': 'application/json',
                },
                json={'model': self.settings.model, 'input': batch},
                timeout=self.settings.timeout_seconds,
            )
            if response.status_code >= 400:
                payload = response.text
                raise EmbeddingProviderError(f'Embedding request failed ({response.status_code}): {payload[:300]}')

            payload = response.json()
            data = payload.get('data')
            if not isinstance(data, list):
                raise EmbeddingProviderError('Embedding provider returned no usable data.')

            batch_vectors = []
            for item in data:
                embedding = item.get('embedding')
                if not isinstance(embedding, list):
                    raise EmbeddingProviderError('Embedding item missing vector data.')
                if len(embedding) != self.settings.dimensions:
                    raise EmbeddingDimensionError(
                        f'Embedding dimension mismatch: expected {self.settings.dimensions}, got {len(embedding)}.'
                    )
                batch_vectors.append(embedding)
            if len(batch_vectors) != len(batch):
                raise EmbeddingProviderError('Embedding batch size mismatch.')
            vectors.extend(batch_vectors)
        return vectors

    def embed_text(self, text: str):
        if not text:
            return []
        return self.embed_batch([text])[0]


def get_embedding_settings(provider: str | None = None, model: str | None = None, api_url: str | None = None, api_key: str | None = None, dimensions: int | None = None):
    provider = provider or settings.EMBEDDING_PROVIDER
    model = model or settings.EMBEDDING_MODEL
    api_url = api_url or settings.EMBEDDING_API_URL
    api_key = api_key or settings.EMBEDDING_API_KEY
    dimensions = dimensions or settings.EMBEDDING_DIMENSIONS
    return EmbeddingSettings(
        provider=provider,
        model=model,
        api_url=api_url,
        api_key=api_key,
        dimensions=dimensions,
        timeout_seconds=settings.EMBEDDING_TIMEOUT_SECONDS,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
    )


def cosine_similarity(vector_a, vector_b):
    if not vector_a or not vector_b:
        return 0.0
    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
