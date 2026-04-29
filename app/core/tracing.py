import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from app.core.config import settings
from app.core.db import engine

logger = structlog.get_logger("tracing")


def setup_tracing(app: FastAPI) -> None:
    """Set up OpenTelemetry tracing for FastAPI, SQLAlchemy, and Redis."""
    if not settings.OTEL_ENABLED:
        logger.info("OpenTelemetry tracing is disabled")
        return

    tracer_provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": settings.PROJECT_NAME,
                "service.version": settings.VERSION,
            }
        ),
        sampler=TraceIdRatioBased(0.1),  # Sample 10% of traces, adjust as needed
    )

    exporter: SpanExporter
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        logger.info(
            "Configuring OTLP exporter",
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=settings.OTEL_EXPORTER_OTLP_INSECURE,
        )
        exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            insecure=settings.OTEL_EXPORTER_OTLP_INSECURE,
        )
    else:
        exporter = ConsoleSpanExporter()

    tracer_provider.add_span_processor(
        BatchSpanProcessor(exporter),
    )
    trace.set_tracer_provider(tracer_provider)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    RedisInstrumentor().instrument()

    FastAPIInstrumentor().instrument_app(
        app,
        excluded_urls="/healthz,/readyz,/metrics",
    )

    logger.info("OpenTelemetry tracing is enabled")
