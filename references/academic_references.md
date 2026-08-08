# Academic References

## 1. Event-Study Methodology

MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature, 35*(1), 13–39.

### Relevance to This Project

MacKinlay (1997) is included as the core methodological reference for conventional event-study research.

The CXMT project does **not** implement the full conventional event-study framework described in that literature.

Specifically, this project does not estimate:

- expected returns;
- a market model;
- alpha or beta;
- abnormal return (AR); or
- cumulative abnormal return (CAR).

Instead, the project uses an event-aligned normalized return framework based on observed closing prices.

## 2. Methodological Boundary

The primary descriptive metric used in this repository is Normalized Cumulative Return (NCR):

\[
NCR_{i,t}
=
\left(
\frac{P_{i,t}}{P_{i,0}} - 1
\right)
\times 100\%
\]

NCR should not be described as CAR.

The academic event-study reference is therefore used to distinguish this repository's descriptive normalized-return framework from a conventional abnormal-return event study.

## 3. Supporting Non-Academic References

Industry reports, company disclosures, and investor-relations materials are documented separately in:

- `references/industry_reports.md`

Market-price interfaces and data-processing rules are documented separately in:

- `references/data_sources.md`

Keeping these categories separate avoids presenting industry reports or market-data interfaces as peer-reviewed academic research.

## 4. Final Reference Scope

The Final V4 research note directly identifies MacKinlay (1997) as its academic methodological reference.

No additional peer-reviewed references are listed because they were not incorporated into the frozen research note.

This prevents the repository from presenting unused sources as part of the study's academic foundation. Any later expansion of the literature review should be released as a new research version.
