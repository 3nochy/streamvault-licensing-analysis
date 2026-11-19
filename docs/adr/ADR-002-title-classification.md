# ADR-002: Use TMDb collection membership to classify franchise candidates

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owner:** Data Engineering

## Context

The client needs a comparison between franchise bundles and standalone titles. The available TMDb movie details include collection membership, but this metadata does not establish the actual licensing terms or whether a title can legally be licensed individually. The analysis must use a consistent, reproducible classification without claiming more than the data supports.

## Decision

Classify a movie as a franchise candidate when TMDb identifies it as belonging to a collection, and classify a movie without collection membership as a standalone proxy. Document that these are analytical categories, not confirmation of actual licensing availability.

## Alternatives considered

### Alternative A: Treat every movie without collection membership as a confirmed standalone title

- **How it would work:** Classify movies without a TMDb collection as individually licensable standalone titles.
- **Why it is attractive:** Produces a simple comparison between two apparently distinct licensing options.
- **Why rejected:** Collection metadata does not establish contractual rights or licensing availability. This would overstate what the source data proves.

### Alternative B: Exclude movies without collection membership

- **How it would work:** Analyze franchise collections only and leave movies without collection membership out of the comparison.
- **Why it is attractive:** Avoids making assumptions about standalone licensing.
- **Why rejected:** The client explicitly requires a comparison between franchise bundles and standalone candidates. Excluding these movies would prevent that comparison.

### Alternative C: Use collection membership as a proxy and state the limitation

- **How it would work:** Use TMDb collection membership to identify franchise candidates and label movies without collection membership as standalone proxies.
- **Why it is attractive:** Enables a consistent comparison while making the classification limitation transparent.
- **Why rejected:** Not rejected. This is the selected approach.

## Consequences

- **What this buys:** A reproducible classification that supports comparisons across all years and from 2000 onward.
- **What this costs:** The standalone group may contain movies that are not actually available for individual licensing, and franchise metadata may not reflect the precise package being offered.
- **What it costs the client if I am wrong:** The comparison could misrepresent the available licensing options and lead to an unsuitable shortlist or negotiation strategy.
- **What would make me revisit this:** Verified licensing catalogues, distributor information, or contractual evidence showing which titles are available individually or as bundles.

## What this survives

The classification rule can be applied consistently when the candidate list grows, provided the same TMDb metadata is available and the limitation is retained in reporting.
