import time
from pathlib import Path

import pandas as pd

from source_system.tmdb_client import TMDbClient

INPUT_PATH = Path("id_list.csv")
OUTPUT_PATH = Path("data/processed/extraction_status.csv")


def main():
    # Preserve invalid values and blank lines for reporting.
    input_df = pd.read_csv(
        INPUT_PATH,
        dtype=str,
        keep_default_na=False,
        skip_blank_lines=False,
    )

    input_df["source_row"] = input_df.index + 2
    input_df["tmdb_id"] = input_df["tmdb_id"].str.strip()

    # Accept positive integer IDs only.
    valid_mask = input_df["tmdb_id"].str.fullmatch(r"[1-9]\d*")

    # Identify duplicate valid IDs without discarding their records.
    duplicate_mask = (
        valid_mask
        & input_df["tmdb_id"].duplicated(keep=False)
    )

    client = TMDbClient()
    results = []

    for position, row in enumerate(
        input_df.itertuples(index=False)
    ):
        raw_id = row.tmdb_id
        source_row = row.source_row

        outcome = {
            "source_row": source_row,
            "movie_id": raw_id,
            "movie_status": "not_attempted",
            "credits_status": "not_attempted",
            "error": None,
        }

        # Keep invalid IDs in the report without calling the API.
        if not valid_mask.iloc[position]:
            outcome["movie_status"] = "invalid_id"
            outcome["credits_status"] = "invalid_id"
            results.append(outcome)
            continue

        # Report duplicate IDs instead of fetching them repeatedly.
        if duplicate_mask.iloc[position]:
            outcome["movie_status"] = "duplicate_id"
            outcome["credits_status"] = "duplicate_id"
            results.append(outcome)
            continue

        movie_id = int(raw_id)

        for endpoint in ("movie", "credits"):
            try:
                payload = client.fetch(movie_id, endpoint)

                if payload is None:
                    outcome[f"{endpoint}_status"] = "not_found"
                else:
                    outcome[f"{endpoint}_status"] = "success"

            except Exception as exc:
                outcome[f"{endpoint}_status"] = "error"
                error_message = (
                    f"{endpoint}: {type(exc).__name__}: {exc}"
                )
                outcome["error"] = (
                    f"{outcome['error']}; {error_message}"
                    if outcome["error"]
                    else error_message
                )
                time.sleep(1)

        results.append(outcome)

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

    assert len(status) == len(input_df)


if __name__ == "__main__":
    main()