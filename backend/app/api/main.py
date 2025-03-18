from fastapi import APIRouter

from app.api.routes import user
from app.api.routes import login

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(login.router)

# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
