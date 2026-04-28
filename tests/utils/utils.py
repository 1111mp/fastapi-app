from httpx import AsyncClient

from app.core.config import settings


async def login_superuser(async_client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = await async_client.post(
        f"{settings.API_V1_PREFIX}/auth/jwt/login",
        data=login_data,
    )
    assert response.status_code == 204
    auth_token = response.cookies.get("fastapiusersauth")
    assert auth_token is not None
    # async_client.cookies.set("fastapiusersauth", auth_token)
