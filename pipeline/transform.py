
import json
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
    source["source_row"] = source.index + 2
    source["tmdb_id"] = source["tmdb_id"].str.strip()
    return source


def read_json(path):
    """Load a JSON file, returning None when it cannot be read."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    source = load_candidate_ids()
    status = pd.read_csv(
        STATUS_PATH,
        dtype=str,
        keep_default_na=False,
    )

    # Map extraction outcomes to each source occurrence.
    status_by_row = {
        int(row.source_row): row
        for row in status.itertuples(index=False)
    }

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

        collection = movie.get("belongs_to_collection")
        collection_name = (
            collection.get("name")
            if isinstance(collection, dict)
            else None
        )

        movies.append({
            "movie_id": int(movie_id),
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "release_year": (
                int(movie["release_date"][:4])
                if isinstance(movie.get("release_date"), str)
                and len(movie["release_date"]) >= 4
                and movie["release_date"][:4].isdigit()
                else None
            ),
            "runtime": movie.get("runtime"),
            "revenue": movie.get("revenue"),
            "vote_average": movie.get("vote_average"),
            "vote_count": movie.get("vote_count"),
            "collection_id": (
                collection.get("id")
                if isinstance(collection, dict)
                else None
            ),
            "collection_name": collection_name,
            "licensing_type": (
                "franchise" if collection_name else "standalone_proxy"
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
