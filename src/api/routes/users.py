import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.routes.auth import get_current_admin
from src.api.schemas import User as UserDTO
from src.database import get_db
from src.database.models import User
from src.database.queries import get_objects

router = APIRouter()


@router.get("", response_model=list[UserDTO])
async def get_all_users(
        current_admin: str = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
        filters: Optional[str] = Query(None),
        offset: Optional[int] = Query(None),
        limit: Optional[int] = Query(None),
        order_by: Optional[str] = Query(None),
        desc: bool = Query(False),
):
    order_by_attr = getattr(User, order_by) if order_by else None

    if filters:
        filters = json.loads(filters)

    users = await get_objects(
        db,
        User,
        filters=filters,
        offset=offset,
        limit=limit,
        order_by=order_by_attr,
        desc=desc
    )

    return UserDTO.from_orm_list(users)
