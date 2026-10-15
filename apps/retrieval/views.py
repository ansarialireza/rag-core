from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.documents.models import DocumentChunk
from apps.knowledge_bases.models import KnowledgeBase
from core.embeddings.provider import OpenAICompatibleEmbeddingProvider, get_embedding_settings

from .serializers import RetrievalRequestSerializer


class RetrievalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RetrievalRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        knowledge_base = KnowledgeBase.objects.filter(tenant=request.tenant, id=data['knowledge_base_id']).first()
        if knowledge_base is None:
            return Response({'detail': 'Knowledge base not found or not accessible.'}, status=status.HTTP_404_NOT_FOUND)

        query_embedding = OpenAICompatibleEmbeddingProvider(
            get_embedding_settings(
                provider=knowledge_base.embedding_provider,
                model=knowledge_base.embedding_model,
                dimensions=knowledge_base.embedding_dimensions,
            )
        ).embed_text(data['query'])

        chunks = list(
            DocumentChunk.objects.filter(knowledge_base=knowledge_base).order_by('-id')
        )

        scored = []
        for chunk in chunks:
            if chunk.embedding is None:
                continue
            embedding = chunk.embedding if isinstance(chunk.embedding, list) else chunk.embedding
            if not isinstance(embedding, list):
                continue
            dot = sum(a * b for a, b in zip(query_embedding, embedding))
            norm_query = (sum(a * a for a in query_embedding)) ** 0.5
            norm_chunk = (sum(b * b for b in embedding)) ** 0.5
            if norm_query == 0 or norm_chunk == 0:
                score = 0.0
            else:
                score = dot / (norm_query * norm_chunk)
            if score >= data.get('similarity_threshold', settings.DEFAULT_SIMILARITY_THRESHOLD):
                scored.append({
                    'chunk_id': chunk.id,
                    'document_id': chunk.document_id,
                    'content': chunk.content,
                    'score': score,
                    'chunk_index': chunk.chunk_index,
                    'start_char': chunk.start_char,
                    'end_char': chunk.end_char,
                    'document_title': chunk.document.title,
                })

        scored.sort(key=lambda item: item['score'], reverse=True)
        return Response({'results': scored[:data['top_k']]}, status=status.HTTP_200_OK)
