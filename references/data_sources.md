# Market Data Sources

## 1. Purpose

This file documents the market-data sources and data-handling rules used by the CXMT IPO research workflow.

The repository follows the same source mapping and integrity rules as the Final V4 research note and the frozen Python chart-generation workflow.

## 2. Equity Price Data

### 2.1 China A-share market

Covered securities:

- CXMT (688825.SH)
- AMEC (688012.SH)

Primary market-data source:

- Tencent Finance API / public market-data interface

Exchange context:

- Shanghai Stock Exchange

Data type:

- Daily closing prices

Usage:

- CXMT: Figure 2 and Figure 3
- AMEC: Figure 1

### 2.2 United States market

Covered securities:

- Apple (AAPL)
- NVIDIA (NVDA)
- Micron Technology (MU)

Primary market-data source:

- Sina Finance

Fallback source:

- Yahoo Finance

Exchange context:

- NASDAQ-listed securities in the current sample

Data type:

- Daily closing prices

Usage:

- Apple: Figure 1
- NVIDIA: Figure 1
- Micron: Figure 2

The Python workflow checks whether the primary U.S. series is sufficiently current before accepting it. If the Sina series is stale relative to the available observation window, Yahoo Finance may be used as the fallback source.

### 2.3 South Korea market

Covered securities:

- SK hynix (000660.KS)
- Samsung Electronics (005930.KS)

Primary market-data source:

- Naver Stock API / public market-data interface

Exchange context:

- Korea Exchange (KRX)

Data type:

- Daily closing prices

Usage:

- SK hynix: Figure 2
- Samsung Electronics: Figure 2

## 3. Research Window

The predefined research window is:

- Start date: **2026-06-08**
- End date: **2026-08-07**

The final dataset is frozen through the August 7, 2026 market close. Only observations inside the predefined window are used, and no future observations are generated.

## 4. Figure-Specific Data Usage

### Figure 1 — Semiconductor Ecosystem Normalized Return Comparison

Coverage:

- AMEC
- NVIDIA
- Apple

Baseline rule:

Each security is normalized to its first valid closing price on or after **2026-06-08** within the predefined research window.

Metric:

- Normalized Cumulative Return (NCR)

### Figure 2 — Event-Aligned Memory Sector Performance Comparison

Coverage:

- CXMT
- Micron
- Samsung Electronics
- SK hynix

Baseline rule:

All four securities use **2026-07-27**, the CXMT listing date, as one common baseline.

At the event date:

- `NCR = 0%` for all four series

Metric:

- Normalized Cumulative Return (NCR)

### Figure 3 — CXMT Post-IPO Closing Price and MA7

Coverage:

- CXMT

Metrics:

- Daily closing price in RMB
- 7-Trading-Day Moving Average (MA7)

Figure 3 does not use NCR.

## 5. Data Processing Pipeline

The Python workflow follows this sequence:

1. Retrieve market data from the documented public interfaces.
2. Validate and clean returned observations.
3. Normalize date values.
4. Restrict the series to the predefined research window.
5. Preserve exchange-specific trading dates.
6. Apply figure-specific baseline rules.
7. Calculate NCR or MA7 as required.
8. Generate research figures.
9. Save real retrieved observations to the documented CSV files for reproducibility and eligible endpoint fallback.

## 6. Trading Calendar Handling

Different exchanges do not share identical trading calendars.

The workflow therefore:

- preserves each market's actual trading dates;
- does not create a synthetic common daily calendar;
- does not treat exchange holidays as missing prices;
- does not force every security to have an observation on every displayed date.

For Figure 2 presentation, the chart may display the union of actual observed trading dates as equally spaced categories. This is a presentation choice only and does not create synthetic observations.

## 7. Missing-Data and Cache Policy

The project follows a strict real-data policy.

Allowed:

- previously retrieved real observations stored in local CSV files;
- cached CSV fallback when a public endpoint is temporarily unavailable;
- Yahoo Finance fallback for U.S. data when the primary Sina series is unavailable or insufficiently current.

Not allowed:

- artificial price generation;
- future-data generation;
- forward filling;
- backward filling;
- manual insertion of unavailable prices;
- interpolation of missing price paths;
- fabricated cross-market synchronization.

## 8. Data Reliability Principles

The workflow is designed around the following rules:

- Use actual observed market data only.
- Use daily closing prices unless a separate OHLC source is explicitly documented.
- Preserve source-specific and exchange-specific trading dates.
- Keep figure-specific baselines explicit and reproducible.
- Check U.S. source freshness when a fallback source is available.
- Do not interpret missing observations as zero returns.
- Do not infer intraday behavior from closing-price-only data.

## 9. Metric Definitions

### Normalized Cumulative Return (NCR)

\[
NCR_{i,t}
=
\left(
\frac{P_{i,t}}{P_{i,0}} - 1
\right)
\times 100\%
\]

NCR is a descriptive normalized-price measure.

It is not:

- abnormal return (AR); or
- conventional cumulative abnormal return (CAR).

### 7-Trading-Day Moving Average (MA7)

\[
MA7_t
=
\frac{1}{7}
\sum_{k=0}^{6} P_{t-k}
\]

Locked implementation:

```python
rolling(window=7, min_periods=7)
```

MA7 is calculated only after seven complete valid trading observations are available.

## 10. Final Freeze Status

The August 7 data refresh is complete. The following items remain locked in Final V4:

- source mapping;
- research window;
- Figure 1 baseline;
- Figure 2 common event baseline;
- Figure 3 metric definition;
- NCR formula;
- MA7 rule;
- exchange-calendar handling; and
- data-integrity policy.

The seven frozen data files are:

- `data/AMEC_688012_SH.csv`
- `data/APPLE_AAPL_US.csv`
- `data/CXMT_688825_SH.csv`
- `data/MICRON_MU_US.csv`
- `data/NVIDIA_NVDA_US.csv`
- `data/SAMSUNG_005930_KS.csv`
- `data/SK_HYNIX_000660_KS.csv`

The frozen files contain no observations after 2026-08-07. Subsequent market data are outside the scope of Final V4 and must not be appended to this archived research version.
