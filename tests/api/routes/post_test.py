import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_create_post(
    authorized_client: AsyncClient,
):
    data = {
        "title": "Test Post",
        "content": "This is a test post.",
    }

    response = await authorized_client.post(
        f"{settings.API_V1_PREFIX}/posts/",
        json=data,
    )

    assert response.status_code == 200
    payload = response.json()
    assert "id" in payload
    assert payload["title"] == data["title"]
    assert payload["content"] == data["content"]


async def test_get_post(
    authorized_client: AsyncClient,
):
    id = 1

    response = await authorized_client.get(
        f"{settings.API_V1_PREFIX}/posts/{id}",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == id
    assert "title" in payload
    assert "content" in payload
