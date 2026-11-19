import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from source_system.tmdb_client import TMDbClient


class TMDbPayloadValidationTests(unittest.TestCase):
    def test_accepts_movie_payload_with_expected_id_and_genres(self):
        TMDbClient._validate_payload({"id": 155, "genres": []}, 155, "movie")

    def test_accepts_credits_payload_with_expected_id_and_lists(self):
        TMDbClient._validate_payload(
            {"id": 155, "cast": [], "crew": []}, 155, "credits"
        )

    def test_rejects_id_mismatch(self):
        with self.assertRaisesRegex(ValueError, "ID does not match"):
            TMDbClient._validate_payload({"id": 999, "genres": []}, 155, "movie")

    def test_rejects_invalid_nested_structure(self):
        with self.assertRaisesRegex(ValueError, "invalid fields"):
            TMDbClient._validate_payload(
                {"id": 155, "cast": {}, "crew": []}, 155, "credits"
            )


class TMDbManifestCacheTests(unittest.TestCase):
    def test_latest_not_found_outcome_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.jsonl"
            manifest.write_text(
                '{"movie_id": 155, "endpoint": "movie", "status": "success"}\n'
                '{"movie_id": 155, "endpoint": "movie", "status": "not_found"}\n',
                encoding="utf-8",
            )
            with patch("source_system.tmdb_client.MANIFEST_PATH", manifest):
                latest = TMDbClient._load_latest_statuses()
            self.assertEqual(latest[("155", "movie")], "not_found")

    def test_ignores_malformed_manifest_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.jsonl"
            manifest.write_text("bad json\n", encoding="utf-8")
            with patch("source_system.tmdb_client.MANIFEST_PATH", manifest):
                latest = TMDbClient._load_latest_statuses()
            self.assertIsNone(latest[("155", "movie")])


if __name__ == "__main__":
    unittest.main()
