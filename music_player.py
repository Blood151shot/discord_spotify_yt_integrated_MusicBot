import asyncio
import yt_dlp
import discord


# ============================================================
# YouTube search options
# ============================================================

YOUTUBE_SEARCH_OPTIONS = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "noplaylist": True,
}


# ============================================================
# Search YouTube
# ============================================================

def search_youtube(song_name, artist_name):
    """
    Search YouTube for a Spotify song.
    """

    query = f"{song_name} {artist_name} official audio"

    print(f"Searching YouTube for: {query}")

    with yt_dlp.YoutubeDL(YOUTUBE_SEARCH_OPTIONS) as ydl:

        result = ydl.extract_info(
            f"ytsearch1:{query}",
            download=False
        )

    if not result or not result.get("entries"):
        return None

    video = result["entries"][0]

    # Get YouTube video ID
    video_id = video.get("id")

    # Build the YouTube URL ourselves
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    return {
        "title": video.get("title"),
        "url": youtube_url,
        "id": video_id
    }


# ============================================================
# Extract audio URL
# ============================================================

def extract_audio_url(youtube_url):

    """
    Extract the direct audio stream URL from YouTube.
    """

    options = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True
    }

    print(f"Extracting audio from: {youtube_url}")

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            youtube_url,
            download=False
        )

    if not info:
        return None

    return {
        "title": info.get("title"),
        "audio_url": info["url"]
    }


# ============================================================
# Play song
# ============================================================

async def play_song(
    voice_client,
    song_name,
    artist_name
):

    """
    Search YouTube, extract audio and play it through Discord.
    """

    # --------------------------------------------------------
    # 1. Search YouTube
    # --------------------------------------------------------

    youtube_result = await asyncio.to_thread(
        search_youtube,
        song_name,
        artist_name
    )

    if youtube_result is None:

        raise Exception(
            "Could not find the song on YouTube."
        )

    print()
    print("===================================")
    print("YouTube Match")
    print("===================================")

    print(
        f"Title: {youtube_result['title']}"
    )

    print(
        f"URL: {youtube_result['url']}"
    )

    print(
        f"ID: {youtube_result['id']}"
    )

    print("===================================")


    # --------------------------------------------------------
    # 2. Extract audio
    # --------------------------------------------------------

    audio_result = await asyncio.to_thread(
        extract_audio_url,
        youtube_result["url"]
    )

    if audio_result is None:

        raise Exception(
            "Could not extract the audio stream."
        )

    audio_url = audio_result["audio_url"]

    print(
        "Audio stream extracted successfully."
    )


    # --------------------------------------------------------
    # 3. Stop current playback
    # --------------------------------------------------------

    if voice_client.is_playing():

        voice_client.stop()


    # --------------------------------------------------------
    # 4. Send stream to FFmpeg
    # --------------------------------------------------------

    audio_source = discord.FFmpegPCMAudio(

        audio_url,

        before_options=(
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5"
        ),

        options="-vn"
    )


    # --------------------------------------------------------
    # 5. Play
    # --------------------------------------------------------

    voice_client.play(

        audio_source,

        after=lambda error: print(
            f"Playback finished: {error}"
        )
    )

    return youtube_result