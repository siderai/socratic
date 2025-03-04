"""Application with configuration for events, routers and middleware."""

import asyncio
from functools import partial

from fastapi import FastAPI
from redis import asyncio as aioredis

from app.api.routers import router
from app.caching.redis_repo import RedisRepo
from app.db.sqlalchemy import build_db_session_factory, close_db_connections
from app.resources import strings
from app.settings import settings


async def startup(application: FastAPI) -> None:
    # -- Database --
    db_session_factory = await build_db_session_factory()

    # -- Redis --
    redis_client = aioredis.from_url(settings.REDIS_DSN)
    pool = aioredis.BlockingConnectionPool(
        max_connections=settings.CONNECTION_POOL_SIZE,
        **redis_client.connection_pool.connection_kwargs,
    )
    redis_client.connection_pool = pool
    redis_repo = RedisRepo(redis=redis_client)

    application.state.db_session_factory = db_session_factory
    application.state.redis = redis_client
    application.state.redis_repo = redis_repo


async def shutdown(application: FastAPI) -> None:
    # -- Redis --
    redis_client: aioredis.Redis = application.state.redis
    await redis_client.close()

    # -- Database --
    await close_db_connections()


def get_application() -> FastAPI:
    """Create configured server application instance."""

    application = FastAPI(title=strings.PROJECT_NAME, openapi_url=None)

    application.add_event_handler(
        "startup", partial(startup, application)
    )
    application.add_event_handler("shutdown", partial(shutdown, application))

    application.include_router(router)

    return application
