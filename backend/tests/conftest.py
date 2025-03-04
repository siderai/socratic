"""Test fixtures for the application."""

from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from alembic import config as alembic_config
from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.caching.redis_repo import RedisRepo
from app.db.sqlalchemy import get_db
from app.db.user.repo import UserRepo
from app.main import get_application
from app.services.security import create_access_token
from app.settings import settings


@pytest.fixture
def db_migrations() -> Generator:
    """Run database migrations before tests and downgrade after."""
    alembic_config.main(argv=["upgrade", "head"])
    yield
    alembic_config.main(argv=["downgrade", "base"])


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: List[pytest.Function]) -> None:
    """Add db_migrations fixture to all tests."""
    # We can't use autouse, because it appends fixture to the end
    # but session from db_session fixture must be closed before migrations downgrade
    for item in items:
        item.fixturenames = ["db_migrations"] + item.fixturenames


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with get_db() as session:
        yield session


@pytest.fixture
async def redis_repo() -> RedisRepo:
    """Get a Redis repository."""
    app = get_application()
    async with LifespanManager(app):
        yield app.state.redis_repo


@pytest.fixture
def client() -> TestClient:
    """Get a test client."""
    return TestClient(get_application())


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Get test user data."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
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
def mock_user_repo() -> AsyncMock:
    """Get a mock user repository."""
    return AsyncMock(spec=UserRepo)


@pytest.fixture
def user_id() -> int:
    """Get a test user ID."""
    return 1
