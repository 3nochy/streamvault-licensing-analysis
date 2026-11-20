# ADR-005: Keep the pipeline simple and rely on the local cache for 500 titles

- **Status:** Accepted
- **Date:** 2026-11-20
- **Decision owner:** Data Engineering

## Context

Next year's list is expected to be about 500 titles, up from 127. Adjoa will rerun the analysis quarterly on her own laptop, sometimes live in a meeting.

## Decision

Keep the sequential download with a short delay between requests. Save every response locally so reruns do not call the API again. Adjoa runs the download before the meeting and runs only the analysis in the room.

## Alternatives considered

### Alternative A: Download many films in parallel
- **Why it is attractive:** Faster first download.
- **Why rejected:** TMDb rate-limits requests, and parallel calls risk blocks and failures that Adjoa cannot easily fix. The download only needs to be fast once per quarter.

### Alternative B: Rewrite the pipeline as a database or cloud job
- **Why it is attractive:** Handles far larger lists.
- **Why rejected:** 500 films is small. Adjoa needs something she can run on a laptop with no setup.

### Alternative C: Keep it simple and use the cache (selected)

## Measured results

Download, measured on the real 127-row list (Ubuntu on WSL, 20 Nov 2026):
- Fresh download (`--refresh`): 2 min 3 s.
- Cached rerun: 9 s.
- Scaled to 500 titles, assuming time grows in line with row count: about 8 min fresh and about 35 s cached. This is an estimate, not a measurement.

Transform and analysis, measured on a **synthetic 500-row test set**, not 500 distinct real TMDb titles. The test was created by relabelling the 112 cached films with new IDs, so it measures pipeline handling of a larger row count but does not validate 500-title data quality or API acquisition performance.

- Transform: 0.86 s; all 500 synthetic rows validated.
- Analysis: 0.012 s on the synthetic test set.

## What the recommendation would look like under the alternatives

- **If parallel download were used:** the first run could be faster, but it could fail on rate limits during a meeting.
- **If a database were used:** no change to the results, but Adjoa would have more to maintain.

## Consequences

- **What this buys:** A pipeline Adjoa can run alone, with results that are easy to check.
- **What this costs:** The fresh download takes minutes, and Adjoa must run it before the meeting.
- **What it costs the client if I am wrong:** If the live download is much slower than the scaled estimate, the analysis may not be ready for the meeting.
- **What would make me revisit this:** A list of several thousand titles, or a measured 500-title download much slower than 8 minutes.

## What this survives

Cached files, the one-row-per-source audit and the validation checks work the same at 500 titles. A refresh changes ratings and vote counts: a second download on the same day changed vote counts for all 112 films. Revenue, release dates and collections did not change. Results that use ratings can therefore shift slightly between runs, while revenue rankings stay stable.
