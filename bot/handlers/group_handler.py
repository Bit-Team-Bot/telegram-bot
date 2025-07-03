# handlers/group_handler.py

class GroupHandler:
    def __init__(self, db):
        self.db = db

    async def add_group(self, user_id, group_id, name):
        await self.db.add_group(user_id, group_id, name)

    async def get_groups_for_user(self, user_id):
        return await self.db.get_groups_for_user(user_id)

    async def link_groups(self, group_a_id, group_b_id):
        await self.db.link_groups(group_a_id, group_b_id)
