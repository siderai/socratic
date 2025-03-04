"""Configuration of routers for all endpoints."""
from fastapi import APIRouter

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.healthcheck import router as healthcheck_router

router = APIRouter()

router.include_router(healthcheck_router)
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])