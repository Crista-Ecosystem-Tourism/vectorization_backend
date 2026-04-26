# Crista — Vectorization Backend

Семантический поиск мест: **FastAPI**, эмбеддинги (Hugging Face), **ChromaDB** по HTTP.

## Роль

Загрузка JSON/API, `POST /api/v1/search` для RAG в **ai_agent**. В стеке `CHROMA_HOST`/`CHROMA_PORT` указывают на **сервис** `chromadb`.

## Локально

Сначала **Chroma** на **:8010**, затем:

```bash
cd vectorization_backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## CI/CD

Синк в [crs/vectorization_backend](https://github.com/Crista-Ecosystem-Tourism/crs): [инструкция](https://github.com/Crista-Ecosystem-Tourism/crs/blob/main/docs/CI-CD-SYNC.md), `CRS_SYNC_PAT`.

## Полная документация

[README `crs`](https://github.com/Crista-Ecosystem-Tourism/crs#readme)
