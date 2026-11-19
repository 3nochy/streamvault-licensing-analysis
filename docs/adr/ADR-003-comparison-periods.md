# ADR-003: Evaluate licensing candidates across all years and from 2000 onward

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owner:** Data Engineering

## Context

The client requires a comparison of franchise bundles and standalone candidates across all available release years and separately from 2000 onward. Finance has expressed concerns about historical box-office data because of inflation, currency differences, and historical reporting practices. The analysis must show whether the recommendation changes between these periods.

## Decision

Produce separate franchise-versus-standalone-proxy comparisons for all available release years and for titles released from 2000 onward. Report the results and any change in the preferred strategy explicitly, while identifying the limitations of using unadjusted historical theatrical revenue.

## Alternatives considered

### Alternative A: Use only all-years results

- **How it would work:** Include every available release year in a single comparison.
- **Why it is attractive:** Uses the largest available sample and provides a broad historical view.
- **Why rejected:** Does not address the client's concern about older box-office data or reveal whether the conclusion changes for more recent releases.

### Alternative B: Use only titles released from 2000 onward

- **How it would work:** Exclude pre-2000 releases from the analysis.
- **Why it is attractive:** Reduces reliance on older box-office records.
- **Why rejected:** Discards historical evidence and fails to meet the requirement for an all-years comparison.

### Alternative C: Report both periods separately

- **How it would work:** Calculate and compare the same key metrics for all years and for 2000 onward, and explicitly flag any reversal in the preferred strategy.
- **Why it is attractive:** Preserves the broad historical view while testing whether the conclusion holds in the more recent period.
- **Why rejected:** Not rejected. This is the selected approach.

## What the recommendation would look like under the alternatives

- **If only all years were reported:** Franchise candidates would still lead on median theatrical revenue ($578.9M versus $161.8M), but Kwame could not answer Finance's concern about older releases.
- **If only titles from 2000 onward were reported:** Franchise candidates would still lead ($786.6M versus $283.2M), but the analysis would omit the required full-history view and would rely on only eight standalone candidates.
- **Selected approach:** Keep the franchise negotiation priority in both periods and state that the evidence is historical revenue, not streaming value. The strategy does not reverse; the sample and revenue levels change.

## Consequences

- **What this buys:** The client can see whether the comparison is consistent across both periods and whether older titles materially affect the conclusion.
- **What this costs:** The recent-period sample is smaller, and neither period's raw theatrical revenue is adjusted for inflation or differences in historical reporting.
- **What it costs the client if I am wrong:** A misleading comparison could cause the client to favour a licensing strategy based on historical revenue patterns that do not hold for the relevant period.
- **What would make me revisit this:** Inflation-adjusted revenue, more complete historical financial data, a change in the client's preferred time period, or a material change in the candidate list.

## What this survives

The two-period comparison can be repeated for future candidate lists, allowing the client to monitor whether the relative performance of franchise candidates and standalone proxies changes over time.
