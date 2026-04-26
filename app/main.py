from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings
from app.core.db import check_db_connection
from app.core.exceptions import global_exception_handler
from app.core.logging import setup_logging
from app.core.redis import redis_client
from app.scheduler.scheduler import shutdown_scheduler, start_scheduler
from app.workers.provider import broker


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """
    Application lifespan manager.
    """
    # Set up logging
    setup_logging()

    # Postgres
    await check_db_connection()
    # Redis
    await redis_client.init(settings.REDIS_DSN)
    # Scheduler
    start_scheduler()
    # Workers
    if not broker.is_worker_process:
        await broker.startup()

    yield

    shutdown_scheduler()
    if not broker.is_worker_process:
        await broker.shutdown()
    await redis_client.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id,
)

app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.assemble_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
    max_age=3600,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_config=None,
    )
