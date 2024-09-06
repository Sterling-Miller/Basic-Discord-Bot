import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print("moderation.py is ready to be used.")

    @app_commands.command(name="clear", description="Clear specified amount of messages starting with most recent in the text chat.")
    async def clear(self, interaction: discord.Interaction, count: int):
        """
        Clear specified amount of messages in the channel.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.user.guild_permissions.manage_messages:
            if count == 0:
                await interaction.followup.send("Must enter number greater than zero.", ephemeral=True)
                return
            channel = interaction.channel
            await channel.purge(limit=count)
            await interaction.followup.send("Cleared the channel.", ephemeral=True)
        else:
            await interaction.followup.send("You don't have permission to manage messages.", ephemeral=True)

async def setup(client):
    await client.add_cog(Moderation(client))
