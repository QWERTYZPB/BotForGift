from database import req
import config

from datetime import datetime, timedelta





async def _get_tickets(user: req.User):
    tickets = []
    for ticket in user.tickets:
        tickets.append({
            "id": ticket.id,
            "number": ticket.number,
            "createdAt": ticket.created_at.strftime("%d.%m.%Y, %H:%M")
            })
        
    return tickets


async def get_json_user_tickets(user_id: int):
    user = await req.get_user(user_id=user_id)

    
    return {
            "tickets": await _get_tickets(user=user)
        } 



async def get_json_event_time(eventId: int):
    event = await req.get_event(eventId)
    
    event_date = event.end_date

    date =  datetime.now() - timedelta(
        days=event_date.day,
        hours=event_date.hour,
        minutes=event_date.minute,
        seconds=event_date.second
    )
    
    return {
     
            "days": date.day,
            "hours": date.hour,
            "minutes": date.minute,
            "seconds": date.second
            
        }



async def get_json_user(userId, event_id):
    user = await req.get_user(user_id=userId)


    return {
        "id": user.user_id,
        "referralLink": f"{config.BOT_URL}?start={userId}-{event_id}", # t.me/<bot_username>?start=<parameter>
        "tickets": await _get_tickets(user=user)
        }




async def get_json_event_channels(eventId):
    event = await req.get_event(eventId)

    channels_event = event.channels

    channels = []

    for channel in channels_event:
        channels.append(
            {
                "id": channel.id,
                "name": channel.name,
                "url": channel.url,
                "isSubscribed": False # here will be another function
            }
        )

    return {
        "data": channels
        }





