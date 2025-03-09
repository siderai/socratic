"""Test fixtures for the application."""

import os
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, Generator, List

import pytest
from alembic import config as alembic_config
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.caching.redis_repo import RedisRepo
from app.db.sqlalchemy import get_session, build_db_session_factory
from app.db.user.repo import UserRepo
from app.main import get_application
from app.services.security import create_access_token
from app.settings import settings
from redis import asyncio as aioredis

# Load test environment variables
load_dotenv(".env.test")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Ensure we're using test settings
    os.environ["TESTING"] = "True"
    
    # Run database migrations
    alembic_config.main(argv=["upgrade", "head"])
    
    yield
    
    # Clean up after tests
    alembic_config.main(argv=["downgrade", "base"])


@pytest.fixture
def fastapi_app() -> FastAPI:
    """Get the FastAPI application."""
    app = get_application()
    return app


@pytest.fixture
async def db_session(fastapi_app: FastAPI) -> AsyncGenerator[AsyncSession, None]:
    """Get a real database session with transaction management."""
    # Ensure the app is initialized with the database session factory
    async with LifespanManager(fastapi_app):
        # Create a new session
        session = fastapi_app.state.db_session_factory()
        try:
            # Start a transaction
            await session.begin()
            yield session
            # Rollback the transaction after the test
            await session.rollback()
        finally:
            await session.close()


@pytest.fixture
def user_repo(db_session: AsyncSession) -> UserRepo:
    """Get a user repository with a real session."""
    return UserRepo(session=db_session)


@pytest.fixture
async def redis_repo(fastapi_app: FastAPI) -> AsyncGenerator[RedisRepo, None]:
    """Get a Redis repository."""
    async with LifespanManager(fastapi_app):
        yield fastapi_app.state.redis_repo


@pytest.fixture
def client(fastapi_app: FastAPI) -> Generator[TestClient, None, None]:
    """Get a test client."""
    # Create a test client
    test_client = TestClient(fastapi_app)
    
    # Override the app's dependency to use the test database session
    from app.db.sqlalchemy import get_session
    
    async def override_get_session():
        """Override the get_session dependency to use the test database session."""
        db_session_factory = fastapi_app.state.db_session_factory
        async with db_session_factory() as session:
            yield session
    
    # Apply the override
    from fastapi import Depends
    from app.api.dependencies.database import get_db_session
    
    fastapi_app.dependency_overrides[get_db_session] = override_get_session
    
    yield test_client
    
    # Clean up
    fastapi_app.dependency_overrides = {}


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Get test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def access_token(test_user_data: Dict[str, Any]) -> str:
    """Get a valid access token for the test user."""
    return create_access_token(
        subject=test_user_data["id"],
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@pytest.fixture
def expired_token(test_user_data: Dict[str, Any]) -> str:
    """Get an expired access token for the test user."""
    return create_access_token(
        subject=test_user_data["id"],
        expires_delta=timedelta(seconds=-1),  # Expired token
    )


@pytest.fixture
def auth_headers(access_token: str) -> Dict[str, str]:
    """Get authorization headers with a valid token."""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def user_id() -> int:
    """Get a test user ID."""
    return 1
