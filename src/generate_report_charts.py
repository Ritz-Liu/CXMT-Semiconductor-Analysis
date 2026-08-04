import glob
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
            return df["Close"].dropna()
    except Exception:
        return None

    return None

# Remove previous cached data files
for f in glob.glob(os.path.join(DATA_DIR, "*.*")):
    if os.path.isfile(f):
        try:
            os.remove(f)
        except Exception:
            pass


# ===============================
# 2. Dynamic Trading Calendar
# ===============================
START_DATE = pd.Timestamp("2026-06-08")
END_DATE = pd.Timestamp("2026-08-07")

MASTER_DATES = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="B"
)


# ===============================
# 3. CXMT IPO Data Handling
# ===============================
# CXMT data is loaded from the A-share market API.
# Only post-IPO trading dates are included in the analysis.

# ===============================
# 4. Market Data Acquisition
# ===============================
def fetch_us_stock_real(symbol: str) -> pd.Series:
    """Fetch US daily stock prices using Sina Finance API with Yahoo Finance fallback."""

    clean_symbol = symbol.replace(".US", "").strip().upper()

    # 1. Primary source: Sina Finance API
    try:
        url = f"https://stock.finance.sina.com.cn/usstock/api/jsonp.php/var%20us_{clean_symbol}=/US_MinKService.getDailyK?symbol={clean_symbol}"

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

                    s = df["Close"].dropna()

                    if len(s) >= 20:
                        pass
                        return s

    except Exception:
        pass

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

            s = df["Close"].dropna()

            if len(s) >= 20:
                pass
                return s

    except Exception:
        pass

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
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count=100&requestType=0"
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
        f"Starting market data acquisition | Window: {START_DATE.strftime("%Y-%m-%d")} to {END_DATE.strftime("%Y-%m-%d")}"
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
                & (raw_s.index <= END_DATE)
            ]
            s[s.index < pd.Timestamp("2026-07-27")] = np.nan

            dfs[target_name] = s
            s.dropna().to_csv(csv_path)

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
            & (raw_s.index <= END_DATE)
        ]

        # Warn only for completed dates; future dates remain unavailable.
        run_date = pd.Timestamp.today().normalize()
        past_dates = MASTER_DATES[MASTER_DATES <= run_date]

        # Warn only for missing values in returned trading data.
        # Holidays are not treated as missing market data.
        observed_dates = raw_s.index.intersection(past_dates)
        if len(observed_dates) > 0:
            missing_past = raw_s.loc[observed_dates].isna().sum()
            if missing_past > 0:
                print(
                    f"[WARNING] {target_name}: {missing_past} missing values detected in returned market data."
                )

        dfs[target_name] = s
        pd.DataFrame({"Close": s}).to_csv(csv_path)
        print(
            f"[{target_name}] Market data loaded successfully | Records: {len(raw_s)}"
        )

    # Final safety check: prevent data beyond report end date
    for name, series in dfs.items():
        if series.index.max() > END_DATE:
            raise ValueError(
                f"{name} contains data beyond frozen date {END_DATE.date()}"
            )

    return dfs


# ===============================
# 6. Main Program: Chart Export
# ===============================
if __name__ == "__main__":
    targets = {
        "sh688012": ("AMEC (688012.SH)", "A"),
        "000660": ("SK Hynix (000660.KS)", "KOREA"),
        "005930": ("Samsung (005930.KS)", "KOREA"),
        "MU": ("Micron (MU.US)", "US"),
        "AAPL": ("Apple (AAPL.US)", "US"),
        "NVDA": ("NVIDIA (NVDA.US)", "US"),
        "sh688825": ("CXMT (688825.SH - Target)", "A"),
    }

    dfs = load_all_targets_data(targets)
    combined_df = pd.DataFrame(dfs)

    print("\n================ Relative Performance Calculation (%) ================")
    normalized_window = pd.DataFrame()
    for col in combined_df.columns:
        first_valid_idx = combined_df[col].first_valid_index()
        if first_valid_idx is not None:
            base_val = combined_df.loc[first_valid_idx, col]
            normalized_window[col] = (combined_df[col] / base_val - 1) * 100

    ipo_date = pd.to_datetime("2026-07-27")

    # --- FIGURE 1: Upstream and Downstream Transmission ---
    plt.figure(figsize=(10, 3.8), dpi=300)
    chain_map = {
        "AMEC (688012.SH)": {"color": "#1f77b4", "style": "-", "w": 2.2},
        "Apple (AAPL.US)": {"color": "#d62728", "style": "-", "w": 2.0},
        "NVIDIA (NVDA.US)": {"color": "#2ca02c", "style": "-", "w": 2.0},
    }
    for col, cfg in chain_map.items():
        if col in normalized_window:
            plot_s = normalized_window[col].dropna()
            if not plot_s.empty:
                plt.plot(
                    plot_s.index,
                    plot_s.values,
                    label=col,
                    color=cfg["color"],
                    linestyle=cfg["style"],
                    linewidth=cfg["w"],
                )

    plt.axvline(
        ipo_date,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label="CXMT IPO Date (07-27)",
    )
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xlabel("Trading Date (2026)", fontsize=9.5)
    plt.ylabel("Cumulative Relative Return (%)", fontsize=9.5)
    plt.axhline(0, color="gray", linestyle=":", linewidth=1)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left", fontsize=9, frameon=True)
    plt.tight_layout()
    chart1_path = os.path.join(
        CHART_DIR, "upstream_downstream_chain.png"
    )
    plt.savefig(chart1_path)
    plt.close()

    # --- FIGURE 2: Memory Sector Comparison ---
    plt.figure(figsize=(10, 3.8), dpi=300)
    midstream_map = {
        "SK Hynix (000660.KS)": {"color": "#9467bd", "style": "--", "w": 2.2},
        "Samsung (005930.KS)": {"color": "#8c564b", "style": "-.", "w": 2.0},
        "Micron (MU.US)": {"color": "#ff7f0e", "style": "-", "w": 2.0},
    }
    for col, cfg in midstream_map.items():
        if col in normalized_window:
            plot_s = normalized_window[col].dropna()
            if not plot_s.empty:
                plt.plot(
                    plot_s.index,
                    plot_s.values,
                    label=col,
                    color=cfg["color"],
                    linestyle=cfg["style"],
                    linewidth=cfg["w"],
                )

    cx_name = "CXMT (688825.SH - Target)"
    if cx_name in normalized_window:
        cx_s = normalized_window[cx_name].dropna()
        if not cx_s.empty:
            plt.plot(
                cx_s.index,
                cx_s,
                label=cx_name,
                color="#d62728",
                linewidth=2.8,
                marker="o",
                markersize=5.5,
            )

    plt.axvline(
        ipo_date,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label="CXMT IPO Date (07-27)",
    )
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    plt.xlabel("Trading Date (2026)", fontsize=9.5)
    plt.ylabel("Cumulative Relative Return (%)", fontsize=9.5)
    plt.axhline(0, color="gray", linestyle=":", linewidth=1)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper left", fontsize=8.8, frameon=True)
    plt.tight_layout()
    chart2_path = os.path.join(CHART_DIR, "memory_sector_comparison.png")
    plt.savefig(chart2_path)
    plt.close()

    # --- FIGURE 3: CXMT Price Trend ---
    if cx_name in dfs and not dfs[cx_name].dropna().empty:
        raw_cx = dfs[cx_name].dropna()
        cx_df = pd.DataFrame({"Close": raw_cx})
        cx_valid = cx_df["Close"].dropna()
        cx_df["MA7"] = np.nan
        cx_df.loc[cx_valid.index, "MA7"] = cx_valid.rolling(
            window=7, min_periods=1
        ).mean()
        plot_cx = cx_df[cx_df.index >= pd.to_datetime("2026-07-27")].copy()

        plt.figure(figsize=(9, 3.5), dpi=300)
        date_labels = [d.strftime("%m-%d") for d in plot_cx.index]

        plt.plot(
            date_labels,
            plot_cx["Close"],
            marker="o",
            markersize=7,
            color="#2b5c8f",
            label="Daily Closing Price (RMB)",
            linewidth=2.2,
        )
        plt.plot(
            date_labels,
            plot_cx["MA7"],
            color="#e06d53",
            linestyle="--",
            label="7-Day Moving Avg (MA7)",
            linewidth=1.8,
        )

        latest_date_str = plot_cx.index[-1].strftime("%Y-%m-%d")
        latest_val = plot_cx["Close"].iloc[-1]

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
        plt.ylim(plot_cx["Close"].min() - 2.0, plot_cx["Close"].max() + 2.0)
        plt.legend(loc="upper left", fontsize=8.8, frameon=True)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        chart3_path = os.path.join(
            CHART_DIR, "cxmt_price_trend.png"
        )
        plt.savefig(chart3_path)
        plt.close()

    print("\nAnalysis completed. All available charts saved successfully.")
