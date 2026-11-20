import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from pipeline import extract
from pipeline.extract import extract_records, prepare_source_records


class FakeTMDbClient:
    api_key = "secret-key"

    def __init__(self, responses=None, error=None):
        self.responses = responses or {}
        self.error = error
        self.calls = []

    def fetch(self, movie_id, endpoint):
        self.calls.append((movie_id, endpoint))
        if self.error:
            raise RuntimeError(self.error)
        return self.responses[(movie_id, endpoint)]


class ExtractionPipelineTests(unittest.TestCase):
    def test_accounts_for_invalid_and_duplicate_rows_without_api_calls(self):
        source, valid, duplicate = prepare_source_records(pd.DataFrame({
            "tmdb_id": [" 155 ", "", "-1", "155", "77"],
        }))
        client = FakeTMDbClient({
            (155, "movie"): {"id": 155},
            (155, "credits"): None,
            (77, "movie"): {"id": 77},
            (77, "credits"): {"id": 77},
        })

        rows = extract_records(source, valid, duplicate, client)

        self.assertEqual([row["source_row"] for row in rows], [2, 3, 4, 5, 6])
        self.assertEqual(
            [(row["movie_status"], row["credits_status"]) for row in rows],
            [
                ("success", "not_found"),
                ("invalid_id", "invalid_id"),
                ("invalid_id", "invalid_id"),
                ("duplicate_id", "duplicate_id"),
                ("success", "success"),
            ],
        )
        self.assertEqual(len(client.calls), 4)
        self.assertEqual(len(rows), len(source))

    def test_redacts_credentials_from_endpoint_errors(self):
        source, valid, duplicate = prepare_source_records(
            pd.DataFrame({"tmdb_id": ["155"]})
        )
        client = FakeTMDbClient(error="request failed with api_key=secret-key")

        with patch("pipeline.extract.time.sleep"):
            rows = extract_records(source, valid, duplicate, client)

        self.assertEqual(rows[0]["movie_status"], "error")
        self.assertEqual(rows[0]["credits_status"], "error")
        self.assertNotIn("secret-key", rows[0]["error"])
        self.assertIn("[redacted]", rows[0]["error"])

    def test_rejects_a_source_without_tmdb_id(self):
        with self.assertRaisesRegex(ValueError, "tmdb_id"):
            prepare_source_records(pd.DataFrame({"other_id": [155]}))

    def test_main_writes_a_reconciled_status_file_without_live_api(self):
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "ids.csv"
            output_path = Path(directory) / "extraction_status.csv"
            source_path.write_text(
                "tmdb_id\n155\n\n155\nbad\n77\n", encoding="utf-8"
            )
            client = FakeTMDbClient({
                (155, "movie"): {"id": 155},
                (155, "credits"): {"id": 155},
                (77, "movie"): {"id": 77},
                (77, "credits"): {"id": 77},
            })

            with (
                patch("pipeline.extract.ID_LIST_PATH", source_path),
                patch("pipeline.extract.EXTRACTION_STATUS_PATH", output_path),
                patch.object(extract, "TMDbClient", return_value=client),
                patch("sys.argv", ["pipeline.extract"]),
            ):
                extract.main()

            with output_path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 5)
        self.assertEqual(
            [row["movie_status"] for row in rows],
            ["success", "invalid_id", "duplicate_id", "invalid_id", "success"],
        )
        self.assertEqual(len(client.calls), 4)


if __name__ == "__main__":
    unittest.main()
