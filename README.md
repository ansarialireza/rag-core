# RAG Core

A lightweight, production-oriented Django REST API for multi-tenant knowledge ingestion and retrieval.

## Quick start

1. Create a local environment file:
   ```bash
   cp .env.example .env
   ```
2. Start PostgreSQL and the API:
   ```bash
   docker compose up --build
   ```
3. Apply migrations (handled automatically by the container startup command).
4. Create an API client and use the `Authorization: Api-Key <key>` header.

## Environment variables

See `.env.example` for the required configuration values.

## Main APIs

- `POST /api/v1/knowledge-bases/`
- `GET /api/v1/knowledge-bases/`
- `GET /api/v1/knowledge-bases/{id}/`
- `PATCH /api/v1/knowledge-bases/{id}/`
- `DELETE /api/v1/knowledge-bases/{id}/`
- `POST /api/v1/documents/upload/`
- `GET /api/v1/documents/`
- `GET /api/v1/documents/{id}/`
- `DELETE /api/v1/documents/{id}/`
- `POST /api/v1/retrieval/search/`

## Notes

- Tenant isolation is enforced by API key ownership.
- Documents are processed synchronously in the initial implementation.
- This release is intentionally simple and not a complete replacement for a production-ready enterprise platform.
