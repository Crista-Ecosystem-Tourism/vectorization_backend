import os
from app.vectorizer.place_vectorizer import PlaceVectorizer

class SearchService:
    def __init__(self, vectorizer: PlaceVectorizer):
        self.vectorizer = vectorizer

    @staticmethod
    def search_by_text(
        vectorizer: PlaceVectorizer,
        query_text: str,
        k: int = 5,
        distance_threshold: float = 1.2
    ):
        results = vectorizer.search(query_text, k, distance_threshold=distance_threshold)
        return results

    @staticmethod
    def search_by_text_and_metadata(vectorizer: PlaceVectorizer, query_text: str, metadata_filter: dict, k: int = 5):
        results = vectorizer.search(query_text, k, metadata_filter=metadata_filter, distance_threshold=1.2)
        return results

    @staticmethod
    def search_by_text_and_distance_threshold(vectorizer: PlaceVectorizer, query_text: str, distance_threshold: float, k: int = 5):
        results = vectorizer.search(query_text, k, distance_threshold=distance_threshold)
        return results
