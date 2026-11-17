
from tmdb_client import TMDbClient

client = TMDbClient()

movie = client.fetch(155, "movie")
credits = client.fetch(155, "credits")

assert movie is not None
assert movie["id"] == 155
assert "title" in movie
assert credits is not None
assert "cast" in credits

print("Movie:", movie["title"])
print("Cast entries:", len(credits["cast"]))
print("Client checks passed.")
