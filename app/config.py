import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # загружаем переменные из .env

EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'ollama').lower()
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'paraphrase-multilingual')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_STORE_NAME = os.getenv('VECTOR_STORE_NAME', 'sochi_rests_and_piter_chroma_db')
VECTOR_STORE_DIR = os.path.join(BASE_DIR, 'vector_store', VECTOR_STORE_NAME)
print(f"VECTOR_STORE_DIR: {VECTOR_STORE_DIR}")

TEST_EMBEDDING_PROVIDER = os.getenv('TEST_EMBEDDING_PROVIDER', EMBEDDING_PROVIDER).lower()
TEST_EMBEDDING_MODEL_NAME = os.getenv('TEST_EMBEDDING_MODEL_NAME', EMBEDDING_MODEL_NAME)


def import_admin_token() -> str | None:
    value = (os.getenv("VECTORIZATION_ADMIN_TOKEN") or "").strip()
    return value or None


def import_directory() -> Path:
    return Path(os.getenv("VECTORIZATION_IMPORT_DIR", "/app/data/import")).resolve()


def import_url_allowlist() -> frozenset[str]:
    raw = os.getenv("VECTORIZATION_IMPORT_URL_ALLOWLIST", "")
    return frozenset(item.strip().lower() for item in raw.split(",") if item.strip())


def import_max_bytes() -> int:
    try:
        return min(max(int(os.getenv("VECTORIZATION_IMPORT_MAX_BYTES", "5242880")), 1024), 50 * 1024 * 1024)
    except ValueError:
        return 5 * 1024 * 1024


def import_timeout_seconds() -> float:
    try:
        return min(max(float(os.getenv("VECTORIZATION_IMPORT_TIMEOUT_SECONDS", "10")), 1.0), 60.0)
    except ValueError:
        return 10.0
