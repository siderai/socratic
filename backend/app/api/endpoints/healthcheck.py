"""Healthcheck endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sqlalchemy import get_session

router = APIRouter()


@router.get("/healthcheck", tags=["healthcheck"])
async def healthcheck(session: AsyncSession = Depends(get_session)) -> dict:
    """Check if the service is healthy."""
    # Try to execute a simple query to check database connection
    await session.execute("SELECT 1")
    return {"status": "ok"} 