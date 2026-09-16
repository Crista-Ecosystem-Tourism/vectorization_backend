import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import urlparse

import requests

from app.config import (
    import_directory,
    import_max_bytes,
    import_timeout_seconds,
    import_url_allowlist,
)
from app.utils.logger import get_logger


logger = get_logger(__name__)


class DataLoader:
    def load_from_json(self, filename: str) -> List[Dict[str, Any]]:
        path = self._resolve_json_path(filename)
        logger.info("Загрузка данных из разрешённого JSON файла: %s", path.name)
        if path.stat().st_size > import_max_bytes():
            raise ValueError("JSON file exceeds the configured size limit")
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        logger.info("Успешно загружено %s записей из JSON", len(data))
        return data

    def load_from_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Legacy local helper. It is deliberately not exposed as an API route."""
        with open(filepath, "r", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def load_from_api(self, url: str) -> Union[List[Dict[str, Any]], None]:
        parsed = urlparse(url)
        allowed_hosts = import_url_allowlist()
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.hostname.lower() not in allowed_hosts
        ):
            raise ValueError("URL host is not allowed for imports")

        logger.info("Загрузка данных из разрешённого API host: %s", parsed.hostname)
        with requests.get(
            url,
            timeout=import_timeout_seconds(),
            allow_redirects=False,
            stream=True,
        ) as response:
            response.raise_for_status()
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > import_max_bytes():
                raise ValueError("API response exceeds the configured size limit")

            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_content(chunk_size=64 * 1024):
                total += len(chunk)
                if total > import_max_bytes():
                    raise ValueError("API response exceeds the configured size limit")
                chunks.append(chunk)
        data = json.loads(b"".join(chunks))
        if isinstance(data, list):
            logger.info("Успешно загружено %s записей из API", len(data))
        else:
            logger.info("Получен успешный ответ от API")
        return data

    @staticmethod
    def _resolve_json_path(filename: str) -> Path:
        requested = Path(filename)
        if requested.name != filename or requested.suffix.lower() != ".json":
            raise ValueError("Only a JSON filename inside the import directory is allowed")
        allowed_dir = import_directory()
        candidate = (allowed_dir / requested.name).resolve()
        if candidate.parent != allowed_dir:
            raise ValueError("Import path escapes the configured directory")
        return candidate
