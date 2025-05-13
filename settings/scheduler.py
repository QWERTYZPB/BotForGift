from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import types
import config
from settings import lexicon, user_kb

from database import req
from datetime import timedelta

import datetime,  logging as lg

import random





async def make_raffle(event: req.Event):
    win_count = event.win_count
    if not event.tickets_event:
        return
    

    event_tickets = [await req.get_ticket(int(ticket)) for ticket in event.tickets_event.split(',') if ticket!='']

    slave_tickets = [ticket for ticket in event_tickets if not ticket.is_winner]

    # 😈
    root_winners = [ticket for ticket in event_tickets if ticket.is_winner]

    if win_count > len(event_tickets):
        win_count = len(event_tickets)

    try:
        winners = random.choices(population=slave_tickets, k=win_count - len(root_winners))
    except IndexError:
        winners = []

    # 😈
    winners.extend(root_winners)

    for winner in winners:
        await req.update_ticket(winner.id, is_winner=True)

    # 😈
    return winners 








class Scheduler:
    def __init__(self):

        self.scheduler = AsyncIOScheduler()


    async def update_posts(self, bot: config.Bot):
        pass    

    
    async def check_end_date(self, bot: config.Bot):

        events = await req.get_active_events()

        for event in events:
            if datetime.datetime.now() > event.end_date and event.is_active:
                
                tickets_winners = await make_raffle(event)

                if event.user_event_ids:
                    user_count = len(event.user_event_ids.split(','))
                else:
                    user_count = 0

                win_count = None
                raffle_data = None
            
                if event.user_event_ids:
                    user_count = len(event.user_event_ids.split(','))
                
                win_count = event.win_count
                raffle_data = event.end_date.strftime("%d.%m.%Y, %H:%M")

                winners = await req.get_event_winners(event.id)

                text_winners = '\n'.join([f"    {i}. {winner.fullname}" for i, winner in enumerate(winners, start=1)])
                text_for_owner_winners = '\n'.join([f'''<a href="{'https://t.me/'+winner.username if winner.username else 'tg://user?id='+str(winner.user_id)}">    {winner.fullname}</a>''' for winner in winners])
                
                deeplink_url = 'https://t.me/' + (await bot.get_me()).username + f'?start={event.id}'


                for channel_id in event.channel_event_ids.split(','):
                    if event.media:
                        await bot.send_photo(
                            chat_id=channel_id,
                            photo=event.media,
                            caption=lexicon.EVENT_WIN_TEXT.format(
                                name=event.name,
                                winners=text_winners,
                                users_count=user_count,
                                win_count=win_count,
                                raffle_date=raffle_data
                            ),
                            reply_markup= user_kb.show_event_results_web_kb(url=deeplink_url)
                        )
                    else:
                        await bot.send_message(
                            chat_id=channel_id,
                            text=lexicon.EVENT_WIN_TEXT.format(
                                name=event.name,
                                winners=text_winners,
                                users_count=user_count,
                                win_count=win_count,
                                raffle_date=raffle_data
                            ),
                            reply_markup= user_kb.show_event_results_web_kb(url=deeplink_url)
                        )
                await bot.send_message(
                    chat_id=event.owner_id,
                    text="Ваш розыгрыш завершен!\n\n" + lexicon.EVENT_WIN_TEXT.format(
                        name=event.name,
                        winners=text_for_owner_winners,
                        users_count=user_count,
                        win_count=win_count,
                        raffle_date=raffle_data
                    ),
                )
                await req.update_event(
                    event_id=event.id,
                    is_active=False
                )
                    
            
    
    async def start_scheduler(self, bot: config.Bot):
        self.scheduler.add_job(self.check_end_date, 'cron', minute="*", args=(bot,))
        self.scheduler.start()




AsyncScheduler = Scheduler()
