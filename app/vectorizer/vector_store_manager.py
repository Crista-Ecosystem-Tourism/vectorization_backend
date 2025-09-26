from typing import List, Dict, Any
import logging
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)

class VectorStoreManager:
    def __init__(self, persist_dir: str, embedding_function):
        self.persist_dir = persist_dir
        self.embedding_function = embedding_function
        self.vector_store = None
        self.load()

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        if self.vector_store is None:
            self.load()
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)

    def similarity_search_with_score(self, query_text: str, k: int, filter=None):
        if self.vector_store is None:
            self.load()
        return self.vector_store.similarity_search_with_score(query_text, k=k, filter=filter)

    def persist(self):
        if self.vector_store and hasattr(self.vector_store, "persist"):
            self.vector_store.persist()
            logger.info(f"Vector store saved in {self.persist_dir}")

    def load(self):
        try:
            self.vector_store = Chroma(
                embedding_function=self.embedding_function,
                persist_directory=self.persist_dir
            )
            logger.info("Vector store loaded")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def clear(self):
        import shutil
        import os
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
            logger.info(f"Vector store cleared at {self.persist_dir}")
