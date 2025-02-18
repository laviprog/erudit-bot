import datetime
import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routes.auth import get_current_admin
from src.api.schemas import Application as ApplicationDTO
from src.bot.messages import get_application_message, get_message_before_event
from src.bot.notification.notify import create_notification, send_notification
from src.database import get_db
from src.database.models import Application, User, Event
from src.database.queries import update_object, get_object_by_id, get_objects

router = APIRouter()


@router.put("", response_model=ApplicationDTO)
async def put_application(
        application: ApplicationDTO,
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    application_status = application.status

    updated_application = await update_object(db, Application, application.id, **application.model_dump())

    user = await get_object_by_id(db, User, updated_application.captain_id)
    event = await get_object_by_id(db, Event, updated_application.event_id)

    message = await get_application_message(updated_application, event)

    if application_status:
        if application_status == "approved":
            message.text = "Ваша заявка на участие в событии одобрена!\n\n" + message.text

            create_notification(
                telegram_id=user.id,
                message=await get_message_before_event(event),
                date=event.event_time - datetime.timedelta(days=1),
                job_id=f"notification_approved_application_{application.id}"
            )

        elif application_status == "declined":
            message.text = "Ваша заявка на участие в событии отклонена.\nСвяжитесь с организаторами!\n\n" + message.text

        await send_notification(
            user.id,
            message,
        )

    return ApplicationDTO.from_orm(updated_application)


@router.get("")
async def get_applications(
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
        filters: Optional[str] = Query(None),
        offset: Optional[int] = Query(None),
        limit: Optional[int] = Query(None),
        order_by: Optional[str] = Query(None),
        desc: bool = Query(False),
):
    order_by_attr = getattr(Application, order_by) if order_by else None

    if filters:
        filters = json.loads(filters)

    applications = await get_objects(
        db,
        Application,
        filters=filters,
        offset=offset,
        limit=limit,
        order_by=order_by_attr,
        desc=desc
    )

    return ApplicationDTO.from_orm_list(applications)
