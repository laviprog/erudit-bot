from enum import Enum

from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=True)
    telegram_id = Column(BigInteger, nullable=True)
    phone_number = Column(String, nullable=True)

    applications = relationship("Application", back_populates="captain", cascade="all, delete")


class Event(Base):
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_time = Column(DateTime, nullable=False)
    end_registration_time = Column(DateTime, nullable=True)
    location = Column(String, nullable=False)
    image_url = Column(String, nullable=True)

    applications = relationship("Application", back_populates="event", cascade="all, delete")


class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"


class Application(Base):
    __tablename__ = "applications"

    id = Column(BigInteger, primary_key=True, index=True)
    captain_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"))
    team_name = Column(String, nullable=False)
    team_size = Column(Integer, nullable=False)
    status = Column(SQLEnum(Status), default=Status.PENDING, nullable=True)

    captain = relationship("User", back_populates="applications")
    event = relationship("Event", back_populates="applications")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
