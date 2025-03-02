from fastapi import APIRouter

from app.api.routes import user

api_router = APIRouter()
api_router.include_router(user.router)

# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
