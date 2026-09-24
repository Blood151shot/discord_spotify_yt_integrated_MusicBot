import discord
from discord.ext import commands
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv(
    r"C:\Users\Tanvir Singh\OneDrive\Desktop\old desktop apps\desktop\intern\PROJECT\api.env"
)


class Client(commands.Bot):

    async def setup_hook(self):

        try:

            # Load Spotify commands
            await self.load_extension("spotify_commands")

            # Load authentication commands
            await self.load_extension("auth_commands")

            # Load music commands
            await self.load_extension("music_commands")

            # Sync slash commands
            synced = await self.tree.sync()

            print(f"Synced {len(synced)} commands")

            for command in synced:
                print(f"/{command.name}")

        except Exception as e:

            print(f"Error loading commands: {e}")


    async def on_ready(self):

        print(f"Logged in as {self.user}")


# Discord intents
intents = discord.Intents.default()
intents.message_content = True


# Create bot
client = Client(
    command_prefix="?",
    intents=intents
)


# Get token from api.env
token = os.getenv("discord_api")


# Start bot
client.run(token)