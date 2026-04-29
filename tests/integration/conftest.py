from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_transaction() -> AsyncGenerator[None]:
    """Wrap each test in a database transaction that is rolled back after the test completes."""
    from app.core.db import async_session, get_async_session
    from app.main import app

    async with async_session() as session:
        original_commit = session.commit

        async def _test_commit() -> None:
            await session.flush()

        session.commit = _test_commit  # type: ignore

        async def _override_get_async_session() -> AsyncGenerator[AsyncSession]:
            yield session

        app.dependency_overrides[get_async_session] = _override_get_async_session

        try:
            yield
        finally:
            session.commit = original_commit  # type: ignore
            await session.rollback()
            app.dependency_overrides.clear()
