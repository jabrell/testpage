import time
import uuid
from typing import Any

import jwt
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import api_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any):
        """Log the request and response for each API call including the duration
        and the user who made the request."""
        request_id = str(uuid.uuid4())
        if request.headers.get("authorization"):
            token = request.headers.get("authorization").split(" ")[1]
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            user = payload["sub"]
        else:
            user = "Anonymous"
        start_time = time.time()
        api_logger.info(f"{request_id} {user} {request.method} {request.url}")
        try:
            response = await call_next(request)
        except HTTPException as http_exc:
            api_logger.error(
                f"{request_id} HTTPException: Status Code {http_exc.status_code}, Detail {http_exc.detail}"  # noqa: E501
            )
            response = http_exc
        except Exception as exc:
            api_logger.error(f"{request_id} UNEXPECTED ERROR: {exc}")
            response = exc
        duration = time.time() - start_time
        status_code = (
            response.status_code
            if hasattr(response, "status_code")
            else "No status code"
        )
        api_logger.info(
            f"{request_id} Response: {status_code} - Duration: {duration:.4f} seconds"
        )
        return response
