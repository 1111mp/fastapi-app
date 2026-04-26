from typing import TYPE_CHECKING

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy.orm import Mapped, relationship

from app.db.base import Base

from .mixins.timestamps import TimestampsMixin

if TYPE_CHECKING:
    from app.models.post import Post


class OAuthAccount(TimestampsMixin, SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(TimestampsMixin, SQLAlchemyBaseUserTableUUID, Base):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )

    posts: Mapped[list["Post"]] = relationship(back_populates="created_by")
