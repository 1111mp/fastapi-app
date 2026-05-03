from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from .link_tables import role_permission, user_role
from .mixins.timestamps import TimestampsMixin

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User


class Role(TimestampsMixin, Base):
    """Role model."""

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list[User]] = relationship(
        secondary=user_role,
        back_populates="roles",
    )
    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permission,
        back_populates="roles",
        lazy="selectin",
    )
