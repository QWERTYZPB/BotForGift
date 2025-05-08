from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import ForeignKey, String, BigInteger, Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column


import asyncio
from datetime import datetime
from typing import List, Optional

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass



# Ассоциативная таблица для связи User и Event
user_event = Table(
    "user_event",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.user_id")),
    Column("event_id", BigInteger, ForeignKey("events.id")),
)

user_channel = Table(
    "user_channel",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.user_id")),
    Column("channel_id", BigInteger, ForeignKey("channels.id"))  # Исправлено название колонки
)

channel_event = Table(
    "channel_event",
    Base.metadata,
    Column("channel_id", BigInteger, ForeignKey("channels.id")),
    Column("event_id", BigInteger, ForeignKey("events.id")),
)

channel_event_association = Table(
    "channel_event_association",
    Base.metadata,
    Column("channel_id", BigInteger, ForeignKey("channels.id")),
    Column("event_id", BigInteger, ForeignKey("events.id")),
)


class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fullname: Mapped[str] = mapped_column(String(200), nullable=True)  #me: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    
    # Отношения
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="user")
    referrals: Mapped[List["User"]] = relationship(back_populates="referrer")
    referrer: Mapped[Optional["User"]] = relationship(back_populates="referrals", remote_side=[user_id])

    events: Mapped[List["Event"]] = relationship(secondary=user_event, back_populates="users")  # Исправлено
    channels: Mapped[List["Channel"]] = relationship(secondary=user_channel, back_populates="subscribers")  # Исправлено


class Ticket(Base):
    __tablename__ = "tickets"
   
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"))  # Добавлено
    
    user: Mapped["User"] = relationship(back_populates="tickets")
    event: Mapped["Event"] = relationship(back_populates="tickets")  # Добавлено


class Channel(Base):
    __tablename__ = "channels"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(200))
    
    # Отношение к User
    subscribers: Mapped[List["User"]] = relationship(  # Новое отношение
        secondary=user_channel, 
        back_populates="channels"
    )
    
    # Отношение к Event
    events: Mapped[List["Event"]] = relationship(
        secondary=channel_event_association,
        back_populates="channels"
    )

    # # Отношение к Event через промежуточную таблицу
    # events: Mapped[List["Event"]] = relationship(
    #     secondary=channel_event_association,
    #     back_populates="channels",
    #     # lazy="selectin"  # Для асинхронной работы
    # )



class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    media: Mapped[Optional[str]] = mapped_column(Text)
    win_count: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Исправленные отношения
    users: Mapped[List["User"]] = relationship(
        secondary=user_event, 
        back_populates="events"
    )
    
    # Отношение к Channel
    channels: Mapped[List["Channel"]] = relationship(
        secondary=channel_event_association,
        back_populates="events",
        lazy="selectin"
    )
    tickets: Mapped[List["Ticket"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan"
    )

async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())