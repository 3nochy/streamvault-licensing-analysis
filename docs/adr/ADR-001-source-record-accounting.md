# ADR-001: Preserve and reconcile every source record

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owner:** Data Engineering

## Context

The client supplied 127 source records. The list contains valid IDs, duplicate IDs, invalid entries, a blank row, and IDs that could not be found on TMDb. The client requires a defensible analysis and a full account of the source data. Silently dropping records would make the extraction results difficult to audit and could obscure data-quality limitations.

## Decision

Preserve all 127 source records in the extraction-status accounting, assign each record an explicit outcome, and use only successfully extracted, validated, unique movies in the movie-level analysis.

## Alternatives considered

### Alternative A: Remove unusable records before extraction

- **How it would work:** Delete blank, invalid, duplicate, and not-found records before recording extraction outcomes.
- **Why it is attractive:** Produces a smaller, simpler working dataset.
- **Why rejected:** Hides the extent and nature of source-data problems and prevents full reconciliation to the client's original list.

### Alternative B: Stop the entire pipeline when a record fails

- **How it would work:** Halt processing whenever an invalid ID, duplicate, or not-found movie is encountered.
- **Why it is attractive:** Prevents the pipeline from continuing with problematic records.
- **Why rejected:** One unusable record would prevent analysis of the remaining valid records, even when their data can be processed reliably.

### Alternative C: Preserve records and record explicit outcomes

- **How it would work:** Retain source-row accounting, classify each outcome, and exclude unusable records only from analyses that require valid movie data.
- **Why it is attractive:** Maintains traceability while allowing valid records to proceed through the pipeline.
- **Why rejected:** Not rejected. This is the selected approach.

## Consequences

- **What this buys:** All 127 source records can be reconciled: 112 successful extractions, 6 duplicate occurrences, 4 invalid records including the blank row, and 5 not-found IDs.
- **What this costs:** Additional status tracking, validation, and documentation are required.
- **What it costs the client if I am wrong:** Dropping or misclassifying records could distort the shortlist, conceal source-data problems, or make the analysis difficult to reproduce and audit.
- **What would make me revisit this:** A revised source file, a change to the client's record-accounting requirements, or evidence that the current classification rules misrepresent source records.

## What this survives

The same accounting approach can be reused when the candidate list grows from 127 records to approximately 500, without silently losing records as the pipeline scales.
