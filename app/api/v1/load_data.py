from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.dependencies.vectorizer import get_vectorizer
from app.security import require_import_admin
from app.utils.data_loader import DataLoader
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)
data_loader = DataLoader()


class JsonImportRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)


class UrlImportRequest(BaseModel):
    url: HttpUrl


@router.post("/load/json")
def load_json(payload: JsonImportRequest, _: None = Depends(require_import_admin)):
    logger.info("Получен внутренний запрос на загрузку JSON")
    try:
        data = data_loader.load_from_json(payload.filename)
        get_vectorizer().build_and_store_embeddings(data)
        return {"message": "Данные успешно загружены и индексированы"}
    except Exception as exc:
        logger.error("Ошибка при загрузке из JSON: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/load/api")
def load_api(payload: UrlImportRequest, _: None = Depends(require_import_admin)):
    logger.info("Получен внутренний запрос на загрузку данных из API")
    try:
        data = data_loader.load_from_api(str(payload.url))
        get_vectorizer().build_and_store_embeddings(data)
        return {"message": "Данные успешно загружены и индексированы"}
    except Exception as exc:
        logger.error("Ошибка при загрузке из API: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
