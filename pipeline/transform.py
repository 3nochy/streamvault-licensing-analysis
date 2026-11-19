import json
import math
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ID_LIST_PATH = PROJECT_ROOT / "id_list.csv"
STATUS_PATH = PROCESSED_DIR / "extraction_status.csv"


def load_candidate_ids():
    """Load candidate IDs while preserving source row positions."""
    source = pd.read_csv(
        ID_LIST_PATH,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False,
    )
    if "tmdb_id" not in source.columns:
        raise ValueError("id_list.csv must contain a 'tmdb_id' column")
    source["source_row"] = source.index + 2
    source["tmdb_id"] = source["tmdb_id"].str.strip()
    return source


def read_json(path):
    """Load a JSON file, returning None when it cannot be read."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _number(value, field, *, required=False, integer=False):
    if value is None or value == "":
        if required:
            raise ValueError(f"missing_{field}")
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid_{field}") from None
    if not math.isfinite(parsed) or parsed < 0:
        raise ValueError(f"invalid_{field}")
    if integer:
        if not parsed.is_integer():
            raise ValueError(f"invalid_{field}")
        return int(parsed)
    return parsed


def _validate_movie(movie):
    title = movie.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("missing_title")

    release_date = movie.get("release_date")
    try:
        parsed_date = date.fromisoformat(release_date)
    except (TypeError, ValueError):
        raise ValueError("invalid_release_date") from None

    revenue = _number(movie.get("revenue"), "revenue", required=True, integer=True)
    vote_average = _number(movie.get("vote_average"), "vote_average")
    vote_count = _number(movie.get("vote_count"), "vote_count", integer=True)
    if vote_average is not None and vote_average > 10:
        raise ValueError("invalid_vote_average")

    collection = movie.get("belongs_to_collection")
    if collection is not None and (
        not isinstance(collection, dict) or collection.get("id") is None
    ):
        raise ValueError("invalid_collection_structure")

    return parsed_date.year, revenue, vote_average, vote_count


def validate_status_reconciliation(source, status):
    required = {"source_row", "movie_id", "movie_status", "credits_status"}
    if not required.issubset(status.columns):
        raise ValueError("extraction status is missing required columns")
    if status["source_row"].duplicated().any():
        raise ValueError("extraction status contains duplicate source rows")
    expected_rows = set(source["source_row"].astype(int))
    actual_rows = set(status["source_row"].astype(int))
    if expected_rows != actual_rows:
        missing = sorted(expected_rows - actual_rows)
        extra = sorted(actual_rows - expected_rows)
        raise ValueError(
            f"extraction status does not reconcile; missing={missing}, extra={extra}"
        )
    status_by_row = {
        int(row.source_row): row
        for row in status.itertuples(index=False)
    }
    source_by_row = {
        int(row.source_row): row.tmdb_id
        for row in source.itertuples(index=False)
    }
    mismatches = [
        source_row
        for source_row, source_id in source_by_row.items()
        if status_by_row[source_row].movie_id.strip() != source_id
    ]
    if mismatches:
        raise ValueError(f"source/status IDs differ at rows: {mismatches}")
    return status_by_row


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    source = load_candidate_ids()
    status = pd.read_csv(
        STATUS_PATH,
        dtype=str,
        keep_default_na=False,
    )

    # Map extraction outcomes to each source occurrence.
    status_by_row = validate_status_reconciliation(source, status)

    seen_ids = set()
    audit = []
    movies = []
    genres = []
    cast_rows = []
    directors = []

    for row in source.itertuples(index=False):
        movie_id = row.tmdb_id
        audit_row = {
            "source_row": row.source_row,
            "movie_id": movie_id,
            "transform_status": "excluded",
            "reason": "",
        }

        if not movie_id or not movie_id.isdigit() or int(movie_id) <= 0:
            audit_row["reason"] = "invalid_id"
            audit.append(audit_row)
            continue

        if movie_id in seen_ids:
            audit_row["reason"] = "duplicate_id"
            audit.append(audit_row)
            continue

        seen_ids.add(movie_id)

        extraction = status_by_row.get(row.source_row)
        if extraction is None:
            audit_row["reason"] = "missing_extraction_status"
            audit.append(audit_row)
            continue

        if (
            extraction.movie_status != "success"
            or extraction.credits_status != "success"
        ):
            audit_row["reason"] = (
                f"movie={extraction.movie_status};"
                f"credits={extraction.credits_status}"
            )
            audit.append(audit_row)
            continue

        movie = read_json(RAW_DIR / f"movie_{movie_id}.json")
        credit = read_json(RAW_DIR / f"credits_{movie_id}.json")

        if not isinstance(movie, dict) or not isinstance(credit, dict):
            audit_row["reason"] = "missing_or_invalid_json"
            audit.append(audit_row)
            continue

        if str(movie.get("id")) != movie_id or str(credit.get("id")) != movie_id:
            audit_row["reason"] = "payload_id_mismatch"
            audit.append(audit_row)
            continue

        if not isinstance(movie.get("genres"), list):
            audit_row["reason"] = "invalid_genres_structure"
            audit.append(audit_row)
            continue

        if not isinstance(credit.get("cast"), list) or not isinstance(
            credit.get("crew"), list
        ):
            audit_row["reason"] = "invalid_credits_structure"
            audit.append(audit_row)
            continue

        if any(not isinstance(item, dict) for item in movie["genres"]):
            audit_row["reason"] = "invalid_genre_record"
            audit.append(audit_row)
            continue
        if any(not isinstance(item, dict) for item in credit["cast"]):
            audit_row["reason"] = "invalid_cast_record"
            audit.append(audit_row)
            continue
        if any(not isinstance(item, dict) for item in credit["crew"]):
            audit_row["reason"] = "invalid_crew_record"
            audit.append(audit_row)
            continue

        try:
            release_year, revenue, vote_average, vote_count = _validate_movie(movie)
        except ValueError as exc:
            audit_row["reason"] = str(exc)
            audit.append(audit_row)
            continue

        collection = movie.get("belongs_to_collection")
        collection_name = collection.get("name") if collection else None

        movies.append({
            "movie_id": int(movie_id),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "release_year": release_year,
            "runtime": movie.get("runtime"),
            "revenue": revenue,
            "vote_average": vote_average,
            "vote_count": vote_count,
            "collection_id": (
                collection.get("id")
                if isinstance(collection, dict)
                else None
            ),
            "collection_name": collection_name,
            "licensing_type": (
                "franchise" if collection is not None else "standalone_proxy"
            ),
        })

        for genre in movie["genres"]:
            if isinstance(genre, dict):
                genres.append({
                    "movie_id": int(movie_id),
                    "genre_id": genre.get("id"),
                    "genre_name": genre.get("name"),
                })

        for person in credit["cast"]:
            if isinstance(person, dict):
                cast_rows.append({
                    "movie_id": int(movie_id),
                    "person_id": person.get("id"),
                    "person_name": person.get("name"),
                    "character": person.get("character"),
                    "cast_order": person.get("order"),
                })

        for person in credit["crew"]:
            if (
                isinstance(person, dict)
                and person.get("job") == "Director"
            ):
                directors.append({
                    "movie_id": int(movie_id),
                    "person_id": person.get("id"),
                    "director_name": person.get("name"),
                })

        audit_row["transform_status"] = "included"
        audit_row["reason"] = "validated"
        audit.append(audit_row)

    outputs = {
        "movies.csv": movies,
        "movie_genres.csv": genres,
        "cast.csv": cast_rows,
        "directors.csv": directors,
        "transform_status.csv": audit,
    }

    for filename, records in outputs.items():
        pd.DataFrame(records).to_csv(
            PROCESSED_DIR / filename,
            index=False,
        )
        print(f"Saved {filename}: {len(records)} rows")

    print("\nTransformation summary:")
    print(pd.DataFrame(audit)["reason"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
