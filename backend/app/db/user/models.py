"""User database models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.sqlalchemy import Base


class UserModel(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        index=True,
        doc="Unique identifier for the user"
    )
    email: Mapped[str] = mapped_column(
        unique=True, 
        index=True, 
        nullable=False,
        doc="User's email address, must be unique"
    )
    username: Mapped[str] = mapped_column(
        unique=True, 
        index=True, 
        nullable=False,
        doc="User's username, must be unique"
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False,
        doc="Hashed password for the user"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        doc="Flag indicating if the user account is active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow,
        doc="Timestamp when the user was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        doc="Timestamp when the user was last updated"
    )

    def __repr__(self) -> str:
        """Show string representation of user."""
        return f"User(id={self.id}, username={self.username}, email={self.email})" 