from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.schemas.place import (
    QueryRequestWithFilters,
    QueryResponse,
    QueryResponseItem
)
from app.services.search import SearchService
from app.utils.logger import get_logger
from app.dependencies.vectorizer import get_vectorizer

router = APIRouter()
logger = get_logger(__name__)

@router.post("/search", response_model=QueryResponse)
def search_places(query: QueryRequestWithFilters, vectorizer=Depends(get_vectorizer)):
    logger.info(f"Получен запрос на поиск: {query.query} (top {query.top_k})")
    try:
        metadata_filter_dict = query.get_metadata_filter_dict()
        results = SearchService.search_by_text_and_metadata(
            vectorizer=vectorizer,
            query_text=query.query,
            k=query.top_k,
            metadata_filter=metadata_filter_dict,
            distance_threshold=query.distance_threshold,
        )
        response_items = [QueryResponseItem(data=doc) for doc in results]
        return QueryResponse(results=response_items)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        raise HTTPException(status_code=500, detail=str(e))
