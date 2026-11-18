
import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TMDB_API_KEY")

if not api_key:
    raise RuntimeError("TMDB_API_KEY is missing from .env")

url = "https://api.themoviedb.org/3/movie/155"

response = requests.get(
    url,
    params={"api_key": api_key},
    timeout=(3.05, 10),
)

response.raise_for_status()
movie = response.json()

print("API connection successful")
print("Movie ID:", movie.get("id"))
print("Title:", movie.get("title"))
print("Release date:", movie.get("release_date"))
print("Budget:", movie.get("budget"))
print("Revenue:", movie.get("revenue"))
print("Collection:", movie.get("belongs_to_collection"))
