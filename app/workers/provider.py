import taskiq_fastapi
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core.config import settings

broker = RedisStreamBroker(
    settings.REDIS_DSN,
).with_result_backend(
    RedisAsyncResultBackend(
        settings.REDIS_DSN,
        keep_results=False,
        result_ex_time=60,  # one minute
        prefix_str=settings.PROJECT_NAME,
    ),
)

taskiq_fastapi.init(broker, "app.main:app")
