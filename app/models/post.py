from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from .mixins.timestamps import TimestampsMixin

if TYPE_CHECKING:
    from app.models.user import User


class Post(TimestampsMixin, Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    created_by: Mapped[User] = relationship(back_populates="posts")
