"""Tests for authentication endpoints."""

from http import HTTPStatus
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user.repo import UserRepo
from app.main import get_application
from app.services.security import ALGORITHM, verify_password


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Mock user repository fixture."""
    mock_repo = AsyncMock(spec=UserRepo)
    return mock_repo


@pytest.fixture
def client() -> TestClient:
    """Test client fixture."""
    return TestClient(get_application())


@patch("app.api.endpoints.auth.get_user_repo")
async def test_register_success(
    mock_get_user_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    client: TestClient,
    test_user_data: Dict[str, Any],
) -> None:
    """Test successful user registration."""
    # - Arrange -
    mock_get_user_repo.return_value = mock_user_repo
    
    # Mock the create method to return a user with the same data plus an ID
    created_user = {
        **test_user_data,
        "id": 1,
        "is_active": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    }
    # Remove password from the returned user
    del created_user["password"]
    
    mock_user_repo.create.return_value = created_user
    
    # - Act -
    response = client.post("/api/auth/register", json=test_user_data)
    
    # - Assert -
    assert response.status_code == HTTPStatus.CREATED
    
    # Check that the response contains the expected user data
    user_data = response.json()
    assert user_data["id"] == 1
    assert user_data["email"] == test_user_data["email"]
    assert user_data["username"] == test_user_data["username"]
    assert user_data["is_active"] is True
    assert "password" not in user_data
    
    # Verify that create was called with the correct data
    mock_user_repo.create.assert_called_once()
    call_args = mock_user_repo.create.call_args[0][0]
    assert call_args.email == test_user_data["email"]
    assert call_args.username == test_user_data["username"]
    assert call_args.password == test_user_data["password"]


@patch("app.api.endpoints.auth.get_user_repo")
async def test_register_user_already_exists(
    mock_get_user_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    client: TestClient,
    test_user_data: Dict[str, Any],
) -> None:
    """Test registration with existing user."""
    # - Arrange -
    mock_get_user_repo.return_value = mock_user_repo
    
    # Mock the create method to raise UserAlreadyExistsError
    from app.db.user.repo import UserAlreadyExistsError
    error_message = f"User with email {test_user_data['email']} already exists"
    mock_user_repo.create.side_effect = UserAlreadyExistsError(error_message)
    
    # - Act -
    response = client.post("/api/auth/register", json=test_user_data)
    
    # - Assert -
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == error_message


@patch("app.api.endpoints.auth.get_user_repo")
async def test_login_success(
    mock_get_user_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    client: TestClient,
    test_user_data: Dict[str, Any],
) -> None:
    """Test successful login."""
    # - Arrange -
    mock_get_user_repo.return_value = mock_user_repo
    
    # Mock the authenticate method to return a user
    authenticated_user = {
        "id": 1,
        "email": test_user_data["email"],
        "username": test_user_data["username"],
        "is_active": True,
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    }
    
    mock_user_repo.authenticate.return_value = authenticated_user
    
    # Prepare form data for login
    form_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    
    # - Act -
    response = client.post("/api/auth/login", data=form_data)
    
    # - Assert -
    assert response.status_code == HTTPStatus.OK
    
    # Check that the response contains an access token
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Verify the token
    from app.settings import settings
    payload = jwt.decode(
        token_data["access_token"], settings.SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert payload["sub"] == str(authenticated_user["id"])
    
    # Verify that authenticate was called with the correct credentials
    mock_user_repo.authenticate.assert_called_once_with(
        test_user_data["username"], test_user_data["password"]
    )


@patch("app.api.endpoints.auth.get_user_repo")
async def test_login_invalid_credentials(
    mock_get_user_repo: AsyncMock,
    mock_user_repo: AsyncMock,
    client: TestClient,
    test_user_data: Dict[str, Any],
) -> None:
    """Test login with invalid credentials."""
    # - Arrange -
    mock_get_user_repo.return_value = mock_user_repo
    
    # Mock the authenticate method to raise AuthenticationError
    from app.db.user.repo import AuthenticationError
    error_message = "Incorrect password"
    mock_user_repo.authenticate.side_effect = AuthenticationError(error_message)
    
    # Prepare form data for login
    form_data = {
        "username": test_user_data["username"],
        "password": "wrongpassword",
    }
    
    # - Act -
    response = client.post("/api/auth/login", data=form_data)
    
    # - Assert -
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["detail"] == error_message
    assert response.headers["WWW-Authenticate"] == "Bearer" 