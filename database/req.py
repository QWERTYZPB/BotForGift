from database.models import User, Ticket, Channel, Event, async_session
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from typing import Optional, List
import asyncio
import random
import string

from datetime import datetime, timedelta



async def add_user(
    user_id: int,
    username: Optional[str] = None,
    referrer_id: Optional[int] = None,
    **kwargs
) -> Optional[User]:
    """
    Добавляет нового пользователя в базу данных.
    
    Args:
        user_id: Уникальный ID пользователя (обязательный)
        username: Имя пользователя (опционально)
        referrer_id: ID пригласившего пользователя (опционально)
        
    Returns:
        User: Объект пользователя или None при ошибке
    """
    try:
        async with async_session() as session:
            # Проверка существования реферера
            if referrer_id:
                referrer = await session.get(User, referrer_id)
                if not referrer:
                    print(f"Реферер с ID {referrer_id} не найден")
                    return None

            # Создание объекта пользователя
            new_user = User(
                user_id=user_id,
                username=username,
                referrer_id=referrer_id,
                created_at=datetime.now(),
                **kwargs
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            return new_user
            
    except IntegrityError as e:
        await session.rollback()
        print(f"Ошибка целостности: {e}")
        # Если пользователь уже существует, можно вернуть существующего
        existing_user = await session.get(User, user_id)
        return existing_user
        
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"Ошибка базы данных: {e}")
        return None
        
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None



async def get_user(user_id: int) -> Optional[User]:
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.user_id == user_id) 
        )
        return result.scalars().one()
    

async def update_user(user_id: int, **data) -> Optional[User]:
    try:
        async with async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None
                
            for key, value in data.items():
                setattr(user, key, value)
                
            await session.commit()
            await session.refresh(user)
            return user
    except SQLAlchemyError as e:
        print(f"Error updating user: {e}")
        await session.rollback()
        return None



async def add_ticket(
    user_id: int,
    event_id: int,  # Добавьте этот параметр
    number: str,
    **kwargs
) -> Optional[Ticket]:
    try:
        async with async_session() as session:
            ticket = Ticket(
                user_id=user_id,
                event_id=event_id,  # Укажите event_id
                number=number,
                **kwargs
            )
            session.add(ticket)
            await session.commit()
            return ticket
    except Exception as e:
        print(f"Error adding ticket: {e}")
        await session.rollback()
        return None
    
















async def generate_ticket_number(event_id: int, user_id: int) -> Optional[str]:
    """
    Генерирует уникальный номер билета для указанного события и пользователя.
    Формат: XXXXXX
    """
    try:
        async with async_session() as session:
            # Получаем событие с жадной загрузкой билетов
            event = await session.execute(
                select(Event)
                .where(Event.id == event_id)
            )

            if not event.scalars().first():
                print(f"Событие с ID {event_id} не найдено")
                return None

            # Генерируем уникальный номер
            while True:
                characters = string.ascii_uppercase + string.digits
    
                # Генерация билета из 6 случайных символов
                new_number = ''.join(random.choice(characters) for _ in range(6))
                
                # Проверяем уникальность номера
                exists = await session.execute(
                    select(Ticket)
                    .where(Ticket.number == new_number)
                )

                
                if not exists.scalars().first():
                    break

            # Создаем билет
            ticket = Ticket(
                number=new_number,
                user_id=user_id,
                event_id=event_id,
                created_at=datetime.now()
            )
            
            session.add(ticket)
            await session.commit()
            return new_number

    except SQLAlchemyError as e:
        print(f"Ошибка генерации билета: {e}")
        await session.rollback()
        return None








async def get_ticket(ticket_id: int) -> Optional[Ticket]:
    try:
        async with async_session() as session:
            return await session.get(Ticket, ticket_id)
    except SQLAlchemyError as e:
        print(f"Error getting ticket: {e}")
        return None




async def get_user_tickets(user_id: int) -> List[Ticket]:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Ticket)
                .where(Ticket.user_id == user_id)
                )
            return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error getting tickets: {e}")
        return []

# async def update_ticket(**data) -> Optional[Ticket]:
#     try:
#         async with async_session() as session:
#             ticket = await session.get(Ticket, data['user_id'])
#             if not ticket:
#                 return None

#             for key, value in data.items():
#                 setattr(ticket, key, value)
                
#             await session.commit()
#             await session.refresh(ticket)
#             return ticket
#     except SQLAlchemyError as e:
#         print(f"Error updating ticket: {e}")
#         await session.rollback()
#         return None

async def add_channel(channel_id:int, name: str, url: str, root_event_ids: str = None) -> Optional[Channel]:
    try:
        async with async_session() as session:
            channel = Channel(
                id=channel_id, 
                name=name, 
                url=url,
                root_event_ids=root_event_ids
            )

            session.add(channel)
            await session.commit()
            await session.refresh(channel)
            return channel
        
    except IntegrityError as e:
        await session.rollback()
        print(f"Channel already exists: {e}")
        return None
    except SQLAlchemyError as e:
        print(f"Error adding channel: {e}")
        await session.rollback()
        return None
    



async def get_channel(id: int) -> Optional[Channel]:
    try:
        async with async_session() as session:
            return await session.get(Channel, id)
    except SQLAlchemyError as e:
        print(f"Error getting channel: {e}")
        return None

async def get_all_channels() -> List[Channel]:
    try:
        async with async_session() as session:
            result = await session.execute(select(Channel))
            return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error getting channels: {e}")
        return []

async def update_channel(channel_id: int, **data) -> Optional[Channel]:
    try:
        async with async_session() as session:
            channel = await session.get(Channel, channel_id)
            if not channel:
                return None

            for key, value in data.items():
                setattr(channel, key, value)
                
            await session.commit()
            await session.refresh(channel)
            return channel
    except SQLAlchemyError as e:
        print(f"Error updating channel: {e}")
        await session.rollback()
        return None

async def create_event(
    name: str,
    description: Optional[str] = None,
    channels: List[Channel] = None,
    **kwargs
) -> Optional[Event]:
    try:
        async with async_session() as session:
            event = Event(
                name=name,
                description=description,
                **kwargs
            )
            
            if channels:
                event.channels.extend(channels)
                
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
    except SQLAlchemyError as e:
        print(f"Error creating event: {e}")
        await session.rollback()
        return None

async def get_active_events() -> List[Event]:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Event)
                .where(Event.is_active == True)
                .options(
                    selectinload(Event.channels),
                    selectinload(Event.users))
            )
            return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error getting active events: {e}")
        return []


async def get_event_winners(event_id: int) -> List[User]:
    async with async_session() as session:
        result = []

        event_ = await session.execute(
            select(Event)
            .where(
                Event.id == event_id
            )
        )
        event = event_.scalars().first()

        for ticket in event.tickets_event.split(','):
            if not ticket == '':    
                t = await get_ticket(int(ticket))
                if t.is_winner:
                    result.append(await get_user(t.user_id))


        return result


async def get_event(event_id: int) -> Optional[Event]:
    try:
        async with async_session() as session:
             result = await session.execute(
                select(Event)
                .where(Event.id == event_id)
        
            )
        return result.scalars().first()
    except SQLAlchemyError as e:
        print(f"Error getting event: {e}")
        return None

async def update_event_status(event_id: int, is_active: bool) -> Optional[Event]:
    try:
        async with async_session() as session:
            event = await session.get(Event, event_id)
            if not event:
                return None
                
            event.is_active = is_active
            await session.commit()
            await session.refresh(event)
            return event
    except SQLAlchemyError as e:
        print(f"Error updating event status: {e}")
        await session.rollback()
        return None



async def update_event(event_id: int, **kw) -> Optional[Event]:
    try:
        async with async_session() as session:
            event = await session.get(Event, event_id)
            if not event:
                return None
                
            for key, value in kw.items():
                setattr(event, key, value)
                
            await session.commit()
            await session.refresh(event)
            return event
    except SQLAlchemyError as e:
        print(f"Error updating event status: {e}")
        await session.rollback()
        return None



async def delete_event(event_id: int) -> bool:
    """
    Удаляет событие и все связанные с ним данные (билеты, связи с каналами)
    
    Args:
        event_id: ID события для удаления
        
    Returns:
        bool: True если удаление успешно, False в случае ошибки
    """
    try:
        async with async_session() as session:
            # Получаем событие со всеми связями
            q = await session.execute(
                select(Event)
                .where(Event.id == event_id)
            )
            
            event = q.scalars().first()

            if not event:
                print(f"Событие с ID {event_id} не найдено")
                return False

            # # Удаляем связанные билеты
            # if event.tickets:
            #     for ticket in event.tickets:
            #         await session.delete(ticket)

            # # Удаляем связи с каналами
            # if event.channels:
            #     event.channels.clear()

            # Удаляем само событие
            await session.delete(event)
            await session.commit()
            return True

    except SQLAlchemyError as e:
        print(f"Ошибка при удалении события: {e}")
        await session.rollback()
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False


async def test_data():
    
    # Создаем пользователей
    # user1 = await add_user(
    #     user_id=1060834219,
    #     username="pbadev",
    #     fullname='PBA'
    # )

    # Создаем каналы
    print(f"Создан канал: channel_b")

    channel_a = await add_channel(
        root_event_ids='1',
        channel_id=-1002141057588,
        name="PBA CODE",
        url="https://t.me/pbacode"
    )
    print(f"Создан канал: channel_a")

    channel_b = await add_channel(
        root_event_ids='1',
        channel_id=-1001744551956,
        name="PBA TEAM",
        url="https://t.me/pbateam"
    )

    # Создаем событие
    event = await create_event(
        name="Event X",
        description="Test Event X",
        channel_event_ids= ','.join(['-1002141057588', '-1001744551956']),
        win_count=5,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=7),
        is_active=True,
        owner_id=1060834219  # Используем существующий user_id
    )
    print(f"Создано событие: event x")
 
    # Создаем билеты
    # ticket1 = await add_ticket(
    #     user_id=1060834219,
    #     event_id=event.id,  # Добавляем event_id
    #     number="T1001-1"
    # )
    # print(f"Создан билет: ticket1")

    # ticket2 = await add_ticket(
    #     user_id=1001,
    #     number="T1001-2"
    # )
    # print(f"Создан билет: ticket2")

    # ticket3 = await add_ticket(
    #     user_id=1002,
    #     number="T1002-1"
    # )
    # print(f"Создан билет: ticket3")

    # ticket4 = await add_ticket(
    #     user_id=1003,
    #     number="T1003-1"
    # )
    # print(f"Создан билет: ticket4")
    
    # # Проверяем связи
    # test_user = await get_user(1002)
    # print(f"\nТестовый пользователь {test_user.user_id}:")
    # print(f"Реферер: {test_user.channels}")
    # # print(f"Билеты: {[t.number for t in test_user.tickets]}")

    # test_event = await get_event(1)
    # # print(f"\nТестовое событие {test_event.name}:")
    # # print(f"\nТестовое событие {test_event}:")
    # print(f"Каналы: {[c.name for c in test_event.channels]}")


# asyncio.run(test_data())


# asyncio.run(delete_event(2))