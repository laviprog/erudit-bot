from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.routes.auth import get_current_admin
from src.api.schemas import Notification
from src.bot.messages import Message
from src.bot.notification.notify import create_notification, send_notification, send_notification_all_users
from src.database import get_db
from src.database.models import Application, User
from src.database.queries import get_objects, get_object_by_id

router = APIRouter()


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def notify(
        request: Notification,
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    message = Message(**request.message.model_dump())

    if request.telegram_id:
        if request.time:
            create_notification(request.telegram_id, message, request.time)

        else:
            await send_notification(request.telegram_id, message)

    elif request.event_id:

        applications = await get_objects(
            db,
            Application,
            filters={
                "event_id": request.event_id,
                "status": "approved"
            }
        )

        if applications:
            for application in applications:
                user = await get_object_by_id(db, User, application.captain_id)

                if request.time:
                    create_notification(user.telegram_id, message, request.time)

                else:
                    await send_notification(user.telegram_id, message)

    else:
        await send_notification_all_users(message, request.time)
