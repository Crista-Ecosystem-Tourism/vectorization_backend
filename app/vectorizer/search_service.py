from typing import List, Dict, Any
from app.vectorizer.vector_store_manager import VectorStoreManager
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vector_store_manager = vector_store_manager

    def search(self, query: str, k: int = 10, distance_threshold: float = 1.0,
               metadata_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            results = self.vector_store_manager.similarity_search_with_score(
                query, k=k*2, filter=metadata_filter
            )
            filtered = []
            for doc, distance in results:
                distance = float(distance)
                similarity = max(0.0, 1.0 - distance)
                if distance <= distance_threshold:
                    data = {
                        **(doc.metadata or {}),
                        "distance": distance,
                        "relevance_score": similarity,
                        "page_content": getattr(doc, "page_content", "")
                    }
                    filtered.append(data)
            filtered.sort(key=lambda x: x["relevance_score"], reverse=True)
            return filtered[:k]

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
