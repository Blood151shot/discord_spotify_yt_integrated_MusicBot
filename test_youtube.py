from music_player import search_youtube

result = search_youtube(
    "Blinding Lights",
    "The Weeknd"
)

print()
print("===================================")
print("TEST RESULT")
print("===================================")

if result:

    print("Title:", result["title"])
    print("URL:", result["url"])
    print("ID:", result["id"])

else:
    
    print("No result found.")

print("===================================")