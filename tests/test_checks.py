import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "check_tmdb_client.py"
)

SPEC = importlib.util.spec_from_file_location("check_tmdb_client", SCRIPT_PATH)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class FakeTMDbClient:
    def __init__(self, movie, credits):
        self.movie = movie
        self.credits = credits
        self.calls = []

    def fetch(self, movie_id, endpoint):
        self.calls.append((movie_id, endpoint))
        return self.movie if endpoint == "movie" else self.credits


class ManualCheckTests(unittest.TestCase):
    def test_main_checks_movie_and_credit_payloads(self):
        client = FakeTMDbClient(
            {"id": 155, "title": "The Dark Knight"},
            {"id": 155, "cast": [{"id": 1}]},
        )
        output = io.StringIO()

        with patch.object(
            checks, "TMDbClient", return_value=client
        ) as client_factory:
            with contextlib.redirect_stdout(output):
                checks.main()

        client_factory.assert_called_once_with(force_refresh=True)
        self.assertEqual(client.calls, [(155, "movie"), (155, "credits")])
        self.assertIn("The Dark Knight", output.getvalue())
        self.assertIn("Client checks passed.", output.getvalue())

    def test_main_fails_when_movie_id_does_not_match(self):
        client = FakeTMDbClient(
            {"id": 999, "title": "Wrong movie"},
            {"id": 155, "cast": []},
        )

        with patch.object(checks, "TMDbClient", return_value=client):
            with self.assertRaises(AssertionError):
                checks.main()


if __name__ == "__main__":
    unittest.main()
