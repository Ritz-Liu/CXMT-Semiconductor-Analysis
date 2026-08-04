# CXMT Semiconductor Analysis

## Overview

This repository contains an independent quantitative research workflow examining stock-price responses surrounding the IPO of ChangXin Memory Technologies (CXMT, 688825.SH).

The project uses an **event-aligned normalized return framework** to compare selected companies across the semiconductor ecosystem. It is designed as a transparent and reproducible research note rather than a conventional abnormal-return event study.

**Current status:** Near-Final / Pre-Data-Freeze  
**Event date:** 2026-07-27  
**Research window:** 2026-06-08 to 2026-08-07

The final data refresh will be performed after the August 7 close. At that stage, only date-dependent values, chart endpoints, and the final archived report will be updated. The methodology is already locked.

---

## Research Scope

The project covers seven securities representing different analytical roles:

| Company | Ticker | Analytical Role |
|---|---|---|
| CXMT | 688825.SH | Focal IPO company; memory semiconductor |
| AMEC | 688012.SH | Upstream semiconductor equipment |
| SK hynix | 000660.KS | Global memory peer |
| Samsung Electronics | 005930.KS | Global memory peer |
| Micron Technology | MU | Global memory peer |
| NVIDIA | NVDA | Semiconductor design / AI ecosystem |
| Apple | AAPL | Downstream electronics demand |

The sample is intentionally heterogeneous. The companies are grouped by ecosystem role and should not all be interpreted as semiconductor manufacturers.

---

## Methodology

### Normalized Cumulative Return (NCR)

The main comparative metric is:

\[
NCR_{i,t}
=
\left(
\frac{P_{i,t}}{P_{i,0}} - 1
\right)
\times 100\%
\]

where:

- `P(i,t)` is the closing price of security `i` on date `t`;
- `P(i,0)` is the baseline closing price defined for the relevant figure.

NCR is a **descriptive normalized-price measure**.

It is **not**:

- abnormal return (AR);
- cumulative abnormal return (CAR); or
- a conventional market-model event-study estimate.

### Figure-Specific Baselines

**Figure 1 — Semiconductor Ecosystem Normalized Return Comparison**

Coverage:

- AMEC
- NVIDIA
- Apple

Baseline:

- each security's first valid closing price on or after **2026-06-08**

**Figure 2 — Event-Aligned Memory Sector Performance Comparison**

Coverage:

- CXMT
- Micron
- Samsung Electronics
- SK hynix

Baseline:

- common event date: **2026-07-27**
- all four series are set to **0% NCR** on the event date

**Figure 3 — CXMT Post-IPO Price Development**

Metric:

- CXMT daily closing price in RMB
- 7-Trading-Day Moving Average (MA7)

Figure 3 does not use NCR.

### 7-Trading-Day Moving Average

\[
MA7_t
=
\frac{1}{7}
\sum_{k=0}^{6} P_{t-k}
\]

Locked Python implementation:

```python
rolling(window=7, min_periods=7)
```

MA7 is calculated only after seven valid trading observations are available.

---

## Current Pre-Freeze Figures

The charts below are generated from currently available observations and are **not yet the final August 7 data-freeze versions**.

### Figure 1 — Semiconductor Ecosystem Normalized Return Comparison

![Figure 1](output/charts/upstream_downstream_chain.png)

### Figure 2 — Event-Aligned Memory Sector Performance Comparison

![Figure 2](output/charts/memory_sector_comparison.png)

### Figure 3 — CXMT Post-IPO Closing Price and MA7

![Figure 3](output/charts/cxmt_price_trend.png)

---

## Market Data Sources

| Market | Primary Source | Fallback |
|---|---|---|
| China A-share | Tencent Finance | Cached real CSV observations |
| United States | Sina Finance | Yahoo Finance, then cached real CSV observations |
| South Korea | Naver Stock | Cached real CSV observations |

The U.S. workflow checks data freshness before accepting the primary Sina series when a newer fallback series may be required.

Only real observed market data are used.

---

## Data Integrity Rules

The workflow follows these rules:

- no artificial price generation;
- no future-data generation;
- no forward filling or backward filling;
- no manual insertion of unavailable prices;
- no interpolation of missing price paths;
- preserve actual exchange-specific trading dates;
- use daily closing prices unless a separate OHLC source is explicitly documented;
- allow cached CSV fallback only for previously retrieved real observations.

For Figure 2, observed trading dates may be displayed as equally spaced categories for readability. This affects presentation only and does not create synthetic observations.

---

## Project Structure

```text
CXMT-Semiconductor-Analysis/
│
├── data/
│   └── cached market-data CSV files
│
├── src/
│   └── generate_report_charts.py
│
├── output/
│   └── charts/
│       ├── upstream_downstream_chain.png
│       ├── memory_sector_comparison.png
│       └── cxmt_price_trend.png
│
├── methodology/
│   ├── research_methodology.md
│   ├── mathematical_models.md
│   └── variables_definition.md
│
├── references/
│   ├── academic_references.md
│   ├── data_sources.md
│   └── industry_reports.md
│
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

The final archived research report will be added after the data freeze.

---

## Reproducibility

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Run the chart-generation workflow from the repository root:

```bash
python src/generate_report_charts.py
```

The script:

1. retrieves available market data;
2. validates and cleans observations;
3. preserves actual exchange trading dates;
4. applies the locked figure-specific baseline rules;
5. calculates NCR and MA7 where required;
6. saves market-data CSV files to `data/`;
7. exports charts to `output/charts/`.

---

## Research Limitations

This project is descriptive.

It does not:

- estimate expected returns;
- estimate market-model alpha or beta;
- calculate AR or CAR;
- establish that the CXMT IPO caused observed price movements;
- infer institutional buying from price data alone;
- provide technical trading signals; or
- provide investment recommendations.

Observed differences may reflect company-specific information, semiconductor-industry conditions, broader market sentiment, macroeconomic factors, and cross-market trading differences.

---

## Research Status

### Locked Before Final Data Freeze

- research identity;
- event date;
- research window;
- NCR definition;
- Figure 1 baseline;
- Figure 2 common IPO baseline;
- Figure 3 metric;
- MA7 definition;
- source mapping;
- calendar handling;
- data-integrity rules;
- interpretation boundaries.

### Final Refresh After August 7 Close

The final refresh will update only:

- date-dependent values;
- final NCR endpoints;
- final MA7 values;
- Figures 1–3;
- final research report;
- final GitHub release; and
- Zenodo archival information.

Zenodo archival and DOI assignment will follow the final research freeze. The DOI will be added to the repository after the archived version is created.

---

## Documentation

Detailed methodology and source documentation are available in:

- [`methodology/research_methodology.md`](methodology/research_methodology.md)
- [`methodology/mathematical_models.md`](methodology/mathematical_models.md)
- [`methodology/variables_definition.md`](methodology/variables_definition.md)
- [`references/data_sources.md`](references/data_sources.md)
- [`references/industry_reports.md`](references/industry_reports.md)
- [`references/academic_references.md`](references/academic_references.md)

---

## License

This repository is released under the terms specified in the [`LICENSE`](LICENSE) file.
