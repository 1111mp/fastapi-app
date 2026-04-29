from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .jobs import async_job, sync_job

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        async_job,
        trigger=IntervalTrigger(seconds=30),
        id="async_job",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.add_job(
        sync_job,
        trigger=IntervalTrigger(seconds=30),
        id="sync_job",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()


def shutdown_scheduler() -> None:
    scheduler.shutdown()
