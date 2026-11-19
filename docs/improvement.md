# Improvement beyond the brief: automated reconciliation and validation

## What changed

The pipeline now checks that extraction status accounts for every source row exactly once and that each status row's movie ID matches the ID at that source position. Before a payload can enter the analysis, the workflow checks its requested movie ID, required nested structures, title, release date, revenue, rating, vote count, and collection structure. Invalid or incomplete records are excluded with a reason in the transformation status output.

The TMDb client also reuses recorded `not_found` outcomes on ordinary reruns, avoiding repeat requests for known missing IDs. Use `--refresh` when the intent is to query TMDb again.

## Why this helps

Adjoa is expected to rerun this work quarterly, with the candidate list growing from 127 to about 500 rows. Reconciliation catches missing, extra, duplicated, or misassociated status records before analysis. Payload checks catch malformed data before it can distort rankings. The not-found cache avoids wasting API requests on the same known missing IDs during a routine rerun.

## Evidence

- Reconciliation and analytical-field checks: `pipeline/transform.py`.
- API payload checks and not-found caching: `source_system/tmdb_client.py`.
- Automated tests: `tests/test_extract.py`, `tests/test_transform.py`, `tests/test_tmdb.py`, and `tests/test_checks.py`.
- Validation run: `python -m unittest discover -s tests -v` — 16 tests passed.

The improvement reduces silent data-handling errors; it does not verify current licensing rights, streaming demand, or live API availability. A live refresh still requires a TMDb key and network access.
