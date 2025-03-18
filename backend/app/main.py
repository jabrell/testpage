from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI()

# include routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
def read_root():
    return "Hello Automated World"
