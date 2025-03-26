from fastapi import APIRouter

from .routes import login_router, schema_router, user_router, utils_router

api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(login_router)
api_router.include_router(schema_router)
api_router.include_router(utils_router)

# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
