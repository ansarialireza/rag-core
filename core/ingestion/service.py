import hashlib
import io
import os
import zipfile
from datetime import datetime
from pathlib import Path

import docx
from django.conf import settings
from pypdf import PdfReader

from apps.documents.models import Document, DocumentChunk
from core.chunking.splitter import chunk_text
from core.embeddings.provider import OpenAICompatibleEmbeddingProvider, get_embedding_settings


def detect_file_type(file_name: str, file_bytes: bytes):
    lower_name = file_name.lower()
    if lower_name.endswith('.pdf') or file_bytes.startswith(b'%PDF'):
        return 'pdf'
    if lower_name.endswith('.docx') or (file_bytes.startswith(b'PK') and _is_docx_bytes(file_bytes)):
        return 'docx'
    if lower_name.endswith('.md') or lower_name.endswith('.markdown') or lower_name.endswith('.txt'):
        return 'text'
    raise ValueError('Unsupported file type.')


def _is_docx_bytes(file_bytes: bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            names = set(zf.namelist())
            return 'word/document.xml' in names
    except Exception:
        return False


def extract_text(file_name: str, file_bytes: bytes):
    file_type = detect_file_type(file_name, file_bytes)
    if file_type == 'pdf':
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ''
            pages.append(text)
        return '\n'.join(pages)
    if file_type == 'docx':
        doc = docx.Document(io.BytesIO(file_bytes))
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)
    return file_bytes.decode('utf-8', errors='strict')


def save_uploaded_file(uploaded_file, upload_dir: Path):
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_hash = hashlib.sha256(uploaded_file.read()).hexdigest()
    uploaded_file.seek(0)
    target_path = upload_dir / f'{file_hash}_{os.path.basename(uploaded_file.name)}'
    with open(target_path, 'wb') as fh:
        for chunk in uploaded_file.chunks():
            fh.write(chunk)
    return str(target_path), file_hash


def ingest_document(document: Document, file_bytes: bytes):
    knowledge_base = document.knowledge_base
    document.status = Document.STATUS_PROCESSING
    document.save(update_fields=['status'])

    try:
        text = extract_text(document.file_name, file_bytes).strip()
        document.extracted_text = text
        chunks = chunk_text(text, knowledge_base.chunk_size, knowledge_base.chunk_overlap)
        if not chunks:
            document.status = Document.STATUS_COMPLETED
            document.processed_at = datetime.now()
            document.save(update_fields=['status', 'processed_at', 'extracted_text'])
            return

        settings_obj = get_embedding_settings(
            provider=knowledge_base.embedding_provider,
            model=knowledge_base.embedding_model,
            dimensions=knowledge_base.embedding_dimensions,
        )
        provider = OpenAICompatibleEmbeddingProvider(settings_obj)
        embeddings = provider.embed_batch([chunk['content'] for chunk in chunks])

        DocumentChunk.objects.filter(document=document).delete()
        created_chunks = []
        for chunk_meta, embedding in zip(chunks, embeddings):
            created_chunks.append(DocumentChunk(
                document=document,
                knowledge_base=knowledge_base,
                chunk_index=chunk_meta['index'],
                content=chunk_meta['content'],
                start_char=chunk_meta['start_char'],
                end_char=chunk_meta['end_char'],
                embedding=embedding,
            ))
        DocumentChunk.objects.bulk_create(created_chunks)
        document.status = Document.STATUS_COMPLETED
        document.processed_at = datetime.now()
        document.save(update_fields=['status', 'processed_at', 'extracted_text'])
    except Exception as exc:
        document.status = Document.STATUS_FAILED
        document.error_message = str(exc)
        document.processed_at = datetime.now()
        document.save(update_fields=['status', 'processed_at', 'error_message'])
        raise
