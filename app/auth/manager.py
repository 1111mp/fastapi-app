import uuid

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.core.config import settings
from app.db.user import get_user_db
from app.models.user import User


# Reference: https://fastapi-users.github.io/fastapi-users/latest/configuration/user-manager/
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Custom user manager for the application."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
