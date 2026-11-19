# Data Contract: StreamVault Movie Licensing Analysis

## Purpose

This document defines the source-data expectations, validation rules, extraction outcomes, transformation requirements, and analytical constraints for the StreamVault licensing analysis. It reflects the observed candidate data and the handling implemented in the project, while distinguishing verified behaviour from requirements that must be checked against the current implementation.

- **Parties:** StreamVault content acquisition team (consumer) and The Movie Database (TMDb) (data provider)
- **Version:** 1.0
- **Last reviewed:** 2026-11-19

**Change control:** Changes to source structure, required fields, classification rules, or analytical outputs must be reviewed before implementation. Update the relevant tests, documentation, and ADRs when a change affects an accepted project decision.

## Source data and extraction

| Rule | If it is broken | Where |
|---|---|---|
| The candidate source is `id_list.csv`. | The pipeline stops if the required source file cannot be read. | `pipeline/extract.py` and `pipeline/transform.py`. |
| The source contains a `tmdb_id` column. | A missing required column is reported as a source-schema error. | `pipeline/extract.py` and `pipeline/transform.py`. |
| Source attribution is not present in the supplied file. | Do not infer which of the three named sources supplied an ID. Capture provenance during future intake when available. | Source limitation; `docs/adr/ADR-001-source-record-accounting.md`. |
| Each source occurrence must be accounted for, including blank lines and invalid identifiers. | The extraction audit must preserve the record's disposition rather than silently dropping it. | Extraction logic and `data/processed/extraction_status.csv`. |
| A valid movie identifier must be a positive numeric TMDb ID. | Do not send invalid identifiers to the API; record the occurrence as `invalid_id`. | `pipeline/extract.py`. |
| Repeated valid IDs must not cause repeated analytical movie records. | Preserve the occurrence in the audit and mark subsequent occurrences as `duplicate_id`. | `pipeline/extract.py` and `pipeline/transform.py`. |
| Movie details and credits must be retrieved for eligible unique IDs. | Record retrieval failures explicitly; do not classify failed retrievals as successful records. | `source_system/tmdb_client.py` and `pipeline/extract.py`. |
| Raw API responses must remain distinguishable from transformed analytical outputs. | Do not use the mere presence of a raw file as proof that a record is eligible for analysis. | `data/raw/` and transformation eligibility rules. |

## Source-record accounting

The supplied candidate file contains 127 physical data lines, including one blank physical line. The blank line is skipped by default by Pandas unless blank-line handling is configured explicitly.

The observed source accounting is:

| Disposition | Expected count |
|---|---:|
| Successfully extracted unique movie records | 112 |
| Subsequent duplicate occurrences | 6 |
| Invalid records, including the blank record | 4 |
| Not-found IDs | 5 |
| **Total source records accounted for** | **127** |

The counts above describe the observed extraction run and must be revalidated whenever the candidate file changes.

| Rule | If it is broken | Where |
|---|---|---|
| Every physical source record receives a recorded disposition. | Fail reconciliation and investigate the missing or extra records. | Extraction audit and `data/processed/extraction_status.csv`. |
| Extraction-status counts reconcile to the physical source-record count. | Do not treat the run as complete until the discrepancy is explained. | Extraction reconciliation and tests. |
| Duplicate and invalid records remain visible in the audit. | Do not silently remove them from source accounting. | Extraction-status generation. |
| A not-found response is distinguishable from an invalid identifier or duplicate occurrence. | Record the correct outcome and retain sufficient context to investigate it. | TMDb client and extraction-status generation. |

## Movie payload

The movie-details response supplies the fields used to build the analytical movie dataset. The pipeline must validate required structures and handle optional values explicitly.

| Field or structure | Requirement | If it is broken | Where |
|---|---|---|---|
| `id` | Must match the requested TMDb movie ID. | Reject or flag the payload; do not associate it with the wrong candidate. | `source_system/tmdb_client.py` and `pipeline/transform.py`. |
| `title` | Required and nonempty for identification and reporting. | Exclude the row from analytical output and record `missing_title`. | `pipeline/transform.py`. |
| `release_date` | Must be a valid ISO date; release year is derived from the parsed date. | Do not invent a release year. Exclude the row and record `invalid_release_date`. | `pipeline/transform.py`. |
| `revenue` | Must be a nonnegative integer theatrical-revenue value used for historical comparisons. Zero is valid. | Exclude malformed or missing revenue and record its validation reason. Do not interpret revenue as streaming revenue or licensing price. | `pipeline/transform.py`. |
| `vote_average` | Optional numeric TMDb rating in the 0–10 range, used as supporting context. | Preserve missing values; exclude a malformed value and record its validation reason. | `pipeline/transform.py` and licensing analysis. |
| `vote_count` | Optional nonnegative integer count of TMDb votes, used as supporting context. | Preserve missing values; exclude a malformed value and record its validation reason. | `pipeline/transform.py` and licensing analysis. |
| `genres` | Expected to be a list of genre objects. | Flag unexpected structures before flattening. | `source_system/tmdb_client.py` and `pipeline/transform.py`. |
| `belongs_to_collection` | Expected to be a collection object or `None`. | Flag unexpected structures. Do not infer a collection from the movie title alone. | `pipeline/transform.py`. |
| Optional movie attributes | Optional values must not be silently replaced with invented facts. | Preserve missingness or apply an explicitly documented transformation rule. | Transformation pipeline. |

## Credits payload

| Field or structure | Requirement | If it is broken | Where |
|---|---|---|---|
| `id` | Must match the requested movie ID. | Reject or flag mismatched credits. | Credits payload validation. |
| `cast` | Expected to be a list of cast-member objects. | Flag unexpected structures before transformation. | Credits validation and cast transformation. |
| `crew` | Expected to be a list of crew-member objects. | Flag unexpected structures before transformation. | Credits validation and director transformation. |
| Cast and crew identifiers | Preserve TMDb identifiers where available to support consistent entity references. | Do not invent identifiers for missing values. | Cast and director transformation. |
| Lead-actor proxy | The first cast member returned by TMDb is used as a proxy when producing the specified lead-actor summary. | Describe this as a proxy; do not claim it always identifies the actual lead actor. | Licensing analysis. |
| Director attribution | Director summaries are derived from matching crew records. | Avoid attributing a movie to a director when the relevant crew record is unavailable or ambiguous. | Credits transformation and licensing analysis. |

## Transformed outputs

The transformed dataset separates movie-level information from repeated genre, cast, and director records.

| Output | Requirement | If it is broken | Where |
|---|---|---|---|
| `data/processed/movies.csv` | One eligible analytical record per successfully processed unique movie. | Fail validation if duplicate movie IDs or invalid required fields remain. | Transformation pipeline and tests. |
| `data/processed/movie_genres.csv` | Represents movie-to-genre relationships without duplicating movie-level records. | Flag malformed relationships or references to unknown movie IDs. | Genre transformation and tests. |
| `data/processed/cast.csv` | Represents cast relationships for eligible movies. | Flag malformed records and invalid movie references. | Cast transformation and tests. |
| `data/processed/directors.csv` | Represents director relationships for eligible movies. | Flag malformed records and invalid movie references. | Director transformation and tests. |
| `data/processed/transform_status.csv` | Accounts for the original 127 source occurrences and records transformation dispositions. | Fail reconciliation if source occurrences are missing, duplicated unexpectedly, or assigned inconsistent outcomes. | Transformation status generation and tests. |

The observed transformed outputs contain 112 movie records, 320 movie-genre relationships, 7,827 cast records, and 122 director records. These are observed counts from the current dataset, not permanent expected counts for future runs.

## Classification and analytical rules

| Rule | If it is broken or cannot be established | Where |
|---|---|---|
| A movie with a recorded TMDb collection is classified as `franchise`. | Do not infer collection membership from title similarity alone. | Transformation classification and licensing analysis. |
| A movie without a recorded TMDb collection is classified as `standalone_proxy`. | Do not claim that the movie is legally or commercially available for individual licensing. | Transformation classification and licensing analysis. |
| Franchise collections are ranked by total historical theatrical revenue. | Report the ranking metric and its limitations; do not silently substitute another metric. | Licensing analysis and ADR-004. |
| Standalone proxies are ranked by individual historical theatrical revenue. | Identify the metric as an analyst decision if the client has not specified an alternative. | Licensing analysis and ADR-004. |
| Results are compared across all years and from 2000 onward. | Do not omit either required period. Explicitly flag a reversal if the direction of the comparison changes. | Licensing analysis and ADR-003. |
| Ratings and vote counts provide supporting context. | Do not present them as proof of licensing value or future streaming performance. | Licensing analysis and client memo. |
| Director and lead-actor summaries are descriptive. | Do not infer causation or treat the observed association as a reliable forecast. | Licensing analysis and client memo. |

## Analytical limitations

- TMDb collection membership is a classification proxy, not confirmation that a complete franchise bundle is available for licensing.
- A movie without a recorded collection is a `standalone_proxy`, not a confirmed individually licensable title.
- Revenue is historical theatrical revenue. It is not streaming revenue, licensing price, or profit.
- Revenue comparisons across release years may be affected by inflation and differences in historical reporting.
- The post-2000 standalone comparison contains only eight titles, so its results should be interpreted cautiously.
- Historical revenue rankings do not establish future audience demand, affordability, or expected return on investment.
- The $14M budget cannot be evaluated against a package without actual pricing, territory, rights scope, exclusivity, licensing term, and a defensible estimate of expected streaming value.

## References and traceability

| Document | Responsibility |
|---|---|
| `docs/client_memo.md` | Presents the negotiation recommendation, shortlist, comparisons, deal note, and limitations for Kwame. |
| `docs/data_findings.md` | Reconciles the candidate list and ranks its data-quality and decision risks. |
| `docs/questions.md` | Tracks business questions, evidence available without client responses, and unresolved commercial assumptions. |
| `docs/adr/ADR-001-source-record-accounting.md` | Documents source-record accounting and duplicate handling. |
| `docs/adr/ADR-002-title-classification.md` | Documents the franchise and standalone-proxy classification decision. |
| `docs/adr/ADR-003-comparison-periods.md` | Documents the required comparison periods and revenue-comparability limitations. |
| `docs/adr/ADR-004-ranking-metrics.md` | Documents the ranking metrics and their rationale. |
| `pipeline/run_notebooks.py` | Executes the profiling and licensing notebooks in order and saves their outputs. |
| `explore/data_profiling.ipynb` | Records source and payload profiling evidence. |
| `explore/licensing_analysis.ipynb` | Contains the comparative analysis and ranking outputs. |

The current automated tests cover payload-shape validation, analytical-field validation, and source-to-status reconciliation. The licensing notebook validates movie-key uniqueness and confirms that genre, cast, and director rows refer only to known movies. Re-run the test suite and both notebooks after changing the candidate list or pipeline.
