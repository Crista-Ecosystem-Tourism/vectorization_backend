import os
from dotenv import load_dotenv

load_dotenv()  # загружаем переменные из .env

EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai').lower()
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', None)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VECTOR_STORE_NAME = 'sochi_rests_and_piter_chroma_db'
VECTOR_STORE_DIR = os.path.join(BASE_DIR, 'vector_store', VECTOR_STORE_NAME)
print(f"VECTOR_STORE_DIR: {VECTOR_STORE_DIR}")
