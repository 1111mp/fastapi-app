from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from .link_tables import role_permission
from .mixins.timestamps import TimestampsMixin
from .role import Role


class Permission(TimestampsMixin, Base):
    """Permission model."""

    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        secondary=role_permission,
        back_populates="permissions",
    )
