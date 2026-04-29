from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel
from tzlocal import get_localzone

_LOCAL_TZ = get_localzone()


class PostPayload(BaseModel):
    """Schema for a post."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        validate_by_name=True,
    )

    id: int
    title: str
    content: str
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def format_datetime(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)

        return value.astimezone(_LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


class PostCreate(BaseModel):
    """Schema for creating a post."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
