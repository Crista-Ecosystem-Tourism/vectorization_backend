import json
import csv
import requests
from typing import List, Dict, Any, Union
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataLoader:
    def load_from_json(self, filepath: str) -> List[Dict[str, Any]]:
        logger.info(f"Загрузка данных из JSON файла: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Успешно загружено {len(data)} записей из JSON")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки JSON: {e}")
            raise

    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        logger.info(f"Загрузка данных из CSV файла: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = [row for row in reader]
            logger.info(f"Успешно загружено {len(data)} записей из CSV")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки CSV: {e}")
            raise

    def load_from_api(self, url: str) -> Union[List[Dict[str, Any]], None]:
        logger.info(f"Загрузка данных из API: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                logger.info(f"Успешно загружено {len(data)} записей из API")
            else:
                logger.info("Получен успешный ответ от API")
            return data
        except Exception as e:
            logger.error(f"Ошибка загрузки данных с API: {e}")
            raise
