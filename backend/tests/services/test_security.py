"""Tests for security service."""

import time
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from jose import jwt

from app.services.security import (
    ALGORITHM,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.settings import settings


def test_password_hashing() -> None:
    """Test password hashing and verification."""
    # - Arrange -
    password = "testpassword123"
    
    # - Act -
    hashed_password = get_password_hash(password)
    
    # - Assert -
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_create_access_token() -> None:
    """Test JWT access token creation."""
    # - Arrange -
    user_id = 123
    
    # - Act -
    token = create_access_token(subject=user_id)
    
    # - Assert -
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    
    # Check that expiration is in the future
    assert datetime.fromtimestamp(payload["exp"], UTC) > datetime.now(UTC)


def test_create_access_token_with_custom_expiry() -> None:
    """Test JWT access token creation with custom expiry."""
    # - Arrange -
    user_id = 123
    expires_delta = timedelta(minutes=5)
    
    # - Act -
    token = create_access_token(subject=user_id, expires_delta=expires_delta)
    
    # - Assert -
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)
    
    # Check that expiration is approximately 5 minutes in the future
    # Allow for a small margin of error in the test execution time
    expected_exp = datetime.now(UTC) + expires_delta
    actual_exp = datetime.fromtimestamp(payload["exp"], UTC)
    difference = abs((actual_exp - expected_exp).total_seconds())
    assert difference < 2  # Less than 2 seconds difference


def test_token_expiry() -> None:
    """Test that token expiry works correctly."""
    # - Arrange -
    user_id = 123
    expires_delta = timedelta(seconds=1)  # Very short expiry for testing
    
    # - Act -
    token = create_access_token(subject=user_id, expires_delta=expires_delta)
    
    # Wait for token to expire
    time.sleep(2)
    
    # - Assert -
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


@patch("app.settings.settings.SECRET_KEY", "test_secret_key")
def test_token_with_different_secret_key() -> None:
    """Test that tokens are validated with the correct secret key."""
    # - Arrange -
    user_id = 123
    
    # - Act -
    token = create_access_token(subject=user_id)
    
    # - Assert -
    # Should validate with the correct key
    payload = jwt.decode(token, "test_secret_key", algorithms=[ALGORITHM])
    assert payload["sub"] == str(user_id)
    
    # Should fail with an incorrect key
    with pytest.raises(jwt.JWTError):
        jwt.decode(token, "wrong_secret_key", algorithms=[ALGORITHM]) 