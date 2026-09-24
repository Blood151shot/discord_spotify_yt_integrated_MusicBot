import discord
from discord.ext import commands
from discord import app_commands

from spotify_api import search_song
from music_player import play_song


# ============================================================
# Spotify Buttons
# ============================================================

class SpotifyButtons(discord.ui.View):

    def __init__(
        self,
        spotify_url,
        song_name,
        artist_name
    ):

        super().__init__(
            timeout=None
        )

        # ----------------------------------------------------
        # Store song information
        # ----------------------------------------------------

        self.song_name = song_name
        self.artist_name = artist_name

        # ----------------------------------------------------
        # Open Spotify button
        # ----------------------------------------------------

        self.add_item(
            discord.ui.Button(
                label="Open Spotify",
                style=discord.ButtonStyle.link,
                emoji="🎧",
                url=spotify_url
            )
        )


    # ========================================================
    # Play button
    # ========================================================

    @discord.ui.button(
        label="Play",
        style=discord.ButtonStyle.blurple,
        emoji="▶️"
    )
    async def play_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        # ----------------------------------------------------
        # Check if user is in a voice channel
        # ----------------------------------------------------

        if interaction.user.voice is None:

            await interaction.response.send_message(
                "❌ You need to join a voice channel first.",
                ephemeral=True
            )

            return


        voice_channel = interaction.user.voice.channel


        # ----------------------------------------------------
        # Tell Discord we're processing
        # ----------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )


        try:

            # ------------------------------------------------
            # Get existing voice client
            # ------------------------------------------------

            voice_client = interaction.guild.voice_client


            # ------------------------------------------------
            # Connect if not connected
            # ------------------------------------------------

            if voice_client is None:

                voice_client = await voice_channel.connect()


            # ------------------------------------------------
            # Move if connected to another channel
            # ------------------------------------------------

            elif voice_client.channel != voice_channel:

                await voice_client.move_to(
                    voice_channel
                )


            # ------------------------------------------------
            # Play song
            # ------------------------------------------------

            result = await play_song(
                voice_client,
                self.song_name,
                self.artist_name
            )


            # ------------------------------------------------
            # Success message
            # ------------------------------------------------

            await interaction.followup.send(
                f"🎵 Now playing: **{result['title']}**",
                ephemeral=True
            )


        except Exception as e:

            print("PLAY ERROR:")
            print(e)

            await interaction.followup.send(
                f"❌ Could not play the song.\n`{e}`",
                ephemeral=True
            )


    # ========================================================
    # Battle button
    # ========================================================

    @discord.ui.button(
        label="Add To Battle",
        style=discord.ButtonStyle.green,
        emoji="⚔️"
    )
    async def battle_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Song added to battle ⚔️",
            ephemeral=True
        )


# ============================================================
# Spotify Command Cog
# ============================================================

class SpotifyCommands(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # ========================================================
    # /song command
    # ========================================================

    @app_commands.command(
        name="song",
        description="Search Spotify songs"
    )
    async def song(
        self,
        interaction: discord.Interaction,
        song: str
    ):

        # ----------------------------------------------------
        # Search Spotify
        # ----------------------------------------------------

        data = search_song(song)


        if data is None:

            await interaction.response.send_message(
                "Song not found ❌"
            )

            return


        # ----------------------------------------------------
        # Create Spotify embed
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🎵 " + data["song_name"],
            description=data["artist"],
            url=data["spotify_url"],
            color=discord.Color.green()
        )


        # ----------------------------------------------------
        # Album image
        # ----------------------------------------------------

        embed.set_image(
            url=data["image"]
        )


        # ----------------------------------------------------
        # Album
        # ----------------------------------------------------

        embed.add_field(
            name="Album",
            value=data["album"],
            inline=False
        )


        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        embed.add_field(
            name="Duration",
            value=str(
                round(
                    data["duration"] / 60000,
                    2
                )
            ) + " minutes",
            inline=False
        )


        # ----------------------------------------------------
        # Send embed + buttons
        # ----------------------------------------------------

        await interaction.response.send_message(

            embed=embed,

            view=SpotifyButtons(
                data["spotify_url"],
                data["song_name"],
                data["artist"]
            )
        )


# ============================================================
# Cog setup
# ============================================================

async def setup(bot):

    await bot.add_cog(
        SpotifyCommands(bot)
    )