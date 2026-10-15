from rest_framework import serializers

from .models import Document, DocumentChunk


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'knowledge_base', 'title', 'file_name', 'file_type', 'file_size',
            'mime_type', 'status', 'storage_path', 'error_message', 'uploaded_at', 'processed_at',
        ]
        read_only_fields = fields


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_index', 'content', 'start_char', 'end_char']
        read_only_fields = fields
