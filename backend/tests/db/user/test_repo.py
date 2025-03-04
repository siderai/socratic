"""Tests for user repository."""

from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user.models import UserModel
from app.db.user.repo import (
    UserRepo,
    UserRepoError,
    UserNotFoundError,
    UserAlreadyExistsError,
    AuthenticationError,
)
from app.schemas.user import UserCreate, UserUpdate
from app.services.security import get_password_hash, verify_password


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data fixture."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def test_user_model() -> UserModel:
    """Test user model fixture."""
    user = UserModel(
        id=1,
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return user


@pytest.fixture
def mock_crud() -> AsyncMock:
    """Mock CRUD fixture."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_session() -> AsyncMock:
    """Mock session fixture."""
    mock = AsyncMock(spec=AsyncSession)
    return mock


@pytest.fixture
def user_repo(mock_session: AsyncMock, mock_crud: AsyncMock) -> UserRepo:
    """User repository fixture with mocked dependencies."""
    repo = UserRepo(session=mock_session)
    repo._crud = mock_crud
    return repo


@pytest.mark.asyncio
async def test_create_user_success(
    user_repo: UserRepo,
    test_user_data: Dict[str, Any],
    test_user_model: UserModel,
) -> None:
    """Test successful user creation."""
    # - Arrange -
    user_create = UserCreate(**test_user_data)
    
    # Mock get_by_email and get_by_username to return None (user doesn't exist)
    user_repo.get_by_email = AsyncMock(return_value=None)
    user_repo.get_by_username = AsyncMock(return_value=None)
    
    # Mock create to return the user ID
    user_repo._crud.create = AsyncMock(return_value=[1])
    
    # Mock get to return the created user
    user_repo._crud.get = AsyncMock(return_value=test_user_model)
    
    # - Act -
    created_user = await user_repo.create(user_create)
    
    # - Assert -
    assert created_user.id == 1
    assert created_user.email == test_user_data["email"]
    assert created_user.username == test_user_data["username"]
    assert created_user.is_active is True
    
    # Verify that the password was hashed
    user_repo._crud.create.assert_called_once()
    create_args = user_repo._crud.create.call_args[1]["model_data"]
    assert "password" not in create_args
    assert "hashed_password" in create_args
    assert verify_password(test_user_data["password"], create_args["hashed_password"])


@pytest.mark.asyncio
async def test_create_user_email_exists(
    user_repo: UserRepo,
    test_user_data: Dict[str, Any],
    test_user_model: UserModel,
) -> None:
    """Test user creation when email already exists."""
    # - Arrange -
    user_create = UserCreate(**test_user_data)
    
    # Mock get_by_email to return a user (email exists)
    existing_user = test_user_model
    user_repo.get_by_email = AsyncMock(return_value=existing_user)
    
    # - Act & Assert -
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await user_repo.create(user_create)
    
    assert str(exc_info.value) == f"User with email {test_user_data['email']} already exists"
    user_repo._crud.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_username_exists(
    user_repo: UserRepo,
    test_user_data: Dict[str, Any],
    test_user_model: UserModel,
) -> None:
    """Test user creation when username already exists."""
    # - Arrange -
    user_create = UserCreate(**test_user_data)
    
    # Mock get_by_email to return None (email doesn't exist)
    user_repo.get_by_email = AsyncMock(return_value=None)
    
    # Mock get_by_username to return a user (username exists)
    existing_user = test_user_model
    user_repo.get_by_username = AsyncMock(return_value=existing_user)
    
    # - Act & Assert -
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await user_repo.create(user_create)
    
    assert str(exc_info.value) == f"User with username {test_user_data['username']} already exists"
    user_repo._crud.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_integrity_error(
    user_repo: UserRepo,
    test_user_data: Dict[str, Any],
) -> None:
    """Test user creation with database integrity error."""
    # - Arrange -
    user_create = UserCreate(**test_user_data)
    
    # Mock get_by_email and get_by_username to return None (user doesn't exist)
    user_repo.get_by_email = AsyncMock(return_value=None)
    user_repo.get_by_username = AsyncMock(return_value=None)
    
    # Mock create to raise IntegrityError
    error_message = "Duplicate key value violates unique constraint"
    user_repo._crud.create = AsyncMock(side_effect=IntegrityError(None, None, error_message))
    
    # - Act & Assert -
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await user_repo.create(user_create)
    
    assert "User creation failed due to integrity error" in str(exc_info.value)
    assert error_message in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_user_success(
    user_repo: UserRepo,
    test_user_model: UserModel,
) -> None:
    """Test successful user update."""
    # - Arrange -
    user_id = 1
    update_data = UserUpdate(email="newemail@example.com")
    
    # Mock get_by_id to return the user
    user_repo.get_by_id = AsyncMock(return_value=test_user_model)
    
    # Mock get_by_email to return None (new email doesn't exist)
    user_repo.get_by_email = AsyncMock(return_value=None)
    
    # Mock update and get
    user_repo._crud.update = AsyncMock()
    
    # Create an updated user model
    updated_user = UserModel(
        id=1,
        email="newemail@example.com",
        username="testuser",
        hashed_password=test_user_model.hashed_password,
        is_active=True,
        created_at=test_user_model.created_at,
        updated_at=datetime.utcnow(),
    )
    user_repo._crud.get = AsyncMock(return_value=updated_user)
    
    # - Act -
    updated_user = await user_repo.update(user_id, update_data)
    
    # - Assert -
    assert updated_user.id == 1
    assert updated_user.email == "newemail@example.com"
    assert updated_user.username == "testuser"
    
    # Verify that update was called with the correct data
    user_repo._crud.update.assert_called_once()
    update_args = user_repo._crud.update.call_args[1]["model_data"]
    assert update_args["email"] == "newemail@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(
    user_repo: UserRepo,
) -> None:
    """Test user update when user not found."""
    # - Arrange -
    user_id = 999  # Non-existent user ID
    update_data = UserUpdate(email="newemail@example.com")
    
    # Mock get_by_id to return None (user not found)
    user_repo.get_by_id = AsyncMock(return_value=None)
    
    # - Act & Assert -
    with pytest.raises(UserNotFoundError) as exc_info:
        await user_repo.update(user_id, update_data)
    
    assert str(exc_info.value) == f"User with ID {user_id} not found"
    user_repo._crud.update.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_success(
    user_repo: UserRepo,
    test_user_model: UserModel,
    mock_session: AsyncMock,
) -> None:
    """Test successful user authentication."""
    # - Arrange -
    username = "testuser"
    password = "testpassword123"
    
    # Mock session.execute to return a result with the user
    result_mock = MagicMock()
    result_mock.scalars().first.return_value = test_user_model
    mock_session.execute.return_value = result_mock
    
    # - Act -
    authenticated_user = await user_repo.authenticate(username, password)
    
    # - Assert -
    assert authenticated_user.id == 1
    assert authenticated_user.email == test_user_model.email
    assert authenticated_user.username == test_user_model.username
    
    # Verify that execute was called with the correct query
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_not_found(
    user_repo: UserRepo,
    mock_session: AsyncMock,
) -> None:
    """Test authentication when user not found."""
    # - Arrange -
    username = "nonexistentuser"
    password = "testpassword123"
    
    # Mock session.execute to return a result with no user
    result_mock = MagicMock()
    result_mock.scalars().first.return_value = None
    mock_session.execute.return_value = result_mock
    
    # - Act & Assert -
    with pytest.raises(AuthenticationError) as exc_info:
        await user_repo.authenticate(username, password)
    
    assert str(exc_info.value) == "User not found"


@pytest.mark.asyncio
async def test_authenticate_incorrect_password(
    user_repo: UserRepo,
    test_user_model: UserModel,
    mock_session: AsyncMock,
) -> None:
    """Test authentication with incorrect password."""
    # - Arrange -
    username = "testuser"
    password = "wrongpassword"
    
    # Mock session.execute to return a result with the user
    result_mock = MagicMock()
    result_mock.scalars().first.return_value = test_user_model
    mock_session.execute.return_value = result_mock
    
    # Mock verify_password to return False
    with patch("app.db.user.repo.verify_password", return_value=False):
        # - Act & Assert -
        with pytest.raises(AuthenticationError) as exc_info:
            await user_repo.authenticate(username, password)
        
        assert str(exc_info.value) == "Incorrect password"


@pytest.mark.asyncio
async def test_authenticate_inactive_user(
    user_repo: UserRepo,
    test_user_model: UserModel,
    mock_session: AsyncMock,
) -> None:
    """Test authentication with inactive user."""
    # - Arrange -
    username = "testuser"
    password = "testpassword123"
    
    # Make the user inactive
    test_user_model.is_active = False
    
    # Mock session.execute to return a result with the inactive user
    result_mock = MagicMock()
    result_mock.scalars().first.return_value = test_user_model
    mock_session.execute.return_value = result_mock
    
    # Mock verify_password to return True
    with patch("app.db.user.repo.verify_password", return_value=True):
        # - Act & Assert -
        with pytest.raises(AuthenticationError) as exc_info:
            await user_repo.authenticate(username, password)
        
        assert str(exc_info.value) == "User is inactive" 