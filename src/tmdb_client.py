
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
RAW_DIR = Path("data/raw")
MANIFEST_PATH = RAW_DIR / "manifest.jsonl"

API_KEY = os.getenv("TMDB_API_KEY")


class TMDbClient:
    def __init__(self):
        if not API_KEY:
            raise RuntimeError("TMDB_API_KEY is missing from .env")

        RAW_DIR.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "StreamVault-Licensing-Analysis/1.0"}
        )

        retry_policy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods={"GET"},
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry_policy)
        self.session.mount("https://", adapter)

    def fetch(self, movie_id, endpoint):
        if endpoint not in {"movie", "credits"}:
            raise ValueError(f"Unsupported endpoint: {endpoint}")

        cache_path = RAW_DIR / f"{endpoint}_{movie_id}.json"

        # Reuse an existing raw response.
        if cache_path.exists():
            with cache_path.open(encoding="utf-8") as file:
                payload = json.load(file)

            self._record(
                movie_id, endpoint, "cache", "success", cache_path
            )
            return payload

        url = f"{BASE_URL}/movie/{movie_id}"
        if endpoint == "credits":
            url += "/credits"

        response = self.session.get(
            url,
            params={"api_key": API_KEY},
            timeout=(3.05, 10),
        )

        # A missing film or credits resource is recorded, not retried.
        if response.status_code == 404:
            self._record(
                movie_id, endpoint, "network", "not_found", None
            )
            return None

        response.raise_for_status()
        payload = response.json()

        # Save the original response before downstream transformations.
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

        self._record(
            movie_id, endpoint, "network", "success", cache_path
        )

        # A small pause between successful network requests.
        time.sleep(0.25)

        return payload

    def _record(self, movie_id, endpoint, source, status, cache_path):
        record = {
            "movie_id": movie_id,
            "endpoint": endpoint,
            "source": source,
            "status": status,
            "cache_path": str(cache_path) if cache_path else None,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        with MANIFEST_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")
