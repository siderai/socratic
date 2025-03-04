"""Authentication endpoints."""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_user_repo
from app.db.sqlalchemy import get_db
from app.db.user.repo import UserRepo, UserAlreadyExistsError, UserRepoError, AuthenticationError
from app.schemas.user import Token, User, UserCreate
from app.services.security import create_access_token
from app.settings import settings

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, user_repo: UserRepo = Depends(get_user_repo)
) -> Any:
    """
    Register a new user.
    
    Args:
        user_in: User creation data
        user_repo: User repository
        
    Returns:
        The created user
        
    Raises:
        HTTPException: If the user already exists or if there's an error during registration
    """
    try:
        user = await user_repo.create(user_in)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during registration: {str(e)}",
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepo = Depends(get_user_repo),
) -> Any:
    """
    Login and get access token.
    
    Args:
        form_data: Form data with username and password
        user_repo: User repository
        
    Returns:
        Access token
        
    Raises:
        HTTPException: If the credentials are invalid or if there's an error during login
    """
    try:
        # Authenticate user - will raise AuthenticationError if authentication fails
        user = await user_repo.authenticate(form_data.username, form_data.password)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}",
        ) 