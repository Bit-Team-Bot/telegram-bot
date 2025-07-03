# handlers/scheduler_handler.py

import asyncio

class SchedulerHandler:
    def __init__(self, news_handler, send_func):
        self.news_handler = news_handler
        self.send_func = send_func

    async def start_daily_morning_update(self):
        while True:
            await asyncio.sleep(86400)  # 24h
            msg = await self.news_handler.get_morning_market_update()
            await self.send_func(msg)

    async def start_weekly_report(self):
        while True:
            await asyncio.sleep(604800)  # 7 Tage
            msg = await self.news_handler.get_weekly_report()
            await self.send_func(msg)
