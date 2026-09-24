import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv(
    r"C:\Users\Tanvir Singh\OneDrive\Desktop\old desktop apps\desktop\intern\PROJECT\api.env"
)

# creating spotify authentication object
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("spotify_client_id"),
    client_secret=os.getenv("spotify_client_secret")
)

# creating spotify object
spotify = spotipy.Spotify(
    auth_manager=auth_manager
)
# function for searching songs
def search_song(song_name):
    result = spotify.search(
        q=song_name,
        limit=1,
        type="track"

    )
    # checking if spotify found any song
    if len(result["tracks"]["items"]) == 0:

        return None
    track = result["tracks"]["items"][0]
    # print(track.keys()) # for checking all the available spotify data
    song_data = {
        "song_name":
        track["name"],
        "artist":
        track["artists"][0]["name"],
        "album":
        track["album"]["name"],
        "image":
        track["album"]["images"][0]["url"],
        "spotify_url":
        track["external_urls"]["spotify"],
        "popularity":
        track.get(
            "popularity",
            "Not Available"
        ),
        "song_id":
        track["id"],
        "duration":
        track["duration_ms"],

        "preview":
        track.get(
            "preview_url",
            None
        )
    }
    return song_data