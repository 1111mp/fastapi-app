import structlog

from .provider import broker

logger = structlog.get_logger("workers.tasks")


@broker.task
async def send_email(email: str):
    logger.info("send_email", email=email)


@broker.task(schedule=[{"cron": "* * * * *"}])
async def scheduled_task():
    """
    Scheduled task that runs on a cron schedule.
    Scheduled to run every minute.
    """
    logger.info("scheduled_task")
