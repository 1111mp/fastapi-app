from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.user import OAuthAccount, User


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, OAuthAccount]]:
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
