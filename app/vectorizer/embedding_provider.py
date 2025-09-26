import logging
from typing import List
from app import config

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    def __init__(self, provider_name: str = None, model_name: str = None, **kwargs):
        self.provider_name = provider_name or config.EMBEDDING_PROVIDER
        self.model_name = model_name or config.EMBEDDING_MODEL_NAME
        self.kwargs = kwargs
        self.model = None
        self._init_model()

    def _init_model(self):
        if self.provider_name == 'openai':
            from langchain.embeddings import OpenAIEmbeddings
            init_params = self.kwargs.copy()
            if self.model_name:
                init_params['model'] = self.model_name
            if config.OPENAI_API_KEY:
                init_params['openai_api_key'] = config.OPENAI_API_KEY
            logger.info(f"Используется OpenAI Embeddings модель: {self.model_name}")
            self.model = OpenAIEmbeddings(**init_params)

        elif self.provider_name == 'ollama':
            from langchain_ollama import OllamaEmbeddings
            init_params = self.kwargs.copy()
            if self.model_name:
                init_params['model'] = self.model_name
            if config.OLLAMA_API_URL:
                init_params['base_url'] = config.OLLAMA_API_URL
            logger.info(f"Используется Ollama Embeddings модель: {self.model_name}")
            self.model = OllamaEmbeddings(**init_params)

        elif self.provider_name == 'huggingface':
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                try:
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                except ImportError:
                    from langchain.embeddings import HuggingFaceEmbeddings  # Старый

            init_params = self.kwargs.copy()
            if self.model_name:
                init_params['model_name'] = self.model_name
            # init_params['model_kwargs'] = {'device': 'cuda'}
            init_params['encode_kwargs'] = {
                'normalize_embeddings': True,
                'batch_size': 32
            }
            logger.info(f"Используется HuggingFace Embeddings модель: {self.model_name}")
            self.model = HuggingFaceEmbeddings(**init_params)

        else:
            raise ValueError(f"Неизвестный провайдер эмбеддингов: {self.provider_name}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.model.embed_query(text)
