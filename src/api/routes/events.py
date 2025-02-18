import json
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api.routes.auth import get_current_admin
from src.api.schemas import Event as EventDTO
from src.bot.messages import get_event_message
from src.bot.notification.notify import send_notification_all_users
from src.database import get_db
from src.database.models import Event
from src.database.queries import get_objects, create_object, update_object, delete_object

router = APIRouter()


@router.get("", response_model=list[EventDTO])
async def get_all_events(
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
        filters: Optional[str] = Query(None),
        offset: Optional[int] = Query(None),
        limit: Optional[int] = Query(None),
        order_by: Optional[str] = Query(None),
        desc: bool = Query(False),
):
    order_by_attr = getattr(Event, order_by) if order_by else None

    if filters:
        filters = json.loads(filters)

    events = await get_objects(
        db,
        Event,
        filters=filters,
        offset=offset,
        limit=limit,
        order_by=order_by_attr,
        desc=desc
    )

    return EventDTO.from_orm_list(events)


@router.post("", response_model=EventDTO)
async def create_event(
        event: EventDTO,
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    event = await create_object(db, Event, **event.model_dump())

    message = await get_event_message(event)

    message_text = message.text
    message.text = "НОВОЕ СОБЫТИЕ!\n\n" + message_text

    await send_notification_all_users(message)

    message.text = "Успей зарегистрироваться на игру! Остался 1 день!\n\n" + message_text

    await send_notification_all_users(
        message,
        event.end_registration_time - datetime.timedelta(days=1),
        f"notification_1_day_before_registration_by_event_id_{event.id}"
    )

    return EventDTO.from_orm(event)


@router.put("", response_model=EventDTO)
async def update_event(
        event: EventDTO,
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    if event.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="event_id is required")

    updated_event = await update_object(db, Event, event.id, **event.model_dump())

    message = await get_event_message(updated_event)

    message_text = message.text
    message.text = "Произошли изменения! Ознакомьтесь:\n\n" + message_text

    await send_notification_all_users(message)

    message.text = "Успей зарегистрироваться на игру! Остался 1 день!\n\n" + message_text

    await send_notification_all_users(
        message,
        updated_event.end_registration_time - datetime.timedelta(days=1),
        f"notification_1_day_before_registration_by_event_id_{event.id}"
    )

    return EventDTO.from_orm(updated_event)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
        event: EventDTO,
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    await delete_object(db, Event, event.id)
