# Research Methodology

## 1. Research Objective

This project examines short-term stock-price responses surrounding the initial public offering (IPO) of ChangXin Memory Technologies (CXMT) and compares performance across selected semiconductor-ecosystem participants.

The analysis does not attempt to attribute every observed price movement to the CXMT IPO. Instead, it uses an event-aligned normalized return framework to compare how selected securities performed within a predefined observation window and whether different industry roles were associated with visibly different short-term market responses.

## 2. Research Questions

The study addresses three main questions:

1. How did selected semiconductor-ecosystem companies perform during the observation window surrounding the CXMT IPO?
2. How did post-IPO price movements differ among CXMT and selected global memory peers when all firms are measured from the same event-date baseline?
3. How did CXMT's own closing price develop after listing, and what descriptive information is provided by a 7-trading-day moving average?

## 3. Research Contribution

The project provides a transparent and reproducible quantitative workflow that links:

- documented public market-data interfaces;
- Python-based data retrieval and cleaning;
- explicit figure-specific normalization rules;
- exchange-specific trading-date preservation;
- reproducible chart generation; and
- clearly stated interpretation boundaries.

The framework is descriptive. It does not estimate causal effects, expected returns, abnormal returns, or conventional cumulative abnormal return (CAR).

## 4. Event-Aligned Research Design

### 4.1 Focal event

The focal event is the first trading day of CXMT:

- Event date: **2026-07-27**
- Event notation: **t = 0**

The IPO date is used as an alignment point for the memory-sector comparison. It should not be interpreted as proof that all contemporaneous market movements were caused by the listing.

### 4.2 Research window

The predefined research window is:

- Start date: **2026-06-08**
- End date: **2026-08-07**

The final dataset is frozen through the August 7, 2026 market close. Only actually observed data inside the predefined window are included, and the workflow does not generate future observations.

### 4.3 Figure-specific baseline rules

The project uses different baselines because the three figures answer different analytical questions.

**Figure 1 — Semiconductor Ecosystem Normalized Return Comparison**

Coverage:

- AMEC
- NVIDIA
- Apple

Each security is normalized to its **first valid closing price on or after 2026-06-08** within the predefined research window.

**Figure 2 — Event-Aligned Memory Sector Performance Comparison**

Coverage:

- CXMT
- Micron
- Samsung Electronics
- SK hynix

All four securities use **2026-07-27** as one common baseline, so:

`NCR = 0%` on the event date for all four series.

**Figure 3 — CXMT Post-IPO Closing Price and MA7**

Figure 3 reports CXMT closing prices directly and therefore does not use NCR.

## 5. Sample Selection

The sample is intentionally small and heterogeneous. It is designed to represent different semiconductor-ecosystem roles rather than to provide a statistically exhaustive industry sample.

| Company | Ticker | Analytical Role |
|---|---|---|
| CXMT | 688825.SH | Focal IPO company; memory semiconductor |
| AMEC | 688012.SH | Upstream semiconductor equipment |
| SK hynix | 000660.KS | Global memory peer |
| Samsung Electronics | 005930.KS | Global memory peer |
| Micron Technology | MU | Global memory peer |
| NVIDIA | NVDA | Semiconductor design / AI ecosystem |
| Apple | AAPL | Downstream electronics demand |

## 6. Semiconductor Ecosystem Framework

The coverage set is classified by analytical role rather than treated as a single group of semiconductor manufacturers.

- **Upstream equipment:** AMEC
- **Memory semiconductor / focal issuer:** CXMT
- **Global memory peers:** SK hynix, Samsung Electronics, Micron
- **Semiconductor design / AI ecosystem:** NVIDIA
- **Downstream electronics demand:** Apple

This classification is used to organize Figure 1 and Figure 2 without implying a deterministic supply-chain transmission mechanism.

## 7. Data Sources and Processing Workflow

### 7.1 Source mapping

The Python workflow uses the following market-data interfaces:

- **A-shares:** Tencent Finance
- **U.S. equities:** Sina Finance as the primary source, with Yahoo Finance as fallback
- **Korean equities:** Naver Stock

### 7.2 Processing sequence

The workflow follows this sequence:

1. Retrieve market data.
2. Validate and clean returned records.
3. Restrict observations to the predefined research window.
4. Preserve each market's actual trading dates.
5. Apply the figure-specific baseline rule.
6. Calculate NCR where required.
7. Calculate MA7 for CXMT when enough valid observations exist.
8. Generate the three research figures.
9. Save real observations to local CSV files for reproducibility and endpoint fallback.

### 7.3 Calendar handling

The analysis does not force all markets onto one synthetic common calendar.

Different exchanges may have different holidays, trading sessions, and data-release timing. Each series therefore retains its actual observed trading dates.

## 8. Performance Measurement

### 8.1 Normalized Cumulative Return (NCR)

NCR is used as a descriptive measure of price performance relative to a defined baseline.

\[
NCR_{i,t} = \left(\frac{P_{i,t}}{P_{i,0}} - 1\right) \times 100\%
\]

where:

- `P(i,t)` is the closing price of security `i` on date `t`;
- `P(i,0)` is the baseline closing price defined for the relevant figure.

NCR is **not** conventional cumulative abnormal return (CAR).

### 8.2 7-Trading-Day Moving Average (MA7)

The CXMT price chart uses a 7-trading-day moving average:

\[
MA7_t = \frac{1}{7}\sum_{k=0}^{6} P_{t-k}
\]

The locked Python implementation is:

```python
rolling(window=7, min_periods=7)
```

MA7 is calculated only after seven complete valid trading observations are available. It is used only for descriptive smoothing and is not treated as a predictive trading signal.

## 9. Data Reliability Principles

The project follows the following data-integrity rules:

- No artificial price generation.
- No future-data generation.
- No manual filling of unavailable market prices.
- No interpolation or synthetic smoothing of NCR series.
- Exchange-specific trading dates are preserved.
- Figure-specific baseline rules are explicit and reproducible.
- Daily closing prices are used unless a separate OHLC source is explicitly documented.
- Cached CSV fallback is allowed only for previously retrieved real observations.
- Data freshness is checked before U.S. source data are accepted when a fallback source is available.

## 10. Interpretation Boundaries and Research Limitations

The analysis is descriptive and has several limitations:

- The observation window is short.
- The sample is deliberately small and heterogeneous.
- Cross-market trading hours and market structures differ.
- Security prices reflect many simultaneous company-specific, industry, macroeconomic, and market-wide factors.
- The project does not estimate expected returns, market-model beta, abnormal returns, or CAR.
- Observed co-movements do not establish causal transmission from the CXMT IPO.
- MA7 is a smoothing indicator only and should not be interpreted as a buy or sell signal.

Interpretation should therefore use cautious language such as **observed**, **suggests**, **may reflect**, and **is consistent with**, rather than claims of institutional buying, technical support, causal transmission, or investment recommendations.

## 11. Final Synchronization Status

The August 7 refresh is complete. It updated only:

- date-dependent values;
- final NCR endpoints;
- final MA7 values;
- Figures 1–3; and
- the Final V4 report and frozen replication materials.

Method definitions, baseline rules, source mapping, calendar handling, and interpretation boundaries remained unchanged. The GitHub materials are prepared for final release and Zenodo archival; the DOI will be added after reservation and final archive verification.
