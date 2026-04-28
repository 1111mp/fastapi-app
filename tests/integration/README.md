# Integration tests with automatic rollback

`tests/integration/conftest.py` provides one autouse fixture: `db_transaction`.

How it works:

1. Create a dedicated `AsyncSession` for each test.
2. Override FastAPI `get_async_session` dependency to force API code to use this session.
3. Monkeypatch `session.commit()` to `session.flush()` during tests.
4. Roll back at test teardown so inserted/updated/deleted data does not persist.

This pattern keeps fixtures simple while preventing test data from being written permanently.

## Run integration tests only

```bash
uv run pytest -m integration
```

## How to mark integration tests

For files like `tests/integration/api/post_test.py`, add module-level marker:

```python
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]
```

Or mark each test function individually:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_post(...):
    ...
```

Run commands:

- only integration: `uv run pytest -m integration`
- exclude integration: `uv run pytest -m "not integration"`
- run one file: `uv run pytest tests/integration/api/post_test.py -m integration`
