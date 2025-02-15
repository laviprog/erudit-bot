from datetime import datetime
from typing import Type, TypeVar, Optional

from pydantic import BaseModel, ConfigDict

from src.database.models import Status


class LoginRequest(BaseModel):
    username: str
    password: str


T = TypeVar("T", bound="BaseModel")


class BaseDTO(BaseModel):
    @classmethod
    def from_orm(cls: Type[T], obj) -> T:
        return cls.model_validate(obj, from_attributes=True)

    @classmethod
    def from_orm_list(cls: Type[T], objs) -> list[T]:
        return [cls.model_validate(obj, from_attributes=True) for obj in objs]


class Event(BaseDTO):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_time: Optional[datetime] = None
    end_registration_time: Optional[datetime] = None
    location: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseDTO):
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    telegram_id: Optional[int] = None
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Application(BaseDTO):
    id: Optional[int] = None
    captain_id: Optional[int] = None
    team_name: Optional[str] = None
    team_size: Optional[int] = None
    status: Optional[Status] = None
    event_id: Optional[int] = None
    captain: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)


class Message(BaseDTO):
    text: str
    image_id: Optional[int] = None
    image_url: Optional[str] = None
    video_id: Optional[int] = None
    video_url: Optional[str] = None


class Notification(BaseDTO):
    telegram_id: Optional[int] = None
    message: Optional[Message]
    time: Optional[datetime] = None
    event_id: Optional[int] = None
