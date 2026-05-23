import asyncio

from celery.schedules import crontab

from sa.database import SessionLocal
from sa.operations.refresh_tokens import delete_expired_refresh_tokens

from .app import app


@app.task(ignore_result=True)
def clear_expired_refresh_tokens():
    async def run_asyncronously():
        async with SessionLocal() as session:
            await delete_expired_refresh_tokens(session)
            await session.commit()

    asyncio.run(run_asyncronously())


app.conf.beat_schedule = {
    "clear-expired-refresh-tokens-daily": {
        "task": "celery_tasks.refresh_cleanup.clear_expired_refresh_tokens",
        "schedule": crontab(hour=3, minute=0),
    },
}
