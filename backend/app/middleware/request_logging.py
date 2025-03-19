from typing import Any

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import api_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any):
        api_logger.info(f"{request.method} {request.url}")
        try:
            response = await call_next(request)
        except HTTPException as http_exc:
            api_logger.error(
                f"HTTPException: Status Code {http_exc.status_code}, Detail {http_exc.detail}"  # noqa: E501
            )
            response = http_exc
        except Exception as exc:
            api_logger.error(f"UNEXPECTED ERROR: {exc}")
            response = exc
        api_logger.info(
            f"Response: {response.status_code if hasattr(response, 'status_code') else 'No status code'}"  # noqa: E501
        )
        return response
