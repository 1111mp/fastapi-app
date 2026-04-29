import asyncio

import structlog
from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.db import check_db_connection
from app.core.redis import redis_client

logger = structlog.get_logger("observability")


def setup_metrics(app: FastAPI) -> None:
    """Set up Prometheus metrics collection and exposition"""
    if not settings.METRICS_ENABLED:
        logger.info("Metrics collection is disabled")
        return

    Instrumentator(
        excluded_handlers=["/healthz", "/readyz"],
    ).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
        tags=["Ops"],
    )


def build_ops_router() -> APIRouter:
    """Build the operations router with health and readiness endpoints"""
    router = APIRouter(tags=["Ops"])

    @router.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/readyz")
    async def readyz() -> JSONResponse:
        checks: dict[str, object] = {
            "database": "ok",
            "redis": "ok",
        }
        status_code = status.HTTP_200_OK

        async def check_db() -> int:
            try:
                await check_db_connection()
            except Exception as exc:
                checks["database"] = f"failed: {exc}"
                return status.HTTP_503_SERVICE_UNAVAILABLE
            return status.HTTP_200_OK

        async def check_redis() -> int:
            try:
                redis = await redis_client.get_redis()
                await redis.ping()  # type: ignore
            except Exception as exc:
                checks["redis"] = f"failed: {exc}"
                return status.HTTP_503_SERVICE_UNAVAILABLE
            return status.HTTP_200_OK

        db_status, redis_status = await asyncio.gather(
            check_db(),
            check_redis(),
        )

        if db_status != status.HTTP_200_OK:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        if redis_status != status.HTTP_200_OK:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        payload = {
            "status": "ready" if status_code == status.HTTP_200_OK else "not_ready",
            "checks": checks,
        }

        return JSONResponse(content=payload, status_code=status_code)

    return router
