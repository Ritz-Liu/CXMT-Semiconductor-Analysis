import json
import os
import re
import xml.etree.ElementTree as ET

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# ===============================
# 1. Global Configuration
# ===============================
plt.rcParams["font.sans-serif"] = ["Calibri", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = "./data"
CHART_DIR = "./output/charts"

for d in [DATA_DIR, CHART_DIR]:
    os.makedirs(d, exist_ok=True)

def load_cached_csv(csv_path: str):
    """Load cached market data when API requests fail."""
    if not os.path.exists(csv_path):
        return None

    try:
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        if "Close" in df.columns:
            s = df["Close"]
        elif len(df.columns) == 1:
            # Backward compatibility with earlier single-series cache files.
            s = df.iloc[:, 0]
        else:
            return None

        s.index = pd.to_datetime(s.index).normalize()
        return pd.to_numeric(s, errors="coerce").dropna().sort_index()
    except Exception:
        return None

# ===============================
# 2. Locked Research Window
# ===============================
START_DATE = pd.Timestamp("2026-06-08")
END_DATE = pd.Timestamp("2026-08-07")
IPO_DATE = pd.Timestamp("2026-07-27")

# Cap every run at the research end date. Before that date, use only
# observations available at run time.
EFFECTIVE_END_DATE = min(END_DATE, pd.Timestamp.today().normalize())


# ===============================
# 3. CXMT IPO Data Handling
# ===============================
# CXMT data is loaded from the A-share market API.
# Only post-IPO trading dates are included in the analysis.

# ===============================
# 4. Market Data Acquisition
# ===============================
def _business_day_lag(last_date: pd.Timestamp, reference_date: pd.Timestamp) -> int:
    """Approximate weekday lag between the latest observation and the allowed end date."""
    last_date = pd.Timestamp(last_date).normalize()
    reference_date = pd.Timestamp(reference_date).normalize()
    if last_date >= reference_date:
        return 0
    return len(pd.bdate_range(last_date + pd.Timedelta(days=1), reference_date))


def _us_freshness_tolerance() -> int:
    """Set the allowable lag relative to the research end date."""
    today = pd.Timestamp.today().normalize()
    return 0 if today > END_DATE else 1


def fetch_us_stock_real(symbol: str) -> pd.Series:
    """Fetch US daily closes using Sina, switching to Yahoo when Sina is stale."""

    clean_symbol = symbol.replace(".US", "").strip().upper()
    stale_sina = None

    # 1. Primary source: Sina Finance API
    try:
        url = (
            "https://stock.finance.sina.com.cn/usstock/api/jsonp.php/"
            f"var%20us_{clean_symbol}=/US_MinKService.getDailyK?"
            f"symbol={clean_symbol}"
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        res = requests.get(url, headers=headers, timeout=8)

        if res.status_code == 200:
            match = re.search(r"\[.*\]", res.text)

            if match:
                data = json.loads(match.group(0))

                if len(data) >= 10:
                    df = pd.DataFrame(
                        [
                            {
                                "Date": item["d"],
                                "Close": float(item["c"])
                            }
                            for item in data
                        ]
                    )

                    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
                    df.set_index("Date", inplace=True)
                    s = df["Close"].dropna().sort_index()

                    if len(s) >= 20:
                        latest = s.index.max()
                        lag = _business_day_lag(latest, EFFECTIVE_END_DATE)
                        tolerance = _us_freshness_tolerance()
                        if lag <= tolerance:
                            print(
                                f"[SOURCE] {clean_symbol}: Sina Finance | "
                                f"latest={latest.date()} | freshness_lag={lag}"
                            )
                            return s

                        stale_sina = s
                        print(
                            f"[WARNING] {clean_symbol}: Sina Finance is stale "
                            f"(latest={latest.date()}, weekday_lag={lag}). "
                            "Trying Yahoo Finance fallback."
                        )

    except Exception as e:
        print(f"[WARNING] {clean_symbol}: Sina Finance request failed: {e}")

    # 2. Backup source: Yahoo Finance API
    try:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{clean_symbol}?interval=1d&range=2y"
        )
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        res = requests.get(url, headers=headers, timeout=20)

        if res.status_code == 200:
            result = res.json()["chart"]["result"][0]
            timestamps = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]

            df = pd.DataFrame(
                {
                    "Date": pd.to_datetime(timestamps, unit="s").normalize(),
                    "Close": closes,
                }
            )

            df.dropna(inplace=True)
            df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
            df.set_index("Date", inplace=True)
            s = df["Close"].dropna().sort_index()

            if len(s) >= 20:
                latest = s.index.max()
                print(
                    f"[SOURCE] {clean_symbol}: Yahoo Finance fallback | "
                    f"latest={latest.date()}"
                )

                # If Yahoo unexpectedly returns an older series than stale Sina,
                # use the fresher real series rather than silently regressing.
                if stale_sina is not None and latest < stale_sina.index.max():
                    print(
                        f"[WARNING] {clean_symbol}: Yahoo fallback is older than "
                        "the Sina response; using the fresher Sina observations."
                    )
                    return stale_sina

                return s

    except Exception as e:
        print(f"[WARNING] {clean_symbol}: Yahoo Finance request failed: {e}")

    if stale_sina is not None:
        raise RuntimeError(
            f"US data for [{symbol}] is stale through {stale_sina.index.max().date()} "
            "and Yahoo Finance fallback was unavailable."
        )

    raise RuntimeError(
        f"Unable to fetch sufficient historical data for [{symbol}]."
    )


def fetch_tencent_ashare(code: str, min_length: int = 40) -> pd.Series:
    """Fetch A-share daily price data using Tencent Finance API."""
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,,,100,qfq"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    res = requests.get(url, headers=headers, timeout=20)
    if res.status_code != 200:
        raise RuntimeError(f"A-share [{code}] request failed")

    data = res.json().get("data", {}).get(code, {})
    klines = data.get("qfqday") or data.get("day", [])
    if not klines or len(klines) < min_length:
        raise ValueError(f"A-share [{code}] returned insufficient data")

    df = pd.DataFrame(
        [{"Date": item[0], "Close": float(item[2])} for item in klines]
    )
    df["Date"] = pd.to_datetime(df["Date"]).dt.normalize()
    df.set_index("Date", inplace=True)
    return df["Close"].dropna()


def fetch_naver_korea(code: str) -> pd.Series:
    """Fetch Korean stock daily price data using Naver Stock API."""
    url = (
        "https://fchart.stock.naver.com/sise.nhn?"
        f"symbol={code}&timeframe=day&count=100&requestType=0"
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    res = requests.get(url, headers=headers, timeout=20)
    if res.status_code != 200:
        raise RuntimeError(f"Korean stock [{code}] request failed")

    root = ET.fromstring(res.text)
    rows = []
    for item in root.findall(".//item"):
        parts = item.attrib.get("data", "").split("|")
        if len(parts) >= 6:
            rows.append({"Date": parts[0], "Close": float(parts[4])})
    if not rows or len(rows) < 40:
        raise ValueError(f"Korean stock [{code}] XML parsing returned insufficient data")

    df = pd.DataFrame(rows)
    df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d").dt.normalize()
    df.set_index("Date", inplace=True)
    return df["Close"].dropna()


# ================= 5. Data Loading and Alignment =================
def load_all_targets_data(targets: dict) -> dict:
    dfs = {}
    print(
        f"Starting market data acquisition | Window: "
        f"{START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}"
    )

    for code, (target_name, source_type) in targets.items():
        filename_map = {
            "sh688012": "AMEC_688012_SH.csv",
            "sh688825": "CXMT_688825_SH.csv",
            "000660": "SK_HYNIX_000660_KS.csv",
            "005930": "SAMSUNG_005930_KS.csv",
            "MU": "MICRON_MU_US.csv",
            "AAPL": "APPLE_AAPL_US.csv",
            "NVDA": "NVIDIA_NVDA_US.csv",
        }
        csv_name = filename_map.get(code, f"{code}.csv")
        csv_path = os.path.join(DATA_DIR, csv_name)

        # CXMT: retain only post-IPO trading data
        if "688825" in code:
            try:
                raw_s = fetch_tencent_ashare(code, min_length=1)
            except Exception as e:
                raw_s = load_cached_csv(csv_path)
                if raw_s is None:
                    raise RuntimeError(
                        f"CXMT data unavailable and no cached CSV found: {e}"
                    )
                print(
                    f"[WARNING] {target_name} API unavailable. "
                    "Loaded cached CSV data."
                )

            s = raw_s[
                (raw_s.index >= START_DATE)
                & (raw_s.index <= EFFECTIVE_END_DATE)
            ]
            s = s[s.index >= IPO_DATE].copy()

            dfs[target_name] = s
            pd.DataFrame({"Close": s.dropna()}).to_csv(csv_path)

            print(
                f"[{target_name}] Post-IPO market data loaded successfully."
            )
            continue

        # 1. Fetch market data from external APIs
        try:
            if source_type == "US":
                raw_s = fetch_us_stock_real(code)
            elif source_type == "A":
                raw_s = fetch_tencent_ashare(code)
            elif source_type == "KOREA":
                raw_s = fetch_naver_korea(code)
            else:
                raise ValueError(
                    f"Unsupported data source type: {source_type}"
                )

        except Exception as e:
            cached_data = load_cached_csv(csv_path)

            if cached_data is not None:
                raw_s = cached_data
                print(
                    f"[WARNING] {target_name} API unavailable. "
                    "Loaded cached CSV data."
                )
            else:
                print(
                    f"[ERROR] {target_name} data unavailable. "
                    f"No cached data found: {e}"
                )
                continue

        # 2. Align data with valid trading dates
        # Strict mode:
        # Keep only actual trading dates inside the research window.
        # Do not create artificial weekday dates.
        s = raw_s[
            (raw_s.index >= START_DATE)
            & (raw_s.index <= EFFECTIVE_END_DATE)
        ]

        # Preserve only observed exchange trading dates. No synthetic calendar,
        # forward fill, backward fill, or interpolation is applied.
        if s.index.has_duplicates:
            s = s[~s.index.duplicated(keep="last")].sort_index()

        dfs[target_name] = s
        pd.DataFrame({"Close": s}).to_csv(csv_path)
        print(
            f"[{target_name}] Market data loaded successfully | Records: {len(raw_s)}"
        )

    # Final safety check: prevent data beyond report end date
    for name, series in dfs.items():
        if not series.empty and series.index.max() > EFFECTIVE_END_DATE:
            raise ValueError(
                f"{name} contains data beyond allowed date {EFFECTIVE_END_DATE.date()}"
            )

    return dfs


# ===============================
# 6. Locked Analytical Definitions
# ===============================
def normalized_cumulative_return_from_first_valid(
    series: pd.Series, start_date: pd.Timestamp
) -> pd.Series:
    """
    Figure 1 rule: normalize to the first valid close on or after start_date.

    NCR_t = (P_t / P_0 - 1) * 100
    """
    s = series.dropna().sort_index()
    s = s[s.index >= start_date]
    if s.empty:
        return pd.Series(dtype=float, name=series.name)

    base_price = float(s.iloc[0])
    if base_price == 0:
        raise ValueError("Baseline price cannot be zero.")

    return ((s / base_price) - 1.0) * 100.0


def normalized_cumulative_return_from_event(
    series: pd.Series, event_date: pd.Timestamp
) -> pd.Series:
    """
    Figure 2 rule: use the exact CXMT IPO date as the common 0% baseline.

    No nearest-date substitution is permitted. If a security has no valid close
    on the event date, the comparison is not generated for that security.
    """
    s = series.dropna().sort_index()
    if event_date not in s.index:
        raise ValueError(
            f"Missing exact event-date close for {series.name or 'series'} on "
            f"{event_date.date()}."
        )

    base_price = float(s.loc[event_date])
    if base_price == 0:
        raise ValueError("Event-date baseline price cannot be zero.")

    post_event = s[s.index >= event_date]
    return ((post_event / base_price) - 1.0) * 100.0


def calculate_ma7(series: pd.Series) -> pd.Series:
    """Calculate the 7-trading-observation moving average (MA7)."""
    s = series.dropna().sort_index()
    return s.rolling(window=7, min_periods=7).mean()


# ===============================
# 7. Main Program: Chart Export
# ===============================
if __name__ == "__main__":
    targets = {
        "sh688012": ("AMEC (688012.SH)", "A"),
        "000660": ("SK Hynix (000660.KS)", "KOREA"),
        "005930": ("Samsung Electronics (005930.KS)", "KOREA"),
        "MU": ("Micron (MU.US)", "US"),
        "AAPL": ("Apple (AAPL.US)", "US"),
        "NVDA": ("NVIDIA (NVDA.US)", "US"),
        "sh688825": ("CXMT (688825.SH - Target)", "A"),
    }

    dfs = load_all_targets_data(targets)

    # Fail fast rather than silently generating partial research figures.
    required_names = [target_name for target_name, _ in targets.values()]
    missing_required = [
        name for name in required_names
        if name not in dfs or dfs[name].dropna().empty
    ]
    if missing_required:
        raise RuntimeError(
            "Required market series unavailable or empty: "
            + ", ".join(missing_required)
        )

    print("\n================ NCR Calculation (%) ================")
    print(
        "Figure 1 baseline: first valid close on/after 2026-06-08 | "
        "Figure 2 baseline: 2026-07-27 = 0%"
    )

    # ------------------------------------------------------------------
    # FIGURE 1: Semiconductor Ecosystem Normalized Return Comparison
    # Baseline: each security's first valid close on/after 2026-06-08.
    # ------------------------------------------------------------------
    figure1_map = {
        "AMEC (688012.SH)": {"color": "#1f77b4", "style": "-", "w": 2.2},
        "Apple (AAPL.US)": {"color": "#d62728", "style": "-", "w": 2.0},
        "NVIDIA (NVDA.US)": {"color": "#2ca02c", "style": "-", "w": 2.0},
    }

    # Preserve the original wide research-chart geometry. The report may scale
    # this image proportionally, but must not alter its aspect ratio.
    plt.figure(figsize=(10, 3.8), dpi=300)
    for name, cfg in figure1_map.items():
        if name not in dfs:
            continue
        ncr = normalized_cumulative_return_from_first_valid(dfs[name], START_DATE)
        if ncr.empty:
            continue
        plt.plot(
            ncr.index,
            ncr.values,
            label=name,
            color=cfg["color"],
            linestyle=cfg["style"],
            linewidth=cfg["w"],
        )

    plt.axvline(
        IPO_DATE,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label="CXMT IPO Date (07-27)",
    )
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xlabel("Trading Date (2026)", fontsize=9.5)
    plt.ylabel("Normalized Cumulative Return (%)", fontsize=9.5)
    plt.axhline(0, color="gray", linestyle=":", linewidth=1)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left", fontsize=9, frameon=True)
    plt.tight_layout()
    chart1_path = os.path.join(CHART_DIR, "upstream_downstream_chain.png")
    plt.savefig(chart1_path)
    plt.close()

    # ------------------------------------------------------------------
    # FIGURE 2: Event-Aligned Memory Sector Performance Comparison
    # Common baseline: exact close on 2026-07-27 = 0% for all four names.
    # Only post-event observations are plotted.
    # ------------------------------------------------------------------
    figure2_map = {
        "SK Hynix (000660.KS)": {"color": "#9467bd", "style": "--", "w": 2.2},
        "Samsung Electronics (005930.KS)": {"color": "#8c564b", "style": "-.", "w": 2.0},
        "Micron (MU.US)": {"color": "#ff7f0e", "style": "-", "w": 2.0},
        "CXMT (688825.SH - Target)": {"color": "#d62728", "style": "-", "w": 2.8},
    }

    # Presentation rule: keep the real daily observations, but display only
    # observed market dates on an equal-spaced categorical x-axis.
    # No interpolation or smoothing is applied to Figure 2.
    figure2_ncr = {}
    observed_dates = set()
    for name in figure2_map:
        if name not in dfs:
            raise RuntimeError(f"Figure 2 required series is unavailable: {name}")
        event_ncr = normalized_cumulative_return_from_event(dfs[name], IPO_DATE)
        figure2_ncr[name] = event_ncr
        observed_dates.update(event_ncr.index.tolist())

    observed_dates = sorted(observed_dates)
    date_to_x = {date: pos for pos, date in enumerate(observed_dates)}

    plt.figure(figsize=(10, 3.8), dpi=300)
    for name, cfg in figure2_map.items():
        event_ncr = figure2_ncr[name]
        x_values = [date_to_x[date] for date in event_ncr.index]
        plt.plot(
            x_values,
            event_ncr.values,
            label=name,
            color=cfg["color"],
            linestyle=cfg["style"],
            linewidth=cfg["w"],
            marker="o",
            markersize=5.5 if name.startswith("CXMT") else 4.0,
        )

    baseline_x = date_to_x[IPO_DATE]
    plt.axvline(
        baseline_x,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label="Common Baseline: CXMT IPO (07-27)",
    )

    # Show only real observed dates; weekends/non-observed dates never appear.
    max_ticks = 10
    tick_step = max(1, int(np.ceil(len(observed_dates) / max_ticks)))
    tick_positions = list(range(0, len(observed_dates), tick_step))
    if tick_positions[-1] != len(observed_dates) - 1:
        tick_positions.append(len(observed_dates) - 1)
    tick_labels = [observed_dates[i].strftime("%m-%d") for i in tick_positions]
    plt.xticks(tick_positions, tick_labels)
    plt.xlabel("Observed Trading Date (2026)", fontsize=9.5)
    plt.ylabel("Normalized Cumulative Return (%)", fontsize=9.5)
    plt.axhline(0, color="gray", linestyle=":", linewidth=1)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="best", fontsize=8.5, frameon=True)
    plt.tight_layout()
    chart2_path = os.path.join(CHART_DIR, "memory_sector_comparison.png")
    plt.savefig(chart2_path)
    plt.close()

    # ------------------------------------------------------------------
    # FIGURE 3: CXMT Post-IPO Closing Price + full MA7
    # MA7 appears only after seven valid CXMT trading observations.
    # ------------------------------------------------------------------
    cx_name = "CXMT (688825.SH - Target)"
    if cx_name in dfs and not dfs[cx_name].dropna().empty:
        raw_cx = dfs[cx_name].dropna().sort_index()
        plot_cx = raw_cx[raw_cx.index >= IPO_DATE]
        cx_df = pd.DataFrame({"Close": plot_cx})
        cx_df["MA7"] = calculate_ma7(cx_df["Close"])

        plt.figure(figsize=(9, 3.5), dpi=300)
        date_labels = [d.strftime("%m-%d") for d in cx_df.index]

        plt.plot(
            date_labels,
            cx_df["Close"],
            marker="o",
            markersize=7,
            color="#2b5c8f",
            label="Daily Closing Price (RMB)",
            linewidth=2.2,
        )
        plt.plot(
            date_labels,
            cx_df["MA7"],
            color="#e06d53",
            linestyle="--",
            label="7-Trading-Day Moving Average (MA7)",
            linewidth=1.8,
        )

        latest_date_str = cx_df.index[-1].strftime("%Y-%m-%d")
        latest_val = float(cx_df["Close"].iloc[-1])

        plt.plot(
            date_labels[-1],
            latest_val,
            marker="o",
            markersize=8,
            color="#d9381e",
        )
        plt.annotate(
            f"Latest Close: {latest_val:.2f} RMB\n({latest_date_str})",
            xy=(date_labels[-1], latest_val),
            xytext=(-120, -35),
            textcoords="offset points",
            arrowprops=dict(
                arrowstyle="->",
                connectionstyle="arc3,rad=-.2",
                color="#d9381e",
                lw=1.3,
            ),
            fontweight="bold",
            color="#d9381e",
            fontsize=9,
            bbox=dict(
                boxstyle="round,pad=0.35",
                fc="#fffaf5",
                ec="#d9381e",
                lw=1.1,
            ),
        )

        plt.xlabel("Trading Date (2026)", fontsize=9.5)
        plt.ylabel("Stock Price (RMB)", fontsize=9.5)
        price_min = float(cx_df["Close"].min())
        price_max = float(cx_df["Close"].max())
        plt.ylim(price_min - 2.0, price_max + 2.0)
        plt.legend(loc="upper left", fontsize=8.8, frameon=True)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        chart3_path = os.path.join(CHART_DIR, "cxmt_price_trend.png")
        plt.savefig(chart3_path)
        plt.close()

        valid_ma7 = cx_df["MA7"].dropna()
        if valid_ma7.empty:
            print(
                "[INFO] CXMT has fewer than seven valid post-IPO trading "
                "observations; MA7 is not yet available."
            )
        else:
            print(
                f"[INFO] Latest MA7: {valid_ma7.iloc[-1]:.2f} RMB | "
                f"Date: {valid_ma7.index[-1].date()}"
            )

    print(
        f"\nAnalysis complete. Charts saved to {CHART_DIR}."
    )
