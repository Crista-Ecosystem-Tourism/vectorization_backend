from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.place import QueryRequest, QueryResponse, QueryResponseItem
from app.utils.data_loader import DataLoader
from app.dependencies.vectorizer import get_vectorizer
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
data_loader = DataLoader()

@router.post("/load/json")
def load_json(filepath: str):
    logger.info(f"Получен запрос на загрузку данных из JSON: {filepath}")
    try:
        data = data_loader.load_from_json(filepath)
        get_vectorizer().build_and_store_embeddings(data)
        return {"message": "Данные успешно загружены и индексированы"}
    except Exception as e:
        logger.error(f"Ошибка при загрузке из JSON: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/load/api")
def load_api(url: str):
    logger.info(f"Получен запрос на загрузку данных из API: {url}")
    try:
        data = data_loader.load_from_api(url)
        get_vectorizer().build_and_store_embeddings(data)
        return {"message": "Данные успешно загружены и индексированы"}
    except Exception as e:
        logger.error(f"Ошибка при загрузке из API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

