"""Tests for authentication endpoints."""

from http import HTTPStatus
from typing import Dict, Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints.auth import register, login
from app.db.user.repo import UserRepo
from app.schemas.user import User, UserCreate
from app.services.security import ALGORITHM
from app.settings import settings


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
async def test_user(db_session: AsyncSession, test_user_data: Dict[str, Any]) -> User:
    """Create a test user in the database."""
    # Create a user directly in the database
    user_repo = UserRepo(session=db_session)
    
    # Check if user already exists
    existing_user = await user_repo.get_by_email(test_user_data["email"])
    if existing_user:
        return existing_user
    
    # Create the user
    user_create = UserCreate(**test_user_data)
    user = await user_repo.create(user_create)
    return user


async def test_register_success(
    db_session: AsyncSession,
) -> None:
    """Test successful user registration."""
    # - Arrange -
    user_data = {
        "email": "new_user@example.com",
        "username": "newuser",
        "password": "newpassword123",
    }
    user_in = UserCreate(**user_data)
    user_repo = UserRepo(session=db_session)
    
    # - Act -
    user = await register(user_in=user_in, user_repo=user_repo)
    
    # - Assert -
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]
    
    # Verify user was created in the database
    db_user = await user_repo.get_by_email(user_data["email"])
    assert db_user is not None
    assert db_user.email == user_data["email"]
    assert db_user.username == user_data["username"]


async def test_register_user_already_exists(
    db_session: AsyncSession,
    test_user: User,
    test_user_data: Dict[str, Any],
) -> None:
    """Test registration with existing user."""
    # - Arrange -
    user_in = UserCreate(**test_user_data)
    user_repo = UserRepo(session=db_session)
    
    # - Act & Assert -
    with pytest.raises(Exception):  # Should raise UserAlreadyExistsError
        await register(user_in=user_in, user_repo=user_repo)


async def test_login_success(
    db_session: AsyncSession,
    test_user: User,
    test_user_data: Dict[str, Any],
) -> None:
    """Test successful login."""
    # - Arrange -
    from fastapi.security import OAuth2PasswordRequestForm
    
    class FormData:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    
    form_data = FormData(
        username=test_user_data["username"],
        password=test_user_data["password"],
    )
    user_repo = UserRepo(session=db_session)
    
    # - Act -
    token_data = await login(form_data=form_data, user_repo=user_repo)
    
    # - Assert -
    assert token_data["token_type"] == "bearer"
    assert token_data["access_token"] is not None
    
    # Verify token
    payload = jwt.decode(
        token_data["access_token"], settings.SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert payload["sub"] == str(test_user.id)


async def test_login_invalid_credentials(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Test login with invalid credentials."""
    # - Arrange -
    from fastapi.security import OAuth2PasswordRequestForm
    
    class FormData:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    
    form_data = FormData(
        username=test_user.username,
        password="wrongpassword",
    )
    user_repo = UserRepo(session=db_session)
    
    # - Act & Assert -
    with pytest.raises(Exception):  # Should raise AuthenticationError
        await login(form_data=form_data, user_repo=user_repo) 