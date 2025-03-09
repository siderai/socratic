"""Dependencies for healthcheck."""

from fastapi import Depends, Request
from sqlalchemy.sql import text


async def check_db_connection(request: Request) -> str | None:
    session_factory = request.app.state.db_session_factory

    async with session_factory() as db_session:
        try:
            await db_session.execute(text("SELECT 1"))
        except Exception as exc:
            return str(exc)

    return None


check_db_connection_dependency = Depends(check_db_connection)


async def check_redis_connection(request: Request) -> str | None:
    redis_repo = request.app.state.redis_repo
    return await redis_repo.ping()


check_redis_connection_dependency = Depends(check_redis_connection)
