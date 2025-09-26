from fastapi import APIRouter, HTTPException, Depends
from app.api.v1.schemas.place import QueryRequest, QueryResponse, QueryResponseItem
from app.services.search import SearchService
from app.utils.logger import get_logger
from app.dependencies.vectorizer import get_vectorizer

router = APIRouter()
logger = get_logger(__name__)

@router.post("/search", response_model=QueryResponse)
def search_places(query: QueryRequest, vectorizer=Depends(get_vectorizer)):
    logger.info(f"Получен запрос на поиск: {query.query} (top {query.top_k})")
    try:
        results = SearchService.search_by_text(
            vectorizer=vectorizer,
            query_text=query.query,
            k=query.top_k
        )
        response_items = [QueryResponseItem(data=doc) for doc in results]
        return QueryResponse(results=response_items)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        raise HTTPException(status_code=500, detail=str(e))
