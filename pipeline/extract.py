import argparse
import time

import pandas as pd

from pipeline.config import (
    EXTRACTION_STATUS_PATH as OUTPUT_PATH,
    ID_LIST_PATH as INPUT_PATH,
)
from source_system.tmdb_client import TMDbClient


def prepare_source_records(input_df):
    """Validate source columns and flag valid first-occurrence IDs."""
    if "tmdb_id" not in input_df.columns:
        raise ValueError("id_list.csv must contain a 'tmdb_id' column")

    source = input_df.copy()
    source["source_row"] = source.index + 2
    source["tmdb_id"] = source["tmdb_id"].str.strip()
    valid_mask = source["tmdb_id"].str.fullmatch(r"[1-9]\d*")
    duplicate_mask = valid_mask & source["tmdb_id"].duplicated(keep="first")
    return source, valid_mask, duplicate_mask


def extract_records(input_df, valid_mask, duplicate_mask, client):
    """Return one movie/credits outcome for every source row."""
    results = []
    for position, row in enumerate(input_df.itertuples(index=False)):
        raw_id = row.tmdb_id
        outcome = {
            "source_row": row.source_row,
            "movie_id": raw_id,
            "movie_status": "not_attempted",
            "credits_status": "not_attempted",
            "error": None,
        }

        if not valid_mask.iloc[position]:
            outcome["movie_status"] = "invalid_id"
            outcome["credits_status"] = "invalid_id"
            results.append(outcome)
            continue

        if duplicate_mask.iloc[position]:
            outcome["movie_status"] = "duplicate_id"
            outcome["credits_status"] = "duplicate_id"
            results.append(outcome)
            continue

        for endpoint in ("movie", "credits"):
            try:
                payload = client.fetch(int(raw_id), endpoint)
                outcome[f"{endpoint}_status"] = (
                    "not_found" if payload is None else "success"
                )
            except Exception as exc:
                outcome[f"{endpoint}_status"] = "error"
                safe_error = str(exc)
                if client.api_key:
                    safe_error = safe_error.replace(client.api_key, "[redacted]")
                error_message = f"{endpoint}: {type(exc).__name__}: {safe_error}"
                outcome["error"] = (
                    f"{outcome['error']}; {error_message}"
                    if outcome["error"]
                    else error_message
                )
                time.sleep(1)

        results.append(outcome)
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract TMDb movie and credits data")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="fetch from TMDb even when a local response cache exists",
    )
    args = parser.parse_args()

    # Preserve invalid values and blank lines for reporting.
    input_df = pd.read_csv(
        INPUT_PATH,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False,
    )

    input_df, valid_mask, duplicate_mask = prepare_source_records(input_df)

    client = TMDbClient(force_refresh=args.refresh)
    results = extract_records(input_df, valid_mask, duplicate_mask, client)

    # Retain one status row for every input row.
    status = pd.DataFrame(results)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    status.to_csv(OUTPUT_PATH, index=False)

    print("Input rows:", len(input_df))
    print("Status rows:", len(status))
    print("Valid unique IDs:", int((valid_mask & ~duplicate_mask).sum()))
    print("Invalid IDs:", int((~valid_mask).sum()))
    print("Duplicate ID rows:", int(duplicate_mask.sum()))

    print("\nMovie endpoint outcomes:")
    print(status["movie_status"].value_counts(dropna=False))
    print("\nCredits endpoint outcomes:")
    print(status["credits_status"].value_counts(dropna=False))

    print("\nSaved:", OUTPUT_PATH)

    if len(status) != len(input_df):
        raise RuntimeError(
            f"Extraction reconciliation failed: {len(input_df)} source rows, "
            f"{len(status)} status rows"
        )


if __name__ == "__main__":
    main()
