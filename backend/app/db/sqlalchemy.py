"""SQLAlchemy helpers."""

from asyncio import current_task
from typing import Callable, AsyncGenerator
import contextlib

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool.impl import AsyncAdaptedQueuePool

from app.settings import settings

AsyncSessionFactory = Callable[..., AsyncSession]


def make_url_async(url: str) -> str:
    """Add +asyncpg to url scheme."""
    return "postgresql+asyncpg" + url[url.find(":") :]  # noqa: WPS336


def make_url_sync(url: str) -> str:
    """Remove +asyncpg from url scheme."""
    return "postgresql" + url[url.find(":") :]  # noqa: WPS336


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(metadata=MetaData(naming_convention=convention))

engine: AsyncEngine = create_async_engine(
    make_url_async(settings.POSTGRES_DSN), poolclass=AsyncAdaptedQueuePool
)


async def build_db_session_factory() -> AsyncSessionFactory:
    await verify_db_connection(engine)

    return async_scoped_session(
        async_sessionmaker(bind=engine, expire_on_commit=False),
        scopefunc=current_task,
    )


async def verify_db_connection(engine: AsyncEngine) -> None:
    connection = await engine.connect()
    await connection.close()


async def close_db_connections() -> None:
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as a dependency."""
    from app.main import app
    session_factory = app.state.db_session_factory
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session.
    
    This function creates a session, yields it, and handles committing or
    rolling back changes and closing the session.
    
    Example:
        async with get_session() as session:
            # Use session here
            # Changes will be committed automatically if no exception occurs
    """
    from app.main import app
    session_factory = app.state.db_session_factory
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
