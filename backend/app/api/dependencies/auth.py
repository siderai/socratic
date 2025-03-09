"""Authentication dependencies."""

from datetime import datetime
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.db.user import UserModel
from app.db.user.repo import UserRepo, UserRepoError
from app.schemas.user import TokenPayload, User
from app.services.security import ALGORITHM
from app.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_repo(session: AsyncSession = Depends(get_db_session)) -> UserRepo:
    """
    Get user repository.
    
    Args:
        session: Database session
        
    Returns:
        User repository
    """
    return UserRepo(session=session)


async def get_current_user(
    token: str = Depends(oauth2_scheme), user_repo: UserRepo = Depends(get_user_repo)
) -> User:
    """
    Get the current authenticated user.
    
    Args:
        token: JWT token
        user_repo: User repository
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If the token is invalid or if there's an error
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=user_id, exp=payload.get("exp"))
        
        # Check if token has expired
        if datetime.utcnow().timestamp() > token_data.exp:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user = await user_repo.get_by_id(int(token_data.sub))
        if user is None:
            raise credentials_exception
        
        return user
    except UserRepoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}",
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    # Check if current_user is a dict and access is_active accordingly
    is_active = current_user.get("is_active") if isinstance(current_user, dict) else current_user.is_active
    
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    
    return current_user 