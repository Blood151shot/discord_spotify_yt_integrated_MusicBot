from music_player import (
    search_youtube,
    extract_audio_url
)


# ============================================================
# 1. Search YouTube
# ============================================================

youtube_result = search_youtube(
    "Blinding Lights",
    "The Weeknd"
)


if youtube_result is None:

    print("YouTube search failed.")
    exit()


print()
print("YouTube result:")
print(
    youtube_result["title"]
)
print(
    youtube_result["url"]
)


# ============================================================
# 2. Extract audio
# ============================================================

audio_result = extract_audio_url(
    youtube_result["url"]
)


if audio_result is None:

    print("Audio extraction failed.")
    exit()


print()
print("===================================")
print("AUDIO EXTRACTION SUCCESSFUL")
print("===================================")

print(
    "Title:",
    audio_result["title"]
)

print()

print(
    "Audio URL:",
    audio_result["audio_url"]
)

print()

print(
    "==================================="
)