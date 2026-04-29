import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import structlog
from asgi_correlation_id import correlation_id
from structlog.types import Processor
from structlog.typing import EventDict

from app.core.config import settings


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return bool(record.levelno <= self.max_level)


def add_correlation_id(_: Any, __: str, event_dict: EventDict) -> EventDict:
    """Inject correlation ID into logs."""
    request_id = correlation_id.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging() -> None:
    """Configure structlog + stdlib logging."""

    # =====================
    # 1. shared processors
    # =====================
    base_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(
            fmt="%Y-%m-%d %H:%M:%S",
            utc=False,
        ),
        add_correlation_id,
        structlog.stdlib.PositionalArgumentsFormatter(),
    ]

    # =====================
    # 2. renderer split
    # =====================
    console_renderer = structlog.dev.ConsoleRenderer()
    file_renderer = structlog.processors.JSONRenderer()

    if settings.ENVIRONMENT == "production":
        base_processors.append(structlog.processors.dict_tracebacks)

    # =====================
    # 3. structlog config
    # =====================
    structlog.configure(
        processors=[
            *base_processors,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # =====================
    # 4. console formatter
    # =====================
    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=base_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            console_renderer,
        ],
    )

    # =====================
    # 5. file formatter (JSON)
    # =====================
    file_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=base_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            file_renderer,
        ],
    )

    # =====================
    # 6. console handler
    # =====================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # =====================
    # 7. file handler (rotating)
    # =====================
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=14,  # 保留 14 个文件
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(settings.LOGGER_LEVEL)
    file_handler.addFilter(MaxLevelFilter(logging.WARNING))

    error_log_file = log_dir / "app-error.log"
    error_file_handler = RotatingFileHandler(
        filename=error_log_file,
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=14,  # 保留 14 个文件
        encoding="utf-8",
    )
    error_file_handler.setFormatter(file_formatter)
    error_file_handler.setLevel(logging.ERROR)

    # =====================
    # 8. root logger
    # =====================
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.LOGGER_LEVEL)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)

    # =====================
    # 9. uvicorn logging unify
    # =====================
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
