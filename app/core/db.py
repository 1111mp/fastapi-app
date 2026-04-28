from collections.abc import AsyncGenerator
from time import perf_counter

import structlog
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = structlog.getLogger("postgres")


engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.ENVIRONMENT != "production",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # 30 minutes
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(perf_counter())


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    start_time = conn.info.setdefault("query_start_time", []).pop(-1)
    duration_ms = (perf_counter() - start_time) * 1000
    if duration_ms >= settings.SLOW_QUERY_THRESHOLD_MS:
        logger.warning(
            "slow_query_detected",
            duration_ms=round(duration_ms, 2),
            threshold_ms=settings.SLOW_QUERY_THRESHOLD_MS,
            statement=statement,
        )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def check_db_connection() -> None:
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))

        logger.info("Database connection established")
    except Exception as e:
        logger.error(
            "Database connection failed",
            error=str(e),
        )
        raise
