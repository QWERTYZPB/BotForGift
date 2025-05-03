from database.models import User, Ticket, Channel, Event, async_session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from typing import Optional, List






async def add_user(**data) -> Optional[User]:
    try:
        async with async_session() as session:
            user = User(**data)
            session.add(user)
            await session.commit()
            return user
    except IntegrityError:
        await session.rollback()
        return await update_user(user_id=data['id'], **data)
    except Exception as e:
        print(f"Error adding user: {e}")
        await session.rollback()
        return None

async def get_user(user_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

async def update_user(user_id: int, **data) -> Optional[User]:
    try:
        async with async_session() as session:
            result = await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**data)
                .returning(User)
            )
            await session.commit()
            return result.scalars().first()
    except Exception as e:
        print(f"Error updating user: {e}")
        await session.rollback()
        return None

async def add_ticket(**data) -> Optional[Ticket]:
    try:
        async with async_session() as session:
            # Проверка существования пользователя
            user = await get_user(data['user_id'])
            if not user:
                raise ValueError("User does not exist")
                
            ticket = Ticket(**data)
            session.add(ticket)
            await session.commit()
            return ticket
    except IntegrityError:
        await session.rollback()
        return await update_ticket(ticket_id=data['id'], **data)
    except Exception as e:
        print(f"Error adding ticket: {e}")
        await session.rollback()
        return None

async def get_ticket(ticket_id: int) -> Optional[Ticket]:
    async with async_session() as session:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalars().first()

async def get_user_tickets(user_id: int) -> List[Ticket]:
    async with async_session() as session:
        result = await session.execute(select(Ticket).where(Ticket.user_id == user_id))
        return result.scalars().all()

async def update_ticket(ticket_id: int, **data) -> Optional[Ticket]:
    try:
        async with async_session() as session:
            result = await session.execute(
                update(Ticket)
                .where(Ticket.id == ticket_id)
                .values(**data)
                .returning(Ticket)
            )
            await session.commit()
            return result.scalars().first()
    except Exception as e:
        print(f"Error updating ticket: {e}")
        await session.rollback()
        return None

async def add_channel(**data) -> Optional[Channel]:
    try:
        async with async_session() as session:
            channel = Channel(**data)
            session.add(channel)
            await session.commit()
            return channel
    except IntegrityError:
        await session.rollback()
        return await update_channel(channel_id=data['id'], **data)
    except Exception as e:
        print(f"Error adding channel: {e}")
        await session.rollback()
        return None

async def get_channel(channel_id: int) -> Optional[Channel]:
    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.id == channel_id))
        return result.scalars().first()

async def get_all_channels() -> List[Channel]:
    async with async_session() as session:
        result = await session.execute(select(Channel))
        return result.scalars().all()

async def update_channel(channel_id: int, **data) -> Optional[Channel]:
    try:
        async with async_session() as session:
            result = await session.execute(
                update(Channel)
                .where(Channel.id == channel_id)
                .values(**data)
                .returning(Channel)
            )
            await session.commit()
            return result.scalars().first()
    except Exception as e:
        print(f"Error updating channel: {e}")
        await session.rollback()
        return None






async def create_event(**data) -> Optional[Event]:
    try:
        async with async_session() as session:
            event = Event(**data)
            session.add(event)
            await session.commit()
            return event
    except Exception as e:
        print(f"Error creating event: {e}")
        await session.rollback()
        return None

async def get_active_events() -> List[Event]:
    async with async_session() as session:
        result = await session.execute(
            select(Event).where(Event.is_active == True)
        )
        return result.scalars().all()



async def get_event(event_id) -> Event:
    async with async_session() as session:
        result = await session.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalars().one()




async def update_event_status(event_id: int, is_active: bool) -> bool:
    try:
        async with async_session() as session:
            await session.execute(
                update(Event)
                .where(Event.id == event_id)
                .values(is_active=is_active)
            )
            await session.commit()
            return True
    except Exception as e:
        print(f"Error updating event status: {e}")
        await session.rollback()
        return False

