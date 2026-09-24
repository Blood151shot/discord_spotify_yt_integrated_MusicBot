import discord 
from discord.ext import commands
from discord import app_commands

from spotify_auth import get_login_url


class LoginButton(discord.ui.View):

    def __init__(self,discord_id):
        super().__init__(
            timeout=None
        )

        self.add_item(
            discord.ui.Button(
                label="Login Spotify",
                emoji="🎧",
                style=discord.ButtonStyle.link,
                url=get_login_url(
                    discord_id
                )
            )
        )


class AuthCommands(commands.Cog):

    def __init__(self,bot):
        self.bot=bot


    @app_commands.command(
        name="spotify_login",
        description="Connect your Spotify account"
    )

    async def spotify_login(
        self,
        interaction:discord.Interaction
    ):

        embed=discord.Embed(
            title="Connect Spotify 🎧",
            description="Login to unlock your music profile",
            color=discord.Color.green()
        )


        await interaction.response.send_message(
            embed=embed,
            view=LoginButton(
                interaction.user.id
            ),
            ephemeral=True
        )


async def setup(bot):

    await bot.add_cog(
        AuthCommands(bot)
    )