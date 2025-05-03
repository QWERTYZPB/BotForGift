from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import ForeignKey, BigInteger, String, Boolean, Integer, DateTime, Text

import asyncio
from datetime import datetime
from typing import List, Optional

engine = create_async_engine(url="sqlite+aiosqlite:///database/db.sqlite3")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    
    # Реферальная система
    referral_code: Mapped[Optional[str]] = mapped_column(String(10), unique=True)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.user_id"), nullable=True)
    
    # Отношения
    tickets: Mapped[List["Ticket"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    referrals: Mapped[List["User"]] = relationship(back_populates="referrer")
    referrer: Mapped[Optional["User"]] = relationship(back_populates="referrals", remote_side=[id])

class Ticket(Base):
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Внешний ключ для пользователя
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"))
    
    # Отношения
    user: Mapped["User"] = relationship(back_populates="tickets")


class Channel(Base):
    __tablename__ = "channels"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(200))


class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    media: Mapped[Optional[str]] = mapped_column(Text)

    users: Mapped[List["User"]] = relationship(back_populates="events", cascade="all, delete-orphan")
    channels: Mapped[List["Channel"]] = relationship(back_populates="events", cascade="all, delete-orphan")
    win_count: Mapped[int] = mapped_column(Integer)

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # # Связи
    # participants: Mapped[List["User"]] = relationship(
    #     secondary="event_participants",
    #     back_populates="events"
    # )
    # required_channels: Mapped[List["Channel"]] = relationship(
    #     secondary="event_requirements",
    #     back_populates="events"
    # )



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())