from datetime import datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.date import DateTrigger

from src.bot.messages import Message
from src.bot.notification import scheduler, logger
from src.database import get_db
from src.database.models import User
from src.database.queries import get_objects


async def send_notification(telegram_id: int, message: Message):
    from src.bot import bot

    if message.image_url:
        await bot.send_photo(
            telegram_id,
            message.image_url,
            caption=message.text,
            reply_markup=message.keyboard,
        )

    else:
        await bot.send_message(
            telegram_id,
            message.text,
            reply_markup=message.keyboard,
        )

    logger.info(f"Sending notification for {telegram_id}. Message: {message.to_dict()}")


def remove_notification(job_id: str):
    if job_id:
        try:
            scheduler.remove_job(job_id)
        except JobLookupError:
            pass


def create_notification(telegram_id: int, message: Message, date: datetime, job_id: str = None):
    remove_notification(job_id)

    scheduler.add_job(
        send_notification,
        trigger=DateTrigger(run_date=date),
        args=[telegram_id, message],
        id=job_id,
    )

    logger.info(f"Notification for {telegram_id} scheduled at {date}. Message: {message.to_dict()}")


async def send_notification_all_users(message: Message, date: datetime = None, job_id: str = None):
    async for session in get_db():

        users = await get_objects(session, User)

        for user in users:
            if date is None:
                await send_notification(user.telegram_id, message)

            else:
                create_notification(user.telegram_id, message, date, job_id)
