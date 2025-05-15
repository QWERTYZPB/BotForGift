from aiogram.types import TelegramObject, ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner
from aiogram import Bot

from typing import List


from database import req
from database.models import Ticket, Channel
from settings import request_utils

import config

from datetime import datetime, timedelta








async def get_json_subscriptions(bot: Bot, user_tg_id: int, channels: List[Channel]):
    result = {
        "allSubscribed": False,
        "details": []
    }

    for channel in channels:
        if channel.is_active:
            
            if not request_utils.check_subscription(user_tg_id, channel.id, config.BOT_TOKEN):
                image = request_utils.get_channel_image(
                            bot_token=config.BOT_TOKEN,
                            channel_id=channel.id
                        )
                if image:
                    if len(image) == 2:
                        image = request_utils.bytes_to_data_url(image[0])
                    else:
                        image = '/friends.webp'
                else:
                    image = '/friends.webp'

                result['details'].append(
                    {
                        "channelId": channel.id,
                        "image_data": image,
                        "channelName": channel.name,
                        "channelUrl": channel.url,
                        "isSubscribed": False
                    }
                )
            
    if len(result['details']) == 0:
        result['allSubscribed'] = True

    return result




async def user_tickets_not_in_event(user: req.User, event: req.Event):

    if not user.tickets_ids:
        return True
    
    if not event.tickets_event:
        return True

    
    user_tickets_nums = [i.number for i in await req.get_user_tickets(user.user_id)]
    event_tickets = []
    
    for ticket in event.tickets_event.split(','):
        if not ticket == '':
            event_tickets.append(
                (await req.get_ticket(int(ticket))).number
            )

    for user_ticket in user_tickets_nums:
        if user_ticket in event_tickets:
            return False
        
    return True











async def _get_tickets(user: req.User):
    tickets = []
    for ticket_id in user.tickets_ids.split(','):
        if not ticket_id == '':
            try:
                ticket = await req.get_ticket(int(ticket_id))

                tickets.append({
                    "id": ticket.id,
                    "number": ticket.number,
                    "createdAt": ticket.created_at.strftime("%d.%m.%Y, %H:%M")
                    })
            except:
                pass
        
    return tickets


async def get_json_user_tickets(user_id: int):
    user = await req.get_user(user_id=user_id)

    
    return {
            "tickets": await _get_tickets(user=user)
        } 



async def get_json_event_time(eventId: int):
    print(eventId)
    event = await req.get_event(int(eventId))
    
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



async def get_json_event_winners(eventId: int):
    print(eventId)
    event_winners = await req.get_event_winners(int(eventId))
    # print(event_winners)
    result = []
    
    for i, winner in enumerate(event_winners):
        image_url = request_utils.get_channel_image(
            bot_token=config.BOT_TOKEN, channel_id=winner.user_id)
        if len(image_url) == 2:
            image_url = request_utils.bytes_to_data_url(image_url[0])
        
        tickets = [await req.get_ticket(int(ticket_id)) for ticket_id in winner.tickets_ids.split(',') if ticket_id!='']
        
        result.append(
            {
                'id':i,
                'ticket': tickets[0].number,
                'name':winner.fullname,
                'image_url': image_url
            }
        )

    # print('res', result)

    return result




    


async def get_json_user(userId, event_id):
    user = await req.get_user(user_id=userId)


    return {
        "id": user.user_id,
        "referralLink": f"{config.BOT_URL}?start={userId}-{event_id}", # t.me/<bot_username>?start=<parameter>
        "tickets": await _get_tickets(user=user)
        }




async def get_json_event_channels(eventId):
    event = await req.get_event(eventId)

    channels_event = []

    for channel_id in event.channel_event_ids.split(','):
        if not channel_id == '':
            channels_event.append(await req.get_channel(int(channel_id)))

    channels = []

    for channel in channels_event:
        if channel.is_active:
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





