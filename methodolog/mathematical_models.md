# Mathematical Models

## 1. Normalized Cumulative Return (NCR)

### Purpose

Normalized Cumulative Return (NCR) measures the percentage change in a security's closing price relative to a clearly defined baseline.

It is used to make price paths comparable across securities with different absolute price levels.

### Formula

\[
NCR_{i,t} = \left(\frac{P_{i,t}}{P_{i,0}} - 1\right) \times 100\%
\]

### Variables

- `NCR(i,t)`: normalized cumulative return of security `i` on date `t`
- `P(i,t)`: closing price of security `i` on date `t`
- `P(i,0)`: baseline closing price for security `i`

### Interpretation

- `NCR = 0%` means the closing price equals the selected baseline price.
- `NCR > 0%` means the security is above its baseline price.
- `NCR < 0%` means the security is below its baseline price.

NCR is a descriptive normalized-price measure. It is **not** abnormal return and is **not** conventional cumulative abnormal return (CAR).

## 2. Figure-Specific Baseline Framework

The project uses figure-specific baselines because the figures answer different analytical questions.

### 2.1 Figure 1 baseline

Figure 1 covers:

- AMEC
- NVIDIA
- Apple

For each security, the baseline is the **first valid closing price on or after 2026-06-08** within the research window.

For security `i`:

\[
P_{i,0}^{(F1)} = P_{i,t_i^*}
\]

where `t_i*` is the first valid trading observation on or after 2026-06-08.

The Figure 1 NCR is:

\[
NCR_{i,t}^{(F1)} =
\left(
\frac{P_{i,t}}{P_{i,0}^{(F1)}} - 1
\right)
\times 100\%
\]

### 2.2 Figure 2 common event baseline

Figure 2 covers:

- CXMT
- Micron
- Samsung Electronics
- SK hynix

All four securities use the common event date:

\[
t_0 = \text{2026-07-27}
\]

The event-date closing price is the baseline:

\[
P_{i,0}^{(F2)} = P_{i,t_0}
\]

Therefore:

\[
NCR_{i,t_0}^{(F2)} = 0\%
\]

for all four securities.

The Figure 2 NCR is:

\[
NCR_{i,t}^{(F2)} =
\left(
\frac{P_{i,t}}{P_{i,t_0}} - 1
\right)
\times 100\%
\]

This common event baseline allows post-IPO directional movements to be compared directly.

### 2.3 Figure 3

Figure 3 reports CXMT daily closing prices directly.

It does **not** use NCR.

## 3. Event-Aligned Research Framework

### Event definition

The focal event is the CXMT listing date:

\[
t_0 = \text{2026-07-27}
\]

### Research window

The predefined calendar window is:

\[
\text{2026-06-08} \leq t \leq \text{2026-08-07}
\]

Only actually observed trading data are included.

### Purpose

The event date provides a common reference point for the memory-sector comparison. The framework is descriptive and does not imply that the IPO caused all observed price movements.

## 4. Seven-Trading-Day Moving Average (MA7)

### Purpose

MA7 smooths short-run variation in CXMT's daily closing-price series for descriptive visualization.

### Formula

\[
MA7_t = \frac{1}{7}\sum_{k=0}^{6} P_{t-k}
\]

where `P(t-k)` is the CXMT closing price at each of the seven most recent valid trading observations.

### Locked implementation

```python
rolling(window=7, min_periods=7).mean()
```

### Interpretation

The first valid MA7 value appears only after seven complete trading observations are available.

MA7 is not calculated from calendar days, and it is not a predictive trading signal.

### Limitation

Because CXMT has a short post-listing history in the research window, the MA7 series is initially short. No partial-period MA7 values are used.

## 5. Cross-Market Data Alignment Framework

### Workflow

For each security:

1. Retrieve observed market data.
2. Normalize date values.
3. Restrict the series to the research window.
4. Preserve actual exchange trading dates.
5. Apply the relevant figure baseline.
6. Calculate NCR or MA7.
7. Plot only available observations.

### Data handling principles

- No forward filling.
- No backward filling.
- No manual price insertion.
- No interpolation.
- No fabricated future data.
- No forced synthetic common trading-day calendar.

For Figure 2 presentation, the x-axis may display the union of actual observed trading dates as equally spaced categories. This changes only the visual spacing and does not create or modify observations.

## 6. Data Source Mapping

The locked source hierarchy is:

| Market | Primary Source | Fallback |
|---|---|---|
| China A-share | Tencent Finance | Cached real CSV observations if endpoint fails |
| United States | Sina Finance | Yahoo Finance, then cached real CSV observations if needed |
| South Korea | Naver Stock | Cached real CSV observations if endpoint fails |

U.S. source data are subject to a freshness check before they are accepted when a newer fallback series is required.

## 7. Model Boundaries and Assumptions

The analysis assumes only that closing prices can be used to describe observed market performance during the selected period.

The framework does **not** assume that:

- the CXMT IPO is the sole information event affecting prices;
- all securities respond to the IPO through one causal mechanism;
- normalized returns are abnormal returns;
- MA7 predicts future prices; or
- cross-market observations share identical trading calendars.

The project does not estimate:

- expected return;
- market-model alpha or beta;
- abnormal return (AR);
- cumulative abnormal return (CAR); or
- statistical event-study significance.

## 8. Final Model Status

The following items are fixed in Final V4:

- NCR definition;
- Figure 1 baseline rule;
- Figure 2 common IPO baseline;
- Figure 3 use of raw closing price;
- MA7 formula and `min_periods=7`;
- source hierarchy;
- actual-trading-date preservation; and
- prohibition on fabricated, filled, or interpolated price observations.

The August 7 refresh changed only date-dependent values and chart endpoints. These model definitions were not changed. Any later methodological change requires a new research version and must not be applied retroactively to the Final V4 archive.
