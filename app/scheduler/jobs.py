import structlog

logger = structlog.get_logger("scheduler.jobs")


async def async_job():
    logger.info("async_job started")


def sync_job():
    logger.info("sync_job started")
