from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import req
from datetime import timedelta

import datetime, pytz, logging as lg


class EventsArchiver:
    def __init__(self):
        # self.scheduler = AsyncIOScheduler(timezone=datetime.timezone(datetime.timedelta(hours=6)))
        self.scheduler = AsyncIOScheduler(timezone='Asia/Omsk')
        self.omsk_tz = pytz.timezone('Asia/Omsk')

    async def put_events_to_archive(self):
        events = await req.get_promotions()
        for event in events:
            # print((datetime.datetime.now() + datetime.timedelta(hours=3, minutes=1)).strftime("%d-%m-%Y %H:%M"), event.ended_at.strftime("%d-%m-%Y %H:%M"))
            if event.active and (datetime.datetime.now() + datetime.timedelta(hours=3, minutes=1) > event.ended_at):
                await req.Update_promotion(id=event.id, active=False)    
            
    
    async def start_scheduler(self):
        self.scheduler.add_job(self.put_events_to_archive, 'cron', minute="*")
        self.scheduler.start()




archiever = EventsArchiver()
