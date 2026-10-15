from rest_framework import serializers

from .models import KnowledgeBase


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'embedding_provider', 'embedding_model',
            'embedding_dimensions', 'chunk_size', 'chunk_overlap', 'top_k',
            'similarity_threshold', 'created_at', 'updated_at', 'tenant',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tenant']

    def validate(self, attrs):
        chunk_size = attrs.get('chunk_size', self.instance.chunk_size if self.instance else 500)
        chunk_overlap = attrs.get('chunk_overlap', self.instance.chunk_overlap if self.instance else 80)
        if chunk_overlap >= chunk_size:
            raise serializers.ValidationError({'chunk_overlap': 'Chunk overlap must be smaller than chunk size.'})
        if chunk_size < 100 or chunk_size > 4000:
            raise serializers.ValidationError({'chunk_size': 'Chunk size must be between 100 and 4000 characters.'})
        top_k = attrs.get('top_k', self.instance.top_k if self.instance else 5)
        if top_k <= 0:
            raise serializers.ValidationError({'top_k': 'Top-k must be greater than zero.'})
        return attrs
