from typing import List, Dict, Any
import os
import logging
import chromadb
from langchain_chroma import Chroma

logger = logging.getLogger(__name__)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8010"))


class VectorStoreManager:
    def __init__(self, persist_dir: str, embedding_function):
        self.persist_dir = persist_dir
        self.embedding_function = embedding_function
        self.vector_store = None
        self.load()

    def add_texts(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ):
        if self.vector_store is None:
            self.load()
        if len(texts) != len(metadatas) or len(texts) != len(ids):
            raise ValueError("texts, metadatas and ids must have the same length")
        if any(not document_id for document_id in ids) or len(set(ids)) != len(ids):
            raise ValueError("document ids must be non-empty and unique within a batch")
        # Sanitize metadata: ChromaDB 1.x rejects None values
        clean = [
            {k: v for k, v in m.items() if v is not None and isinstance(v, (str, int, float, bool))}
            for m in metadatas
        ]
        # Chroma upserts a document with an existing ID. Stable IDs make a
        # re-index update the place rather than append a duplicate embedding.
        self.vector_store.add_texts(texts=texts, metadatas=clean, ids=ids)

    def similarity_search_with_score(self, query_text: str, k: int, filter=None):
        if self.vector_store is None:
            self.load()
        return self.vector_store.similarity_search_with_score(query_text, k=k, filter=filter)

    def persist(self):
        logger.info("Persist called (ChromaDB server auto-persists)")

    def load(self):
        try:
            client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            self.vector_store = Chroma(
                client=client,
                collection_name="langchain",
                embedding_function=self.embedding_function,
            )
            logger.info(f"Vector store loaded via ChromaDB server at {CHROMA_HOST}:{CHROMA_PORT}")
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            raise

    def clear(self):
        if self.vector_store:
            try:
                client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                client.delete_collection("langchain")
                logger.info("Collection 'langchain' deleted from ChromaDB server")
            except Exception as e:
                logger.error(f"Error clearing vector store: {e}")
