from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.utils.utils import login_superuser


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="module")
async def authorized_client(
    async_client: AsyncClient,
) -> AsyncClient:
    await login_superuser(async_client)
    return async_client
