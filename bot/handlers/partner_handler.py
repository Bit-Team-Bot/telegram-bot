# handlers/partner_handler.py

class PartnerHandler:
    def __init__(self, db):
        self.db = db

    async def add_partner(self, user_id):
        await self.db.add_partner(user_id)

    async def get_partners(self):
        return await self.db.get_partners()
