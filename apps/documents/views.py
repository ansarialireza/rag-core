from pathlib import Path

from django.conf import settings
from django.http import Http404
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.knowledge_bases.models import KnowledgeBase
from core.ingestion.service import detect_file_type, ingest_document, save_uploaded_file

from .models import Document
from .serializers import DocumentSerializer


class DocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        knowledge_base_id = request.data.get('knowledge_base_id')
        uploaded_file = request.FILES.get('file')
        if not knowledge_base_id or not uploaded_file:
            raise serializers.ValidationError('knowledge_base_id and file are required.')

        knowledge_base = KnowledgeBase.objects.filter(tenant=request.tenant, id=knowledge_base_id).first()
        if knowledge_base is None:
            raise Http404('Knowledge base not found or not accessible.')

        file_size = uploaded_file.size
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise serializers.ValidationError(f'File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB.')

        saved_path, _ = save_uploaded_file(uploaded_file, Path(settings.UPLOAD_STORAGE_DIR))
        detected_type = detect_file_type(uploaded_file.name, uploaded_file.read())
        uploaded_file.seek(0)
        document = Document.objects.create(
            knowledge_base=knowledge_base,
            title=uploaded_file.name,
            file_name=uploaded_file.name,
            file_type=detected_type,
            file_size=file_size,
            mime_type=getattr(uploaded_file, 'content_type', '') or 'application/octet-stream',
            storage_path=saved_path,
            status=Document.STATUS_PENDING,
        )

        try:
            ingest_document(document, uploaded_file.read())
        except Exception as exc:
            return Response(
                {'detail': 'Document ingestion failed.', 'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        knowledge_base_id = self.request.query_params.get('knowledge_base_id')
        queryset = Document.objects.filter(knowledge_base__tenant=self.request.tenant)
        if knowledge_base_id:
            queryset = queryset.filter(knowledge_base_id=knowledge_base_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
