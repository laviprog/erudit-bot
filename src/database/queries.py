from typing import Type, TypeVar, Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.database.models import Admin, Event

T = TypeVar("T")


async def get_object_by_id(
        session: AsyncSession,
        model: Type[T],
        obj_id: int
) -> Optional[T]:
    result = await session.execute(
        select(model)
        .filter(model.id == obj_id)
    )

    return result.scalar_one_or_none()


async def get_objects(
        session: AsyncSession,
        model: Type[T],
        filters: Optional[dict] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[InstrumentedAttribute] = None,
        desc: bool = False
) -> List[T]:
    query = select(model)

    if filters:
        query = query.filter_by(**filters)

    if order_by:
        query = query.order_by(order_by.desc() if desc else order_by)

    result = await session.execute(
        query
        .offset(offset)
        .limit(limit)
    )

    return list(result.scalars().all())


async def create_object(
        session: AsyncSession,
        model: Type[T],
        **data
) -> T:
    new_object = model(**data)
    session.add(new_object)

    await session.commit()
    await session.refresh(new_object)

    return new_object


async def update_object(
        session: AsyncSession,
        model: Type[T],
        obj_id: int,
        **kwargs
) -> Optional[T]:
    obj = await get_object_by_id(session, model, obj_id)

    if not obj:
        return None

    for key, value in kwargs.items():
        if value is not None:
            setattr(obj, key, value)

    await session.commit()
    await session.refresh(obj)

    return obj


async def delete_object(session: AsyncSession, model: Type[T], obj_id: int) -> bool:
    obj = await get_object_by_id(session, model, obj_id)

    if obj:
        await session.delete(obj)
        await session.commit()
        return True

    return False


async def get_admin_by_username(session: AsyncSession, username: str) -> Optional[Admin]:
    result = await get_objects(session, Admin, filters={"username": username})
    return next(iter(result), None)


async def get_current_events(session: AsyncSession):
    result = await session.execute(
        select(Event)
        .where(Event.event_time >= func.now())
        .order_by(Event.event_time)
    )
    return result.scalars().all()
