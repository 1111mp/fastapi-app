from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListRedisScheduleSource

from app.core.config import settings

from .provider import broker

redis_source = ListRedisScheduleSource(
    settings.REDIS_DSN,
    prefix=f"{settings.PROJECT_NAME}.schedule",
)


scheduler = TaskiqScheduler(
    broker,
    [
        # Dynamic schedule source. To add tasks dynamically.
        redis_source,
        # Label schedule source. To schedule tasks with labels.
        LabelScheduleSource(broker),
    ],
)
