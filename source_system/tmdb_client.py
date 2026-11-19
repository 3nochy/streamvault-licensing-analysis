
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.themoviedb.org/3"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MANIFEST_PATH = RAW_DIR / "manifest.jsonl"


class TMDbClient:
    def __init__(self, force_refresh=False):
        load_dotenv(PROJECT_ROOT / ".env")
        self.api_key = os.getenv("TMDB_API_KEY")
        self.force_refresh = force_refresh

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.latest_status = self._load_latest_statuses()

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

        # Reuse only a parseable cache entry with the expected payload shape.
        if cache_path.exists() and not self.force_refresh:
            try:
                with cache_path.open(encoding="utf-8") as file:
                    payload = json.load(file)
                self._validate_payload(payload, movie_id, endpoint)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
                payload = None
            else:
                self._record(movie_id, endpoint, "cache", "success", cache_path)
                return payload

        key = (str(movie_id), endpoint)
        if (
            not self.force_refresh
            and self.latest_status.get(key) == "not_found"
        ):
            self._record(movie_id, endpoint, "cache", "not_found", None)
            return None

        if not self.api_key:
            raise RuntimeError(
                "TMDB_API_KEY is missing from .env; a key is required for live requests"
            )

        url = f"{BASE_URL}/movie/{movie_id}"
        if endpoint == "credits":
            url += "/credits"

        response = self.session.get(
            url,
            params={"api_key": self.api_key},
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
        self._validate_payload(payload, movie_id, endpoint)

        # Save the original response before downstream transformations.
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

        self._record(
            movie_id, endpoint, "network", "success", cache_path
        )

        # A small pause between successful network requests.
        time.sleep(0.25)

        return payload

    @staticmethod
    def _validate_payload(payload, movie_id, endpoint):
        if not isinstance(payload, dict):
            raise ValueError(f"TMDb {endpoint} response must be a JSON object")
        if str(payload.get("id")) != str(movie_id):
            raise ValueError(f"TMDb {endpoint} response ID does not match request")
        required = {"genres"} if endpoint == "movie" else {"cast", "crew"}
        invalid = [key for key in required if not isinstance(payload.get(key), list)]
        if invalid:
            raise ValueError(
                f"TMDb {endpoint} response has invalid fields: {', '.join(sorted(invalid))}"
            )

    def _record(self, movie_id, endpoint, source, status, cache_path):
        self.latest_status[(str(movie_id), endpoint)] = status
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

    @staticmethod
    def _load_latest_statuses():
        latest = defaultdict(lambda: None)
        if not MANIFEST_PATH.exists():
            return latest
        with MANIFEST_PATH.open(encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                key = (str(record.get("movie_id")), record.get("endpoint"))
                latest[key] = record.get("status")
        return latest
