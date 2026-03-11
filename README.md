# Vectorizer Service

Сервис для загрузки данных, их векторизации и семантического поиска мест.

## Зависимости

- Python 3.13+
- ChromaDB Server (запускается отдельно на порту 8010)

## Запуск

### 1. ChromaDB Server (обязательно первым)

```bash
./venv/Scripts/chroma.exe run \
  --path ./app/vector_store/sochi_rests_and_piter_chroma_db \
  --port 8010 --host 0.0.0.0
```

### 2. Vectorization Backend

```bash
source venv/Scripts/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 3. Загрузка данных (первый раз)

```bash
curl -X POST "http://localhost:8001/api/v1/load/json?filepath=/path/to/data.json"
```

## Конфигурация (.env)

```
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHROMA_HOST=localhost
CHROMA_PORT=8010
NO_PROXY=localhost,127.0.0.1
HTTP_PROXY=
HTTPS_PROXY=
```

## API

- `POST /api/v1/search` — семантический поиск мест
- `POST /api/v1/load/json?filepath=...` — загрузка данных из JSON-файла
- `POST /api/v1/load/api?url=...` — загрузка данных из внешнего API
