from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.post import PostCreate, PostPayload


def test_post_create_valid_payload() -> None:
    payload = PostCreate(title="Hello", content="World")
    assert payload.title == "Hello"
    assert payload.content == "World"


@pytest.mark.parametrize(
    ("title", "content"),
    [
        ("", "valid"),
        ("valid", ""),
    ],
)
def test_post_create_validation_error(title: str, content: str) -> None:
    with pytest.raises(ValidationError):
        PostCreate(title=title, content=content)


def test_post_payload_serializes_alias_and_datetime() -> None:
    now = datetime(2026, 1, 1, 12, 0)
    post = PostPayload(
        id=1,
        title="A",
        content="B",
        created_by_id=uuid4(),
        created_at=now,
        updated_at=now,
    )

    dumped = post.model_dump(by_alias=True)
    assert "createdById" in dumped
    assert isinstance(dumped["createdAt"], str)
    assert isinstance(dumped["updatedAt"], str)
    assert len(dumped["createdAt"]) == 19
    assert len(dumped["updatedAt"]) == 19
