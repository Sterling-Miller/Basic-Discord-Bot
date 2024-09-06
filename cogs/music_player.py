import os
import yt_dlp
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import urllib.parse, urllib.request, re

# YouTube URL Formating:
youtube_base_url = "https://www.youtube.com/"
youtube_results_url = youtube_base_url + "results?"
youtube_watch_url = youtube_base_url + "watch?v="
# YouTube-DL Options:
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
# FFmpeg Options:
ffmpeg_options = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5","options": "-vn -filter:a 'volume=0.25'"}

class MusicPlayer(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queues = {}
        self.voice_clients = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print("music_player.py is ready to be used.")

    @app_commands.command(name="join", description="Allow Botto to join voice channel.")
    async def join(self, interaction: discord.Interaction):
        """ Allow Botto to join voice chat. 
            NOTE: Can only be used in a single voice channel at a time on a specific server. 
        """
        await interaction.response.defer(ephemeral=True)
        try:
            if interaction.user.voice:
                if interaction.guild.voice_client:
                    await interaction.followup.send("Already connected!")
                else:
                    voice_client = await interaction.user.voice.channel.connect()
                    self.voice_clients[voice_client.guild.id] = voice_client
                    await interaction.followup.send("Hello!")
            else:
                await interaction.followup.send("You need to be in a voice channel to use that command!")
        except Exception as e:
            print(e)

    @app_commands.command(name="leave", description="Kick Botto from voice chennel.")
    async def leave(self, interaction: discord.Interaction):
        """ Kick Botto from voice chat.
            NOTE: Will kick Botto out of any voice channel on a specific server.
        """
        await interaction.response.defer(ephemeral=True)
        try:
            if interaction.user.voice:
                if interaction.guild.voice_client:
                    self.voice_clients[interaction.guild.id].stop()
                    await self.voice_clients[interaction.guild.id].disconnect()
                    del self.voice_clients[interaction.guild.id]
                    await interaction.followup.send("Goodbye!")
                else:
                    await interaction.followup.send("Already left!")
            else:
                await interaction.followup.send("You need to be in a voice channel to use that command!")
        except Exception as e:
            print(e)

    async def _play_song(self, interaction: discord.Interaction, link: str):
        """ Internal helper to handle the actual music playing. """
        try:
            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({"search_query": link})
                content = urllib.request.urlopen(youtube_results_url + query_string)
                search_results = re.findall(r"/watch\?v=(.{11})", content.read().decode())
                link = youtube_watch_url + search_results[0]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

            song = data["url"]
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
            self.voice_clients[interaction.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next(interaction), self.client.loop))
            await interaction.followup.send(f"Now playing: {data["title"]} {data["duration"]}")

        except Exception as e:
            print(e)

    async def _play_next(self, interaction: discord.Interaction):
        """ Play the next song in the queue. """
        if self.queues[interaction.guild.id]:
            link = self.queues[interaction.guild.id].pop(0)
            await self._play_song(interaction, link=link)

    @app_commands.command(name="play", description="Play music. Use YouTube URL or search term.")
    async def play(self, interaction: discord.Interaction, link: str):
        """ Play music in the voice chat. """
        await interaction.response.defer(ephemeral=False)
        try:
            if not interaction.guild.voice_client:
                voice_client = await interaction.user.voice.channel.connect()
                self.voice_clients[voice_client.guild.id] = voice_client
            else:
                voice_client = interaction.guild.voice_client
                self.voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            await interaction.followup.send("You must be in a voice channel to use that command!")
            return print(e)

        await self._play_song(interaction, link)

    @app_commands.command(name="pause", description="Pause current song.")
    async def pause(self, interaction: discord.Interaction):
        """ Pause music. """
        await interaction.response.defer(ephemeral=True)
        try:
            self.voice_clients[interaction.guild.id].pause()
            await interaction.followup.send("Paused!")
        except Exception as e:
            print(e)

    @app_commands.command(name="resume", description="Resume current song.")
    async def resume(self, interaction: discord.Interaction):
        """ Resume music. """
        await interaction.response.defer(ephemeral=True)
        try:
            self.voice_clients[interaction.guild.id].resume()
            await interaction.followup.send("Resumed!")
        except Exception as e:
            print(e)

    @app_commands.command(name="skip", description="Skip current song.")
    async def skip(self, interaction: discord.Interaction):
        """ Skip current song. """
        await interaction.response.defer(ephemeral=True)
        try:
            self.voice_clients[interaction.guild.id].stop()
            await interaction.followup.send("Skipped!")
        except Exception as e:
            print(e)

    @app_commands.command(name="queue")
    async def queue(self, interaction: discord.Interaction, link: str):
        """ Add a song to the queue. """
        await interaction.response.defer(ephemeral=True)
        if interaction.guild_id not in self.queues:
            self.queues[interaction.guild_id] = []

        if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({"search_query": link})
                content = urllib.request.urlopen(youtube_results_url + query_string)
                search_results = re.findall(r"/watch\?v=(.{11})", content.read().decode())
                link = youtube_watch_url + search_results[0]

        self.queues[interaction.guild_id].append(link)
        await interaction.followup.send("Added ")

    @app_commands.command(name="view_queue")
    async def view_queue(self, interaction: discord.Interaction):
        """ View the queue. """
        await interaction.response.defer(ephemeral=False)
        if interaction.guild.id not in self.queues:
            await interaction.followup.send("There is no queue to view")
            return
        embed = discord.Embed(title="Queue:")
        for i in range(len(self.queues[interaction.guild.id])):
            link = self.queues[interaction.guild.id][i]
            data = ytdl.extract_info(link, download=False)
            embed.add_field(name=str(i+1), value=data["title"], inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear_queue", description="Clear the queue.")
    async def clear_queue(self, interaction: discord.Interaction):
        """ Clear queue. """
        await interaction.response.defer(ephemeral=True)
        if interaction.guild.id in self.queues:
            self.queues[interaction.guild.id].clear()
            await interaction.followup.send("Queue cleared!")
        else:
            await interaction.followup.send("There is no queue to clear")

async def setup(client):
    await client.add_cog(MusicPlayer(client))
