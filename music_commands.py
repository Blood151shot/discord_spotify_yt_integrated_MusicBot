import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio


# ==========================
# YOUTUBE-DL SETTINGS
# ==========================

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
}

FFMPEG_OPTIONS = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 5"
    ),
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


# ==========================
# MUSIC PLAYER
# ==========================

class MusicPlayer:

    def __init__(self, bot):

        self.bot = bot

        # Songs waiting to be played
        self.queue = []

        # Songs already played
        self.history = []

        # Currently playing song
        self.current = None

        # Discord voice connection
        self.voice = None

    # ==========================
    # GET SONG
    # ==========================

    async def get_song(self, search):

        loop = asyncio.get_event_loop()

        data = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(
                f"ytsearch:{search}",
                download=False
            )
        )

        if "entries" in data:
            data = data["entries"][0]

        return {
            "title": data["title"],
            "url": data["url"],
            "webpage": data.get("webpage_url")
        }

    # ==========================
    # PLAY SONG
    # ==========================

    async def play_song(self, song):

        if not self.voice:
            return

        self.current = song

        source = discord.FFmpegPCMAudio(
            song["url"],
            **FFMPEG_OPTIONS
        )

        def after(error):

            if error:
                print(f"Player error: {error}")

            asyncio.run_coroutine_threadsafe(
                self.song_finished(),
                self.bot.loop
            )

        self.voice.play(
            source,
            after=after
        )

        print(f"Now playing: {song['title']}")

    # ==========================
    # SONG FINISHED
    # ==========================

    async def song_finished(self):

        if self.current:

            self.history.append(
                self.current
            )

        self.current = None

        # Play next song
        if self.queue:

            next_song = self.queue.pop(0)

            await self.play_song(
                next_song
            )

    # ==========================
    # PAUSE
    # ==========================

    def pause(self):

        if self.voice and self.voice.is_playing():

            self.voice.pause()

            return True

        return False

    # ==========================
    # RESUME
    # ==========================

    def resume(self):

        if self.voice and self.voice.is_paused():

            self.voice.resume()

            return True

        return False

    # ==========================
    # SKIP
    # ==========================

    def skip(self):

        if self.voice and (
            self.voice.is_playing()
            or self.voice.is_paused()
        ):

            self.voice.stop()

            return True

        return False

    # ==========================
    # PREVIOUS
    # ==========================

    async def previous(self):

        if not self.voice:
            return False

        if not self.history:
            return False

        # Stop current song
        if (
            self.voice.is_playing()
            or self.voice.is_paused()
        ):
            self.voice.stop()

        # Get previous song
        previous_song = self.history.pop()

        # Put current song at beginning of queue
        if self.current:

            self.queue.insert(
                0,
                self.current
            )

        await asyncio.sleep(0.2)

        await self.play_song(
            previous_song
        )

        return True

    # ==========================
    # STOP
    # ==========================

    async def stop(self):

        self.queue.clear()

        self.history.clear()

        self.current = None

        if self.voice:

            if (
                self.voice.is_playing()
                or self.voice.is_paused()
            ):
                self.voice.stop()

            await self.voice.disconnect()

            self.voice = None


# ==========================
# MUSIC BUTTONS
# ==========================

class MusicControls(discord.ui.View):

    def __init__(self, player):

        super().__init__(
            timeout=None
        )

        self.player = player

    # ==========================
    # PREVIOUS BUTTON
    # ==========================

    @discord.ui.button(
        emoji="⏮️",
        style=discord.ButtonStyle.secondary
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        success = await self.player.previous()

        if success:

            await interaction.response.send_message(
                f"⏮️ Playing previous: "
                f"**{self.player.current['title']}**",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ No previous song available.",
                ephemeral=True
            )

    # ==========================
    # PAUSE / RESUME BUTTON
    # ==========================

    @discord.ui.button(
        emoji="⏯️",
        style=discord.ButtonStyle.primary
    )
    async def pause_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.player.voice:

            await interaction.response.send_message(
                "❌ Bot is not in a voice channel.",
                ephemeral=True
            )

            return

        if self.player.voice.is_playing():

            self.player.pause()

            await interaction.response.send_message(
                "⏸️ Music paused.",
                ephemeral=True
            )

        elif self.player.voice.is_paused():

            self.player.resume()

            await interaction.response.send_message(
                "▶️ Music resumed.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Nothing is playing.",
                ephemeral=True
            )

    # ==========================
    # NEXT BUTTON
    # ==========================

    @discord.ui.button(
        emoji="⏭️",
        style=discord.ButtonStyle.secondary
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.player.queue:

            self.player.skip()

            await interaction.response.send_message(
                "⏭️ Skipped to the next song.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Queue is empty.",
                ephemeral=True
            )

    # ==========================
    # STOP BUTTON
    # ==========================

    @discord.ui.button(
        emoji="⏹️",
        style=discord.ButtonStyle.danger
    )
    async def stop_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.player.stop()

        await interaction.response.send_message(
            "⏹️ Music stopped."
        )


# ==========================
# MUSIC COMMANDS COG
# ==========================

class MusicCommands(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.player = MusicPlayer(
            bot
        )

    # ==========================
    # PLAY
    # ==========================

    @app_commands.command(
        name="play",
        description="Play a song"
    )
    async def play(
        self,
        interaction: discord.Interaction,
        song: str
    ):

        await interaction.response.defer()

        # Check voice channel
        if not interaction.user.voice:

            await interaction.followup.send(
                "❌ Join a voice channel first."
            )

            return

        channel = interaction.user.voice.channel

        # Connect to voice
        if not self.player.voice:

            self.player.voice = await channel.connect()

        elif self.player.voice.channel != channel:

            await self.player.voice.move_to(
                channel
            )

        # Find song
        try:

            song_data = await self.player.get_song(
                song
            )

        except Exception as e:

            print(e)

            await interaction.followup.send(
                "❌ Could not find that song."
            )

            return

        # If something is already playing
        if (
            self.player.voice.is_playing()
            or self.player.voice.is_paused()
        ):

            self.player.queue.append(
                song_data
            )

            await interaction.followup.send(
                f"➕ Added to queue:\n"
                f"**{song_data['title']}**"
            )

            return

        # Play immediately
        await self.player.play_song(
            song_data
        )

        embed = discord.Embed(
            title="🎵 Now Playing",
            description=(
                f"**{song_data['title']}**"
            ),
            color=discord.Color.green()
        )

        await interaction.followup.send(
            embed=embed,
            view=MusicControls(
                self.player
            )
        )

    # ==========================
    # PAUSE
    # ==========================

    @app_commands.command(
        name="pause",
        description="Pause the current song"
    )
    async def pause(
        self,
        interaction: discord.Interaction
    ):

        if self.player.pause():

            await interaction.response.send_message(
                "⏸️ Music paused."
            )

        else:

            await interaction.response.send_message(
                "❌ Nothing is playing."
            )

    # ==========================
    # RESUME
    # ==========================

    @app_commands.command(
        name="resume",
        description="Resume the current song"
    )
    async def resume(
        self,
        interaction: discord.Interaction
    ):

        if self.player.resume():

            await interaction.response.send_message(
                "▶️ Music resumed."
            )

        else:

            await interaction.response.send_message(
                "❌ Music isn't paused."
            )

    # ==========================
    # SKIP
    # ==========================

    @app_commands.command(
        name="skip",
        description="Skip to the next song"
    )
    async def skip(
        self,
        interaction: discord.Interaction
    ):

        if not self.player.queue:

            await interaction.response.send_message(
                "❌ No songs are waiting in the queue."
            )

            return

        self.player.skip()

        await interaction.response.send_message(
            "⏭️ Skipped."
        )

    # ==========================
    # PREVIOUS
    # ==========================

    @app_commands.command(
        name="previous",
        description="Play the previous song"
    )
    async def previous(
        self,
        interaction: discord.Interaction
    ):

        success = await self.player.previous()

        if success:

            await interaction.response.send_message(
                f"⏮️ Playing:\n"
                f"**{self.player.current['title']}**"
            )

        else:

            await interaction.response.send_message(
                "❌ No previous song available."
            )

    # ==========================
    # QUEUE
    # ==========================

    @app_commands.command(
        name="queue",
        description="Show the music queue"
    )
    async def queue(
        self,
        interaction: discord.Interaction
    ):

        if not self.player.queue:

            await interaction.response.send_message(
                "📭 Queue is empty."
            )

            return

        queue_text = ""

        for index, song in enumerate(
            self.player.queue,
            start=1
        ):

            queue_text += (
                f"{index}. "
                f"**{song['title']}**\n"
            )

        embed = discord.Embed(
            title="🎵 Music Queue",
            description=queue_text,
            color=discord.Color.blue()
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ==========================
    # STOP
    # ==========================

    @app_commands.command(
        name="stop",
        description="Stop music"
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):

        await self.player.stop()

        await interaction.response.send_message(
            "⏹️ Music stopped and bot left the voice channel."
        )


# ==========================
# SETUP
# ==========================

async def setup(bot):

    await bot.add_cog(
        MusicCommands(bot)
    )