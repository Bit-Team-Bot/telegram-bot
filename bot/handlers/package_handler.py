# handlers/package_handler.py

class PackageHandler:
    def __init__(self, db):
        self.db = db

    async def set_user_paket(self, telegram_id, paket):
        await self.db.set_user_paket(telegram_id, paket)
