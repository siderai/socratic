"""Tests for authentication dependencies."""

from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.api.dependencies.auth import get_current_user, get_current_active_user
from app.db.user.repo import UserRepo, UserRepoError
from app.services.security import ALGORITHM, create_access_token
from app.settings import settings


@pytest.fixture
def test_user() -> Dict[str, Any]:
    """Test user fixture."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Mock user repository fixture."""
    mock_repo = AsyncMock(spec=UserRepo)
    return mock_repo


@pytest.fixture
def valid_token(test_user: Dict[str, Any]) -> str:
    """Valid JWT token fixture."""
    return create_access_token(subject=test_user["id"])


@pytest.fixture
def expired_token(test_user: Dict[str, Any]) -> str:
    """Expired JWT token fixture."""
    return create_access_token(
        subject=test_user["id"],
        expires_delta=timedelta(seconds=-1),  # Expired token
    )


@pytest.mark.asyncio
async def test_get_current_user_valid_token(
    valid_token: str, mock_user_repo: AsyncMock, test_user: Dict[str, Any]
) -> None:
    """Test get_current_user with a valid token."""
    # - Arrange -
    mock_user_repo.get_by_id.return_value = test_user
    
    # - Act -
    user = await get_current_user(token=valid_token, user_repo=mock_user_repo)
    
    # - Assert -
    assert user == test_user
    mock_user_repo.get_by_id.assert_called_once_with(test_user["id"])


@pytest.mark.asyncio
async def test_get_current_user_expired_token(
    expired_token: str, mock_user_repo: AsyncMock
) -> None:
    """Test get_current_user with an expired token."""
    # - Arrange -
    # No need to set up mock_user_repo as the function should raise before calling it
    
    # - Act & Assert -
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=expired_token, user_repo=mock_user_repo)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
    mock_user_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_user_repo: AsyncMock) -> None:
    """Test get_current_user with an invalid token."""
    # - Arrange -
    invalid_token = "invalid.token.string"
    
    # - Act & Assert -
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=invalid_token, user_repo=mock_user_repo)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
    mock_user_repo.get_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(
    valid_token: str, mock_user_repo: AsyncMock
) -> None:
    """Test get_current_user when the user is not found."""
    # - Arrange -
    mock_user_repo.get_by_id.return_value = None
    
    # - Act & Assert -
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=valid_token, user_repo=mock_user_repo)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_get_current_user_repo_error(
    valid_token: str, mock_user_repo: AsyncMock
) -> None:
    """Test get_current_user when there's a repository error."""
    # - Arrange -
    error_message = "Database connection error"
    mock_user_repo.get_by_id.side_effect = UserRepoError(error_message)
    
    # - Act & Assert -
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=valid_token, user_repo=mock_user_repo)
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == f"Error getting user: {error_message}"


@pytest.mark.asyncio
async def test_get_current_active_user_active(test_user: Dict[str, Any]) -> None:
    """Test get_current_active_user with an active user."""
    # - Arrange -
    # Ensure the user is active
    test_user["is_active"] = True
    
    # - Act -
    user = await get_current_active_user(current_user=test_user)
    
    # - Assert -
    assert user == test_user


@pytest.mark.asyncio
async def test_get_current_active_user_inactive(test_user: Dict[str, Any]) -> None:
    """Test get_current_active_user with an inactive user."""
    # - Arrange -
    # Make the user inactive
    test_user["is_active"] = False
    
    # - Act & Assert -
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=test_user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user" 