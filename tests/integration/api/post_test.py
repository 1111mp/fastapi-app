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
    create_data = {
        "title": "Read Target",
        "content": "Created before get.",
    }
    create_response = await authorized_client.post(
        f"{settings.API_V1_PREFIX}/posts/",
        json=create_data,
    )
    assert create_response.status_code == 200
    post_id = create_response.json()["id"]

    response = await authorized_client.get(
        f"{settings.API_V1_PREFIX}/posts/{post_id}",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == post_id
    assert "title" in payload
    assert "content" in payload


async def test_get_post_not_found(
    authorized_client: AsyncClient,
):
    response = await authorized_client.get(
        f"{settings.API_V1_PREFIX}/posts/999999",
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "Post not found"


async def test_create_post_unauthorized(
    unauthenticated_client: AsyncClient,
):
    response = await unauthenticated_client.post(
        f"{settings.API_V1_PREFIX}/posts/",
        json={"title": "No Auth", "content": "Should fail."},
    )

    assert response.status_code == 401


async def test_get_post_unauthorized(
    unauthenticated_client: AsyncClient,
):
    response = await unauthenticated_client.get(
        f"{settings.API_V1_PREFIX}/posts/1",
    )

    assert response.status_code == 401


async def test_create_post_validation_error(
    authorized_client: AsyncClient,
):
    response = await authorized_client.post(
        f"{settings.API_V1_PREFIX}/posts/",
        json={"title": "Missing content"},
    )

    assert response.status_code == 422
