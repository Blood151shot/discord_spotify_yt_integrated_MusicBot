import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv(
    r"C:\Users\Tanvir Singh\OneDrive\Desktop\old desktop apps\desktop\intern\PROJECT\api.env"
)


scope=(
    "user-read-currently-playing "
    "user-read-playback-state "
    "user-read-recently-played "
    "user-top-read "
    "playlist-read-private"
)


def create_oauth():

    return SpotifyOAuth(

        client_id=os.getenv(
            "spotify_client_id"
        ),

        client_secret=os.getenv(
            "spotify_client_secret"
        ),

        redirect_uri=os.getenv(
            "spotify_redirect_url"
        ),

        scope=scope

    )



def get_login_url(discord_id):

    oauth=create_oauth()

    url=oauth.get_authorize_url(
        state=str(discord_id)
    )

    return url