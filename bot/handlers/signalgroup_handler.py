# handlers/signalgroup_handler.py
class SignalGroupHandler:
    def __init__(self, db):
        self.db = db

    async def add_signalgroup(self, name, owner_id, source_group_id, description="", price=0):
        await self.db.add_signalgroup(name, owner_id, source_group_id, description, price)

    async def assign_to_user(self, user_id, signalgroup_id):
        await self.db.assign_signalgroup_to_user(user_id, signalgroup_id)

    async def get_signalgroups_for_user(self, user_id):
        return await self.db.get_signalgroups_for_user(user_id)

    async def update_signalgroup(self, signalgroup_id, name=None, description=None, price=None):
        await self.db.update_signalgroup(signalgroup_id, name, description, price)

