"""User endpoints."""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user, get_user_repo
from app.db.sqlalchemy import get_db
from app.db.user.repo import UserRepo, UserNotFoundError, UserAlreadyExistsError, UserRepoError
from app.schemas.user import User, UserUpdate

router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepo = Depends(get_user_repo),
) -> Any:
    """
    Update current user.
    
    Args:
        user_in: User update data
        current_user: Current authenticated user
        user_repo: User repository
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If there's an error during update
    """
    try:
        user = await user_repo.update(current_user.id, user_in)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepo = Depends(get_user_repo),
) -> Any:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        user_repo: User repository
        
    Returns:
        User information
        
    Raises:
        HTTPException: If the user is not found or if there's an error
    """
    try:
        user = await user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}",
        )


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    user_repo: UserRepo = Depends(get_user_repo),
) -> Any:
    """
    Get all users.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_user: Current authenticated user
        user_repo: User repository
        
    Returns:
        List of users
        
    Raises:
        HTTPException: If there's an error getting users
    """
    try:
        users = await user_repo.get_all()
        return users[skip : skip + limit]
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {str(e)}",
        ) 