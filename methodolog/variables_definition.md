# Variables Definition

## 1. Financial Variables

| Variable | Definition | Unit |
|---|---|---|
| `P(i,t)` | Closing price of security `i` on observed trading date `t` | Local currency |
| `P(i,0)` | Baseline closing price used for the relevant figure | Local currency |
| `NCR(i,t)` | Normalized Cumulative Return of security `i` on date `t` | Percent (%) |
| `MA7(t)` | Seven-trading-day moving average of CXMT closing price | RMB |
| `Close` | Daily closing price returned by the market-data interface | Local currency |

### Normalized Cumulative Return

\[
NCR_{i,t} = \left(\frac{P_{i,t}}{P_{i,0}} - 1\right) \times 100\%
\]

NCR is a descriptive normalized-price measure. It is not abnormal return and is not conventional cumulative abnormal return (CAR).

### 7-Trading-Day Moving Average

\[
MA7_t = \frac{1}{7}\sum_{k=0}^{6}P_{t-k}
\]

The Python implementation is:

```python
rolling(window=7, min_periods=7)
```

The first MA7 value is produced only after seven valid trading observations exist.

## 2. Event and Time Variables

| Variable | Definition |
|---|---|
| `t0` | CXMT IPO / listing date: **2026-07-27** |
| `START_DATE` | Beginning of predefined research window: **2026-06-08** |
| `END_DATE` | End of predefined research window: **2026-08-07** |
| `t` | An actually observed trading date for a security |
| `t_i*` | First valid observed trading date for security `i` on or after 2026-06-08, used for Figure 1 baseline selection |

The analysis uses actual exchange trading dates. It does not create a synthetic common daily calendar.

## 3. Figure-Specific Baseline Variables

### Figure 1 baseline

Coverage:

- AMEC
- NVIDIA
- Apple

For each security:

`P(i,0)` = first valid closing price on or after **2026-06-08** within the research window.

Each Figure 1 series therefore begins at:

`NCR = 0%`

on its own first valid observation in the window.

### Figure 2 baseline

Coverage:

- CXMT
- Micron
- Samsung Electronics
- SK hynix

For every security:

`P(i,0)` = closing price on **2026-07-27**.

Therefore:

`NCR(i,t0) = 0%`

for all four securities on the common event date.

### Figure 3 metric

Figure 3 does not use NCR.

It reports:

- CXMT daily closing price in RMB; and
- 7-Trading-Day Moving Average (MA7).

## 4. Company Classification

| Company | Ticker | Market | Ecosystem Classification | Figure Coverage |
|---|---|---|---|---|
| CXMT | 688825.SH | China | Memory semiconductor; focal IPO company | Figure 2, Figure 3 |
| AMEC | 688012.SH | China | Upstream semiconductor equipment | Figure 1 |
| SK hynix | 000660.KS | South Korea | Memory semiconductor; global memory peer | Figure 2 |
| Samsung Electronics | 005930.KS | South Korea | Memory semiconductor; global memory peer | Figure 2 |
| Micron Technology | MU | United States | Memory semiconductor; global memory peer | Figure 2 |
| NVIDIA | NVDA | United States | Semiconductor design / AI ecosystem | Figure 1 |
| Apple | AAPL | United States | Downstream electronics demand | Figure 1 |

The companies are classified by analytical role. They should not all be described as semiconductor manufacturers.

## 5. Data Source Variables

| Market Group | Source Rule |
|---|---|
| China A-share | Tencent Finance |
| U.S. equities | Sina Finance primary; Yahoo Finance fallback |
| Korean equities | Naver Stock |
| Local cache | Previously retrieved real CSV observations only |

Cached data may be used for reproducibility or endpoint fallback. Artificial prices, future observations, and manual filling are not allowed.

## 6. Research Window and Observation Rules

The predefined research window is:

**2026-06-08 through 2026-08-07**

Observation rules:

- Include only real observed market data.
- Do not generate future prices.
- Do not forward-fill or backward-fill missing market prices.
- Do not interpolate price paths.
- Preserve exchange-specific trading dates.
- Use daily closing prices unless a separate OHLC source is explicitly documented.
- A security may have no observation on a date when its exchange is closed.
- Cross-market chart presentation must not be interpreted as evidence that all markets traded on identical dates.

## 7. Interpretation Variables and Boundaries

The project uses descriptive interpretation.

Preferred terms include:

- observed;
- suggests;
- may reflect;
- is consistent with;
- normalized price performance;
- post-event trajectory.

Avoid unsupported interpretations such as:

- institutional buying;
- technical support;
- golden cross;
- guaranteed cost pass-through;
- causal transmission;
- overweight;
- buy / sell recommendation.

## 8. Final Freeze Status

The following definitions are locked in Final V4:

- event date;
- research window;
- NCR formula;
- Figure 1 baseline;
- Figure 2 common baseline;
- Figure 3 metric;
- MA7 formula;
- source mapping;
- calendar handling; and
- data-integrity rules.

The August 7 refresh updated only date-dependent results and final chart values. The definitions above remained unchanged. Data after 2026-08-07 are outside the frozen research window and must not be added to the Final V4 dataset.
