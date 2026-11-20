import json
import time
from collections import defaultdict
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.config import (
    DOTENV_PATH,
    RAW_DIR,
    TMDB_API_KEY_ENV_VAR,
    TMDB_BASE_URL as BASE_URL,
    TMDB_REQUEST_TIMEOUT,
    TMDB_RETRY_BACKOFF_SECONDS,
    TMDB_RETRY_STATUS_CODES,
    TMDB_RETRY_TOTAL,
    TMDB_SUCCESS_REQUEST_DELAY_SECONDS,
    TMDB_USER_AGENT,
    get_tmdb_api_key,
)

MANIFEST_PATH = RAW_DIR / "manifest.jsonl"


class TMDbClient:
    def __init__(self, force_refresh=False):
        load_dotenv(DOTENV_PATH)
        self.api_key = get_tmdb_api_key()
        self.force_refresh = force_refresh

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.latest_status = self._load_latest_statuses()

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": TMDB_USER_AGENT})

        retry_policy = Retry(
            total=TMDB_RETRY_TOTAL,
            backoff_factor=TMDB_RETRY_BACKOFF_SECONDS,
            status_forcelist=TMDB_RETRY_STATUS_CODES,
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

            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                ValueError,
            ):
                payload = None
            else:
                self._record(
                    movie_id, endpoint, "cache", "success", cache_path
                )
                return payload

        key = (str(movie_id), endpoint)

        if (
            not self.force_refresh
            and self.latest_status.get(key) == "not_found"
        ):
            self._record(
                movie_id, endpoint, "cache", "not_found", None
            )
            return None

        if not self.api_key:
            raise RuntimeError(
                f"{TMDB_API_KEY_ENV_VAR} is missing from .env; "
                "a key is required for live requests"
            )

        url = f"{BASE_URL}/movie/{movie_id}"

        if endpoint == "credits":
            url += "/credits"

        response = self.session.get(
            url,
            params={"api_key": self.api_key},
            timeout=TMDB_REQUEST_TIMEOUT,
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
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=2,
            )

        self._record(
            movie_id, endpoint, "network", "success", cache_path
        )

        # A small pause between successful network requests.
        time.sleep(TMDB_SUCCESS_REQUEST_DELAY_SECONDS)

        return payload

    @staticmethod
    def _validate_payload(payload, movie_id, endpoint):
        """Validate the TMDb response and required nested structures."""
        if not isinstance(payload, dict):
            raise ValueError(
                f"TMDb {endpoint} response must be a JSON object"
            )

        if str(payload.get("id")) != str(movie_id):
            raise ValueError(
                f"TMDb {endpoint} response ID does not match request"
            )

        if endpoint == "movie":
            genres = payload.get("genres")

            if not isinstance(genres, list):
                raise ValueError(
                    "TMDb movie response field 'genres' must be a list"
                )

            for genre in genres:
                if (
                    not isinstance(genre, dict)
                    or not isinstance(genre.get("id"), int)
                    or isinstance(genre.get("id"), bool)
                    or not isinstance(genre.get("name"), str)
                ):
                    raise ValueError(
                        "TMDb movie response contains an invalid "
                        "genre entry"
                    )

        elif endpoint == "credits":
            for field in ("cast", "crew"):
                entries = payload.get(field)

                if not isinstance(entries, list):
                    raise ValueError(
                        f"TMDb credits response field '{field}' "
                        "must be a list"
                    )

                for entry in entries:
                    if (
                        not isinstance(entry, dict)
                        or not isinstance(entry.get("id"), int)
                        or isinstance(entry.get("id"), bool)
                    ):
                        raise ValueError(
                            f"TMDb credits response contains an invalid "
                            f"'{field}' entry"
                        )

        else:
            raise ValueError(f"Unsupported endpoint: {endpoint}")

    def _record(
        self, movie_id, endpoint, source, status, cache_path
    ):
        key = (str(movie_id), endpoint)
        previous_status = self.latest_status.get(key)

        # Update in-memory state for subsequent fetches.
        self.latest_status[key] = status

        # Avoid repeated manifest entries for unchanged statuses.
        if previous_status == status:
            return

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

                # Ignore valid JSON values that are not JSON objects.
                if not isinstance(record, dict):
                    continue

                key = (
                    str(record.get("movie_id")),
                    record.get("endpoint"),
                )
                latest[key] = record.get("status")

        return latest
