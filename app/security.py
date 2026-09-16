from __future__ import annotations

import hmac

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_503_SERVICE_UNAVAILABLE

from app.config import import_admin_token


bearer = HTTPBearer(auto_error=False)


def require_import_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    """Protect expensive and potentially dangerous ingestion endpoints."""
    expected = import_admin_token()
    if expected is None:
        raise HTTPException(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            detail="Import endpoints are disabled until VECTORIZATION_ADMIN_TOKEN is configured",
        )
    if credentials is None or not hmac.compare_digest(credentials.credentials, expected):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid import token")
