import os
from dotenv import load_dotenv

load_dotenv()  # загружаем переменные из .env

EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai').lower()
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', None)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', None)
