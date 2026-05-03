from sqlalchemy import Column, ForeignKey, Table

from .base import Base

user_role = Table(
    "user_role",
    Base.metadata,
    Column(
        "user_id",
        ForeignKey("user.id"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("role.id"),
        primary_key=True,
    ),
)

role_permission = Table(
    "role_permission",
    Base.metadata,
    Column(
        "role_id",
        ForeignKey("role.id"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        ForeignKey("permission.id"),
        primary_key=True,
    ),
)
