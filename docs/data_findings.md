# Data findings — StreamVault

**Prepared for:** Kwame Boateng, VP of Content Acquisition  
**Prepared by:** Adjoa, Content Acquisition  
**Evidence reviewed:** `id_list.csv`, `data/processed/extraction_status.csv`, `data/processed/transform_status.csv`, transformed movie data, and the analysis exports in `out/`  
**Assessment date:** 19 November 2026

## Summary

The file has 127 data rows: 126 nonblank candidate entries and one blank row. The final analysis contains 112 unique movies: 96 with a TMDb collection and 16 without one (used as standalone proxies). Of the 126 nonblank entries, 112 were analyzed, six repeat an already-listed ID, five valid IDs were not found, and three contain malformed IDs. The blank row is accounted for separately. The five unavailable candidates and three malformed entries leave eight potentially assessable titles out of the evidence; their effect on the rankings is unknown. The revenue comparison favors franchise candidates in both periods, supporting negotiation priority only—not a purchase or budget commitment.

## Reconciliation

| Stage | Rows | Delta | Reason |
|---|---:|---:|---|
| Source file data rows | 127 | — | 128 physical CSV lines including the header. |
| Nonblank candidate entries | 126 | −1 | One of the 127 data rows is blank (physical line 69). |
| Valid numeric ID occurrences | 123 | −3 | Three nonblank entries are malformed: `-1`, `tt0468569`, and `N/A`. |
| Unique valid IDs sent for lookup | 117 | −6 | Six later occurrences repeat an ID already listed. |
| TMDb movie and credits records found | 112 | −5 | Five unique numeric IDs returned not found from both endpoints. |
| Final transformed movie records | 112 | 0 | All 112 successful movie/credits pairs passed transformation validation. |
| Final analysis categories | 112 | 0 | 96 have a recorded collection; 16 have no recorded collection and are standalone proxies. |

The candidate-entry reconciliation is 112 analyzed + 6 duplicate entries + 5 valid IDs not found + 3 malformed entries = 126 nonblank entries. Add the one blank row to reconcile to 127 source data rows. Thus, 15 rows are not separate analyzed films: six duplicates do not represent additional titles, five unavailable IDs and three malformed entries may represent titles that could not be assessed, and one row is blank. The eight unresolved nonblank entries could change the analysis, but their impact cannot be quantified without corrected/retrieved records. Extraction and transformation status files each retain one row per source occurrence. The analysis joins are checked for unique movie IDs and for child records referring only to included movies.

The final count of 112 is unique retrieved movies, not 112 of 127 distinct intended titles: the source has six duplicate occurrences, and the intended titles behind three malformed values are unknown.

## Findings, ranked by risk

### F-01: No deal economics or streaming evidence — Severity: Critical

- **What it is:** The materials contain no licensing quotes, rights scope, territory, exclusivity, term, streaming demand, or expected platform value. The $14 million budget is not enough to assess affordability.
- **How I detected it:** Compared the requested decision and budget in the brief with the fields supplied in the candidate list and the TMDb movie and credits responses.
- **Scale:** Applies to every candidate and all $14 million under consideration.
- **Effect on Kwame's recommendation:** Keep franchise targets first in the negotiation queue if useful, but do not treat the revenue ranking as an offer price, expected return, or basis to commit the $14 million. The Avengers Collection leads the available revenue ranking at $7.92 billion across four candidate-list films; that number is not its licensing value.
- **What I did about it:** Limited the recommendation to negotiation priority. The memo calls for a quote, verified rights, and an independent streaming-value estimate before a commitment.
- **Residual risk:** Kwame cannot make an evidence-backed affordability or return decision until commercial terms and demand evidence are supplied.

### F-02: Five valid candidate IDs were not found — Severity: High

- **What it is:** TMDb returned not found for IDs 8471293, 9412887, 8471294, 9412888, and 7733901. Both movie and credits lookups failed for each.
- **How I detected it:** Recorded endpoint outcomes for each unique valid ID in the extraction status file and reconciled them to the input rows.
- **Scale:** 5 of 117 unique valid IDs (4.3%); 5 of 127 supplied rows (3.9%).
- **Effect on Kwame's recommendation:** The franchise-first negotiation priority is conditional on the 112 retrieved titles. These five could change medians, shortlists, or franchise totals; their direction and size of effect are unknown.
- **What I did about it:** Preserved the source rows and not-found status, excluded them from calculations, and did not guess replacement IDs.
- **Residual risk:** Confirm the IDs with the submitters or rights desk. Until then, rankings are conditional on the 112 retrieved titles.

### F-03: TMDb collection membership is only a licensing proxy — Severity: High

- **What it is:** The analysis labels a film as a franchise candidate when TMDb supplies a collection and labels a film without one as a standalone proxy. TMDb metadata does not establish how a studio packages or licenses rights.
- **How I detected it:** Compared the fields available from the movie endpoint with the brief's commercial distinction between all-or-none franchise bundles and individually priced standalone titles. The data contains no rights-holder package or availability field.
- **Scale:** 96 collection-associated movies and 16 no-collection movies in the final set.
- **Effect on Kwame's recommendation:** Treat franchise and standalone rankings as screening groups only. The actual offers may classify or package titles differently, so this comparison cannot settle which deal type to buy.
- **What I did about it:** Applied the same metadata rule to every title, labeled the categories as candidates/proxies, and stated the limitation in the memo and classification decision record.
- **Residual risk:** Verify package contents and individual availability with each rights holder before negotiating or comparing prices.

### F-04: Historical theatrical revenue is not comparable deal value — Severity: High

- **What it is:** Revenue is nominal historical theatrical revenue. It is not adjusted for inflation, historical reporting differences, or currency effects and is not streaming revenue or profit.
- **How I detected it:** Reviewed the available revenue and release-year fields and compared them with Finance's stated concern about pre-2000 data. No adjustment basis or streaming metrics were supplied.
- **Scale:** All 112 included films; the all-years comparison includes pre-2000 releases. The post-2000 standalone sample has only 8 films.
- **Effect on Kwame's recommendation:** Franchise candidates rank higher on median theatrical revenue in both windows, so the screening priority does not reverse. This is not evidence that bundles will earn more on StreamVault; the eight-title recent standalone sample is also small.
- **What I did about it:** Reported both windows with counts, kept the revenue measure consistent, and treated it as a negotiation-screening signal only.
- **Residual risk:** Rankings and differences could change with inflation-adjusted financial data, verified reporting comparability, or streaming-demand evidence.

### F-05: Candidate source provenance is absent — Severity: Medium

- **What it is:** The brief says the list was assembled from three sources, but `id_list.csv` contains only a TMDb ID column and no source, submitter, or intake date.
- **How I detected it:** Inspected the supplied CSV schema; there is no field connecting an occurrence to Adjoa's tracker, the inherited spreadsheet, or the studio email.
- **Scale:** All 127 source rows.
- **Effect on Kwame's recommendation:** No candidate can be prioritized or discounted based on which of the three sources supplied it. The team also cannot efficiently trace the five missing IDs or questionable entries to their submitters.
- **What I did about it:** Preserved the list as supplied and did not infer provenance. Recommended adding source attribution to future intake.
- **Residual risk:** The current list cannot be audited by source; missing provenance cannot be reconstructed from TMDb IDs alone.

### F-06: Four rows cannot be looked up — Severity: Medium

- **What it is:** Physical source rows 30 (`-1`), 69 (blank), 95 (`tt0468569`), and 111 (`N/A`) are not positive numeric TMDb IDs.
- **How I detected it:** Validated each source value before making API requests and retained invalid rows in the status output.
- **Scale:** 4 of 127 rows (3.1%).
- **Effect on Kwame's recommendation:** Three nonblank entries may be intended candidates but are unassessed; the fourth invalid row is blank and identifies no candidate. The intended titles and any ranking effect cannot safely be inferred, so no replacement should be guessed.
- **What I did about it:** Skipped API calls for invalid values and recorded each as `invalid_id`; retained physical source-row numbering, including the blank row.
- **Residual risk:** Ask the original submitters to correct these entries. The analysis remains incomplete if they were intended to identify valid candidates.

### F-07: Repeated IDs would inflate counts if treated as separate films — Severity: Low

- **What it is:** Six of the 123 valid numeric ID occurrences repeat an earlier occurrence, leaving 117 unique valid IDs.
- **How I detected it:** Counted valid source occurrences and unique IDs, then checked extraction outcomes and the transformed movie ID uniqueness.
- **Scale:** 6 duplicate occurrences (4.7% of source rows); no duplicate analytical movie records remain.
- **Effect on Kwame's recommendation:** Deduplication prevents repeated titles from receiving extra weight. These six rows do not reduce the set of unique retrieved movies and do not change the current recommendation when counted once.
- **What I did about it:** Kept each occurrence in the audit, marked subsequent occurrences `duplicate_id`, and analyzed each unique movie once.
- **Residual risk:** None from these six repeats in the current analysis; future reruns must preserve the same deduplication rule.

### F-08: An earlier saved profiling snapshot was stale — Severity: Low; corrected

- **What it is:** An earlier notebook snapshot showed 107 raw files and 106 successful extractions, while the reconciled current outputs contain 112 successful unique records.
- **How I detected it:** Compared saved notebook outputs with extraction status, raw-file counts, and transformation status.
- **Scale:** The prior snapshot understated successful coverage by 6 records and showed inconsistent totals.
- **Effect on Kwame's recommendation:** The old snapshot could have understated the evidence and distorted the shortlist. The notebooks were rerun, so the current recommendation uses the refreshed 112-film dataset.
- **What I did about it:** Reran both notebooks after the pipeline outputs were corrected and refreshed their saved outputs.
- **Residual risk:** Notebook snapshots can become stale after data or code changes; rerun `python -m pipeline.run_notebooks` after regenerating the processed data.

### F-09: Talent summaries are descriptive, not reliable predictors — Severity: Low

- **What it is:** Director and actor revenue summaries describe overlapping credits in this candidate set. The first cast-listed person is used as a lead-actor proxy; TMDb cast order does not verify a contractual or billing lead.
- **How I detected it:** Reviewed the available credits structure and compared repeated talent credits, including overlapping Russo brothers franchise films.
- **Scale:** The sample is limited to people with at least two included films; Robert Downey Jr. has seven listed credits and the Russo brothers have two overlapping credits each.
- **Effect on Kwame's recommendation:** Use talent summaries as context only; they do not justify moving a title up the negotiation list as a reliable predictor of streaming performance.
- **What I did about it:** Reported talent only as descriptive context and labeled cast order zero as a proxy.
- **Residual risk:** Independent performance evidence and streaming audience data would be needed to use talent as a predictive acquisition signal.

## Looked wrong, is not wrong

| Apparent problem | Why it looks wrong | Why it is actually fine |
|---|---|---|
| 128 physical CSV lines versus 127 rows in the audit | The counts differ by one. | There are 128 physical lines including the header and 127 data occurrences; the status file intentionally keeps the blank data row on physical line 69. |
| A normal Pandas read shows 126 records | The default CSV reader skips a blank line. | The extraction explicitly preserves the blank occurrence, so all 127 data rows reconcile. |
| Extraction has 112 successes, while 117 IDs were looked up | Five IDs appear to have vanished. | They remain accounted for with `not_found` outcomes on both endpoints; only successful unique records enter analysis. |
| Collection counts and standalone counts total 112 despite 127 source rows | Fifteen rows are not in the final movie-level dataset. | Those are exactly 6 duplicates, 5 not-found IDs, and 4 invalid rows; every one has a recorded disposition. |
| The all-years and post-2000 comparisons use different sample sizes | Removing earlier releases changes group sizes and may change comparisons. | That is the required time-window analysis. The sample sizes are reported explicitly; the revenue direction remains franchise-favoring in both windows. |
| Five standalone shortlist titles differ after restricting to 2000 onward | The shortlist is not identical in both periods. | The all-years list includes pre-2000 films; the recent list is separately ranked on its eligible titles, as required. |
| Some included movies have zero revenue in the source | Zero can look like missing or failed data. | Zero is retained as a valid nonnegative revenue value by the documented rule. None of the 112 included movies has zero revenue in this snapshot. |

## Could not verify

- Whether TMDb's 112 returned records reflect the latest metadata, or why the five valid numeric IDs are unavailable.
- The correct titles intended by the four invalid rows, including the blank row.
- Which of the three candidate sources supplied each occurrence.
- Whether each TMDb collection matches a studio's actual bundle, or which titles are licensable individually.
- Current rights ownership, package availability, territory, exclusivity, term, and quoted prices.
- Streaming demand, expected subscriber value, profitability, or a defensible offer price.
- Whether nominal historical revenue is comparable across years, currencies, and reporting practices; no inflation adjustment was applied.
- Whether the first cast-listed person is the commercially relevant lead, or whether director and actor records predict future performance.

These gaps mean the analysis supports a negotiation shortlist and screening comparison only. They do not support committing the $14 million.
