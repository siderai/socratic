"""User schemas for authentication."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    is_active: bool = Field(True, description="Flag indicating if the user account is active")


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(
        ..., 
        min_length=8, 
        description="User's password, must be at least 8 characters long"
    )


class UserUpdate(BaseModel):
    """Schema for user update."""

    email: EmailStr | None = Field(None, description="User's email address")
    username: str | None = Field(None, description="User's username")
    password: str | None = Field(
        None, 
        description="User's password, will be hashed before storage"
    )
    is_active: bool | None = Field(
        None, 
        description="Flag indicating if the user account is active"
    )


class UserInDB(UserBase):
    """Schema for user in database."""

    id: int = Field(..., description="Unique identifier for the user")
    hashed_password: str = Field(..., description="Hashed password for the user")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated")

    class Config:
        """Pydantic config."""

        from_attributes = True


class User(UserBase):
    """Schema for user response."""

    id: int = Field(..., description="Unique identifier for the user")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: datetime = Field(..., description="Timestamp when the user was last updated")

    class Config:
        """Pydantic config."""

        from_attributes = True


class Token(BaseModel):
    """Schema for token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of token, usually 'bearer'")


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: str = Field(..., description="Subject of the token, usually the user ID")
    exp: int = Field(..., description="Expiration timestamp of the token") 