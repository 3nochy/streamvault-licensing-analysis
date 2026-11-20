"""Shared paths and runtime settings for the StreamVault pipeline."""

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOTENV_PATH = PROJECT_ROOT / ".env"

ID_LIST_PATH = PROJECT_ROOT / "id_list.csv"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "out"

PROFILING_NOTEBOOK_PATH = PROJECT_ROOT / "explore" / "data_profiling.ipynb"
LICENSING_NOTEBOOK_PATH = PROJECT_ROOT / "explore" / "licensing_analysis.ipynb"

NOTEBOOK_PATHS = (
    PROFILING_NOTEBOOK_PATH,
    LICENSING_NOTEBOOK_PATH,
)

EXTRACTION_STATUS_PATH = PROCESSED_DIR / "extraction_status.csv"
TRANSFORM_STATUS_PATH = PROCESSED_DIR / "transform_status.csv"

TMDB_API_KEY_ENV_VAR = "TMDB_API_KEY"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_REQUEST_TIMEOUT = (3.05, 10)
TMDB_SUCCESS_REQUEST_DELAY_SECONDS = 0.25
TMDB_USER_AGENT = "StreamVault-Licensing-Analysis/1.0"
TMDB_RETRY_TOTAL = 5
TMDB_RETRY_BACKOFF_SECONDS = 1
TMDB_RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


def get_tmdb_api_key():
    """Read the TMDb key from the environment without exposing its value."""
    return os.getenv(TMDB_API_KEY_ENV_VAR)
