"""Database dependencies for the API."""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.sqlalchemy import get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for the request."""
    async for session in get_session():
        yield session 