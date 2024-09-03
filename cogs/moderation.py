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

    @app_commands.command(name="join", description="Allow Botto to join voice channel.")
    async def join(self, interaction: discord.Interaction):
        """
        Allow Botto to join voice chat.

        NOTE: Can only be used in a single voice channel at a time on a specific server.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice:
            if interaction.guild.voice_client:
                await interaction.followup.send("Already connected!")
            else:
                channel = interaction.user.voice.channel
                await channel.connect()
                await interaction.followup.send("Hello!")
        else:
            await interaction.followup.send("You need to be in a voice channel to use that command!")

    @app_commands.command(name="leave", description="Kick Botto from voice chennel.")
    async def leave(self, interaction: discord.Interaction):
        """
        Kick Botto from voice chat.

        NOTE: Will kick Botto out of any voice channel on a specific server.
        """
        await interaction.response.defer(ephemeral=True)
        if interaction.user.voice:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                await interaction.followup.send("Goodbye!")
            else:
                await interaction.followup.send("Already left!")
        else:
            await interaction.followup.send("You need to be in a voice channel to use that command!")

    @app_commands.command(name="clear", description="Clear specified amount of messages starting with the most recent in the text chat.")
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
