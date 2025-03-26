# simple hello world with fast api

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings

app = FastAPI()

# include routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return "Hello Automated World"
