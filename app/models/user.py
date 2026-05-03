from typing import TYPE_CHECKING

from fastapi_users.db import (
    SQLAlchemyBaseOAuthAccountTableUUID,
    SQLAlchemyBaseUserTableUUID,
)
from sqlalchemy.orm import Mapped, relationship

from .base import Base
from .link_tables import user_role
from .mixins.timestamps import TimestampsMixin

if TYPE_CHECKING:
    from .post import Post
    from .role import Role


class OAuthAccount(TimestampsMixin, SQLAlchemyBaseOAuthAccountTableUUID, Base):
    pass


class User(TimestampsMixin, SQLAlchemyBaseUserTableUUID, Base):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount",
        lazy="joined",
    )

    roles: Mapped[list[Role]] = relationship(
        secondary=user_role,
        back_populates="users",
        lazy="selectin",
    )
    posts: Mapped[list[Post]] = relationship(
        back_populates="created_by",
    )

    @property
    def is_admin(self) -> bool:
        """Check if the user has the admin role."""
        return any(role.name == "admin" for role in self.roles)
