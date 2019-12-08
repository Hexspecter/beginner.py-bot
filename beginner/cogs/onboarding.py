from beginner.cog import Cog


class OnBoarding(Cog):
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_ready(self):
        print("On Boarding is ready")

    @Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.emoji.name != "✅":
            return

        channel = self.get_channel("new-users")
        if reaction.channel_id != channel.id:
            return

        message = await channel.fetch_message(reaction.message_id)
        if message.mentions and message.mentions[0].id == reaction.user_id:
            await self.server.get_member(reaction.user_id).add_roles(
                self.get_role("coders")
            )
            await message.delete()

    @Cog.listener()
    async def on_member_join(self, member):
        emote = "✅"
        rules = self.get_channel("rules")
        message = await self.get_channel("new-users").send(
            f"Welcome {member.mention}!!! Have a look at <#{rules.id}>, once you're done tap the {emote} to agree and gain full access to the server!"
        )
        await message.add_reaction(emote)

    @Cog.listener()
    async def on_member_remove(self, member):
        await self.get_channel("new-users").purge(
            limit=1, check=lambda message: message.content.find(f"<@{member.id}>") >= 0
        )


def setup(client):
    client.add_cog(OnBoarding(client))