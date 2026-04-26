from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampsMixin:
    """
    Simple created at and updated at timestamps. Mix them into your model:

    >>> class MyModel(TimestampsMixin, Base):
    >>>    pass
    """

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
