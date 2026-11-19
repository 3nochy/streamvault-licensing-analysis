import unittest

import pandas as pd

from pipeline.transform import _validate_movie, validate_status_reconciliation


class TransformValidationTests(unittest.TestCase):
    def test_parses_analytical_movie_fields(self):
        movie = {
            "title": "Example",
            "release_date": "2001-02-03",
            "revenue": 0,
            "vote_average": 7.5,
            "vote_count": 4,
            "belongs_to_collection": None,
        }
        self.assertEqual(_validate_movie(movie), (2001, 0, 7.5, 4))

    def test_rejects_malformed_release_date_and_revenue(self):
        base = {
            "title": "Example",
            "release_date": "2001-02-03",
            "revenue": 10,
            "belongs_to_collection": None,
        }
        with self.assertRaisesRegex(ValueError, "invalid_release_date"):
            _validate_movie({**base, "release_date": "2001-99-99"})
        with self.assertRaisesRegex(ValueError, "invalid_revenue"):
            _validate_movie({**base, "revenue": "unknown"})

    def test_rejects_unreconciled_source_status_rows(self):
        source = pd.DataFrame({"source_row": [2], "tmdb_id": ["155"]})
        status = pd.DataFrame({
            "source_row": [3],
            "movie_id": ["155"],
            "movie_status": ["success"],
            "credits_status": ["success"],
        })
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            validate_status_reconciliation(source, status)

    def test_rejects_status_id_mismatch(self):
        source = pd.DataFrame({"source_row": [2], "tmdb_id": ["155"]})
        status = pd.DataFrame({
            "source_row": [2],
            "movie_id": ["156"],
            "movie_status": ["success"],
            "credits_status": ["success"],
        })
        with self.assertRaisesRegex(ValueError, "IDs differ"):
            validate_status_reconciliation(source, status)


if __name__ == "__main__":
    unittest.main()
