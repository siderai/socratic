"""Healthcheck endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sqlalchemy import get_db

router = APIRouter()


@router.get("/healthcheck", tags=["healthcheck"])
async def healthcheck(db: AsyncSession = Depends(get_db)) -> dict:
    """Check if the service is healthy."""
    # Try to execute a simple query to check database connection
    await db.execute("SELECT 1")
    
    return {"status": "ok"} 