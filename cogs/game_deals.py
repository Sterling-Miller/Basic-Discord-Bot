import discord
import requests
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone

class GameDeals(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print("game_deals.py is ready to be used.")

    @app_commands.command(name="free_games", description="View this weeks free games on Epic.")
    async def free_games(self, interaction: discord.Interaction):
        """
        Use cheapshark.com api to view this weeks free games on Epic.
        https://apidocs.cheapshark.com/#396fb8c3-eb0a-72ed-9255-13bd16ce5945
        """
        await interaction.response.defer(ephemeral=True)
        try:
            url = "https://www.cheapshark.com/api/1.0/deals?storeID=25&upperPrice=0"
            response = requests.get(url).json()

            for game in range(len(response)):
                changed = datetime.fromtimestamp(response[game]["lastChange"], tz=timezone.utc)
                embed = discord.Embed(title=response[game]["title"], colour=discord.Colour(0x3572b8), timestamp=changed)
                embed.set_thumbnail(url=response[game]["thumb"])
                embed.add_field(name="Normal Price", value=f"${response[game]["normalPrice"]}", inline=False)
                embed.add_field(name="Rating", value=f"Steam:  {response[game]['steamRatingText']} %{response[game]['steamRatingPercent']}", inline=False)
                embed.set_footer(text="Epic Games", icon_url="https://www.cheapshark.com/img/stores/logos/24.png")
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print(e)
    
async def setup(client):
    await client.add_cog(GameDeals(client))