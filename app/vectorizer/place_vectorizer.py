from typing import List, Dict, Any
from .embedding_provider import EmbeddingProvider
from .vector_store_manager import VectorStoreManager
from .text_preparer import TextPreparer
from .search_service import SearchService
import logging

logger = logging.getLogger(__name__)

class PlaceVectorizer:
    def __init__(self, persist_dir: str,
                 embedding_provider_name: str,
                 embedding_model_name: str):
        self.embedding_provider = EmbeddingProvider(embedding_provider_name, embedding_model_name)
        self.text_preparer = TextPreparer()
        self.vector_store_manager = VectorStoreManager(persist_dir, self.embedding_provider.model)
        self.search_service = SearchService(self.vector_store_manager)
        logger.info(f"PlaceVectorizer created with provider {embedding_provider_name}, model {embedding_model_name}")

    def build_and_store_embeddings(self, places: List[Dict[str, Any]], batch_size: int = 50):
        texts = [self.text_preparer.prepare_text(p) for p in places]
        metadatas = [self.text_preparer.create_metadata(p) for p in places]
        self.vector_store_manager.add_texts(texts, metadatas)
        self.vector_store_manager.persist()
        logger.info(f"Embeddings built and stored for {len(places)} places")

    def search(self, query: str, k: int = 5, distance_threshold: float = 0.7, metadata_filter: Dict[str, Any] = None):
        return self.search_service.search(query, k, distance_threshold, metadata_filter)

    def clear_index(self):
        self.vector_store_manager.clear()
