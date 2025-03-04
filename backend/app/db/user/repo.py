"""User repository."""

from typing import Self

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CRUD
from app.db.user.models import UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.security import get_password_hash, verify_password


class UserRepoError(Exception):
    """Base exception for UserRepo errors."""
    pass


class UserNotFoundError(UserRepoError):
    """Exception raised when a user is not found."""
    pass


class UserAlreadyExistsError(UserRepoError):
    """Exception raised when trying to create a user that already exists."""
    pass


class AuthenticationError(UserRepoError):
    """Exception raised when authentication fails."""
    pass


class UserRepo:
    """Repository for user operations."""

    def __init__(self: Self, session: AsyncSession) -> None:
        """Initialize repo with CRUD."""
        self._crud = CRUD(session=session, cls_model=UserModel)
        self._session = session

    async def create(self: Self, user_in: UserCreate) -> User:
        """
        Create a new user.
        
        Raises:
            UserAlreadyExistsError: If a user with the same email or username already exists.
            UserRepoError: If there's an error during user creation.
        """
        try:
            # Check if user with the same email already exists
            existing_user = await self.get_by_email(user_in.email)
            if existing_user:
                raise UserAlreadyExistsError(f"User with email {user_in.email} already exists")
            
            # Check if user with the same username already exists
            existing_user = await self.get_by_username(user_in.username)
            if existing_user:
                raise UserAlreadyExistsError(f"User with username {user_in.username} already exists")
            
            user_data = user_in.model_dump(exclude={"password"})
            user_data["hashed_password"] = get_password_hash(user_in.password)
            
            user_id = await self._crud.create(model_data=user_data)
            user_in_db = await self._crud.get(pkey_val=user_id[0])
            return User.model_validate(user_in_db)
        except IntegrityError as e:
            raise UserAlreadyExistsError(f"User creation failed due to integrity error: {str(e)}") from e
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error creating user: {str(e)}") from e

    async def update(self: Self, user_id: int, user_in: Union[UserUpdate, dict]) -> User:
        """
        Update a user.
        
        Raises:
            UserNotFoundError: If the user with the given ID doesn't exist.
            UserAlreadyExistsError: If the update would create a duplicate email or username.
            UserRepoError: If there's an error during user update.
        """
        try:
            # Check if user exists
            user = await self.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            if isinstance(user_in, UserUpdate):
                user_data = user_in.model_dump(exclude_unset=True)
            else:
                user_data = user_in
            
            # Check for email uniqueness if email is being updated
            if "email" in user_data and user_data["email"] and user_data["email"] != user.email:
                existing_user = await self.get_by_email(user_data["email"])
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"User with email {user_data['email']} already exists")
            
            # Check for username uniqueness if username is being updated
            if "username" in user_data and user_data["username"] and user_data["username"] != user.username:
                existing_user = await self.get_by_username(user_data["username"])
                if existing_user and existing_user.id != user_id:
                    raise UserAlreadyExistsError(f"User with username {user_data['username']} already exists")
            
            if "password" in user_data and user_data["password"]:
                user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            
            await self._crud.update(pkey_val=user_id, model_data=user_data)
            user_in_db = await self._crud.get(pkey_val=user_id)
            return User.model_validate(user_in_db)
        except IntegrityError as e:
            raise UserAlreadyExistsError(f"User update failed due to integrity error: {str(e)}") from e
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error updating user: {str(e)}") from e

    async def delete(self: Self, user_id: int) -> None:
        """
        Delete a user.
        
        Raises:
            UserNotFoundError: If the user with the given ID doesn't exist.
            UserRepoError: If there's an error during user deletion.
        """
        try:
            # Check if user exists
            user = await self.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            
            await self._crud.delete(pkey_val=user_id)
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error deleting user: {str(e)}") from e

    async def get_by_id(self: Self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            user = await self._crud.get_or_none(pkey_val=user_id)
            if user:
                return User.model_validate(user)
            return None
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error getting user by ID: {str(e)}") from e

    async def get_by_email(self: Self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            users = await self._crud.get_by_field(field="email", field_value=email)
            if users and len(users) > 0:
                return User.model_validate(users[0])
            return None
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error getting user by email: {str(e)}") from e

    async def get_by_username(self: Self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            users = await self._crud.get_by_field(field="username", field_value=username)
            if users and len(users) > 0:
                return User.model_validate(users[0])
            return None
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error getting user by username: {str(e)}") from e

    async def get_all(self: Self) -> List[User]:
        """Get all users."""
        try:
            users_in_db = await self._crud.all()
            return [User.model_validate(user) for user in users_in_db]
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error getting all users: {str(e)}") from e

    async def authenticate(self: Self, username_or_email: str, password: str) -> User:
        """
        Authenticate a user.
        
        Returns:
            User: The authenticated user.
            
        Raises:
            AuthenticationError: If authentication fails.
            UserRepoError: If there's an error during authentication.
        """
        try:
            # Use a direct query to get the user with hashed_password in one go
            query = select(UserModel).where(
                (UserModel.email == username_or_email) | 
                (UserModel.username == username_or_email)
            )
            result = await self._session.execute(query)
            user_model = result.scalars().first()
            
            if not user_model:
                raise AuthenticationError("User not found")
            
            if not verify_password(password, user_model.hashed_password):
                raise AuthenticationError("Incorrect password")
            
            # Check if user is active
            if not user_model.is_active:
                raise AuthenticationError("User is inactive")
            
            # Convert to User schema (without hashed_password)
            return User.model_validate(user_model)
        except AuthenticationError:
            # Re-raise authentication errors
            raise
        except SQLAlchemyError as e:
            raise UserRepoError(f"Error during authentication: {str(e)}") from e 