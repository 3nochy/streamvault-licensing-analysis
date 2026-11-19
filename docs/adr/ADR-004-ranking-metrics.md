# ADR-004: Use theatrical revenue as the primary ranking metric and ratings as supporting evidence

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owner:** Data Engineering

## Context

The client needs a shortlist of three franchise targets and five standalone titles, supported by clear reasons. The available TMDb data includes theatrical revenue, audience ratings, vote counts, release years, collection membership, directors, and cast information. The brief does not provide licensing prices, streaming performance, contractual rights, or profitability data.

## Decision

Rank franchise collections by total theatrical revenue and rank standalone proxies by individual theatrical revenue. Use median movie revenue, audience ratings, vote counts, release years, and director or lead-actor summaries as supporting context, while clearly stating that these measures do not establish streaming demand, licensing value, or profitability.

## Alternatives considered

### Alternative A: Rank candidates by audience rating alone

- **How it would work:** Use TMDb audience ratings as the primary ranking metric.
- **Why it is attractive:** Ratings provide a signal of audience reception and help identify well-regarded titles.
- **Why rejected:** Ratings do not measure commercial performance, and vote counts vary. Rating alone does not meet the client's need for a financially informed licensing comparison.

### Alternative B: Rank candidates by theatrical revenue alone and present it as licensing value

- **How it would work:** Use theatrical revenue as the ranking metric and assume higher-revenue candidates justify higher licensing prices.
- **Why it is attractive:** Revenue is a clear, comparable financial measure available in the dataset.
- **Why rejected:** Historical theatrical revenue is not streaming revenue, profit, or a measure of the rights currently available. It cannot independently establish an appropriate licensing price.

### Alternative C: Use revenue for ranking and other metrics as supporting evidence

- **How it would work:** Rank collections by summed theatrical revenue and individual standalone proxies by theatrical revenue, then report audience ratings, vote counts, and other available signals separately.
- **Why it is attractive:** Provides a consistent and explainable shortlist while preserving important context and limitations.
- **Why rejected:** Not rejected. This is the selected approach.

## What the recommendation would look like under the alternatives

- **If audience ratings alone set the priority:** Standalone candidates would lead on median rating in both windows (8.444 versus 7.601 across all years; 8.206 versus 7.450 since 2000). That would shift the screening priority to standalone titles, but ratings do not measure commercial performance, licensing value, or streaming demand.
- **If theatrical revenue were treated as licensing value:** The same revenue leaders would top the list, but Kwame might pay a premium without evidence that the rights or expected StreamVault value justify it. No price recommendation can be calculated from these data.
- **Selected approach:** Use revenue to screen candidates, ratings and votes as context, and actual quotes plus a separate streaming-value estimate to make a purchase decision.

## Talent-summary rule

Include only directors and first-listed cast members with at least two movie credits in this candidate set. Two credits allow a small within-list comparison and avoid presenting a single-film result as a pattern, but this threshold does not make a person a reliable predictor. If the threshold is wrong, one-credit talent will be omitted and people with two overlapping franchise credits may appear more dependable than they are. The summaries remain descriptive; validating prediction would require a larger independent film sample and streaming outcomes.

## Consequences

- **What this buys:** A transparent, reproducible ranking method that can be explained to the client and rerun for future candidate lists.
- **What this costs:** The ranking may not reflect streaming demand, current market value, licensing terms, or profitability. Collection totals also depend on the movies represented in the candidate data.
- **What it costs the client if I am wrong:** The client could overvalue a candidate or overlook a better licensing opportunity if theatrical history is a poor indicator of future platform value.
- **What would make me revisit this:** Reliable streaming audience data, licensing quotes, rights availability, territory-specific demand, comparable deal terms, or a client-approved alternative ranking objective.

## What this survives

The ranking can be rerun as the candidate list grows, provided the metric definitions remain consistent. Any change in the primary ranking objective should be documented as a new or superseding decision.
