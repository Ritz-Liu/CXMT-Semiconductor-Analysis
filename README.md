# CXMT Semiconductor Analysis / CXMT 半导体分析

> Independent Quantitative Research Note / 独立量化研究说明  
> Event-Aligned Normalized Return Analysis / 事件对齐标准化收益分析

## Overview / 项目概述

This repository contains an independent quantitative research workflow examining stock-price responses surrounding the IPO of ChangXin Memory Technologies (CXMT, 688825.SH).

本仓库包含一套独立量化研究流程，用于分析长鑫科技（CXMT，688825.SH）IPO 前后的股票价格表现，并比较不同半导体生态参与者在同一研究窗口内的市场反应。

The project uses an **event-aligned normalized return framework** rather than a conventional abnormal-return event study.

本项目采用**事件对齐标准化收益框架**，而不是传统的异常收益事件研究模型。

**Current status / 当前状态:** Near-Final / Pre-Data-Freeze  
**Event date / 事件日:** 2026-07-27  
**Research window / 研究窗口:** 2026-06-08 to 2026-08-07

The final data refresh will be performed after the August 7 close. At that stage, only date-dependent values, chart endpoints, and the final archived report will be updated. The methodology is already locked.

最终数据将在 8 月 7 日收盘后刷新。届时仅更新与日期相关的数值、图表终点和最终归档研报，不再修改研究方法定义。

---

## Research Scope / 研究范围

| Company / 公司 | Ticker / 代码 | Analytical Role / 分析角色 |
|---|---|---|
| CXMT / 长鑫科技 | 688825.SH | Focal IPO company; memory semiconductor / 核心 IPO 标的；存储半导体 |
| AMEC / 中微公司 | 688012.SH | Upstream semiconductor equipment / 上游半导体设备 |
| SK hynix | 000660.KS | Global memory peer / 全球存储芯片可比公司 |
| Samsung Electronics / 三星电子 | 005930.KS | Global memory peer / 全球存储芯片可比公司 |
| Micron Technology / 美光科技 | MU | Global memory peer / 全球存储芯片可比公司 |
| NVIDIA / 英伟达 | NVDA | Semiconductor design / AI ecosystem / 半导体设计与 AI 生态 |
| Apple / 苹果 | AAPL | Downstream electronics demand / 下游电子需求 |

The sample is intentionally heterogeneous and is organized by ecosystem role rather than treating all companies as semiconductor manufacturers.

样本有意覆盖不同产业角色，按半导体生态位置进行分类，而不是将所有公司统一视为“半导体制造商”。

---

## Methodology / 研究方法

### Normalized Cumulative Return (NCR) / 标准化累计收益率

The main comparative metric is / 主要比较指标为：

```text
NCR(i,t) = [P(i,t) / P(i,0) - 1] × 100%
```

where / 其中：

- `P(i,t)`: closing price of security `i` on date `t` / 股票 `i` 在日期 `t` 的收盘价
- `P(i,0)`: baseline closing price defined for the relevant figure / 对应图表所定义的基准收盘价

NCR is a **descriptive normalized-price measure**. It is not abnormal return (AR), cumulative abnormal return (CAR), or a conventional market-model event-study estimate.

NCR 是一种**描述性的标准化价格表现指标**，不等同于异常收益（AR）、累计异常收益（CAR），也不是传统市场模型事件研究中的异常收益估计。

### Figure-Specific Baselines / 图表基准规则

**Figure 1 — Semiconductor Ecosystem Normalized Return Comparison**  
**图 1 — 半导体生态标准化收益比较**

Coverage / 标的：

- AMEC
- NVIDIA
- Apple

Baseline / 基准：

- each security's first valid closing price on or after **2026-06-08**
- 每只股票在 **2026-06-08 当日或之后的第一个有效收盘价**

**Figure 2 — Event-Aligned Memory Sector Performance Comparison**  
**图 2 — 事件对齐的存储行业表现比较**

Coverage / 标的：

- CXMT
- Micron
- Samsung Electronics
- SK hynix

Baseline / 基准：

- common event date: **2026-07-27**
- 统一事件日：**2026-07-27**
- all four series are set to **0% NCR** on the event date
- 四只股票在事件日统一设为 **0% NCR**

**Figure 3 — CXMT Post-IPO Price Development**  
**图 3 — CXMT 上市后价格走势**

Metric / 指标：

- CXMT daily closing price in RMB / CXMT 每日收盘价（人民币）
- 7-Trading-Day Moving Average (MA7) / 7 个交易日移动平均线（MA7）

Figure 3 does not use NCR.  
图 3 不使用 NCR。

### 7-Trading-Day Moving Average (MA7) / 7 个交易日移动平均线

```text
MA7(t) = [P(t) + P(t-1) + P(t-2) + ... + P(t-6)] / 7
```

Equivalent summation form / 等价求和形式：

```text
MA7(t) = (1/7) × Σ[k=0 to 6] P(t-k)
```

Locked Python implementation / 锁定的 Python 实现：

```python
rolling(window=7, min_periods=7)
```

MA7 is calculated only after seven valid trading observations are available.

MA7 仅在取得 7 个完整有效交易观测值后才开始计算。

---

## Current Pre-Freeze Figures / 当前冻结前图表

These charts use currently available observations and are **not yet the final August 7 data-freeze versions**.

以下图表使用当前已经获得的真实市场数据，**尚不是 8 月 7 日数据冻结后的最终版本**。

### Figure 1 / 图 1

![Figure 1](output/charts/upstream_downstream_chain.png)

### Figure 2 / 图 2

![Figure 2](output/charts/memory_sector_comparison.png)

### Figure 3 / 图 3

![Figure 3](output/charts/cxmt_price_trend.png)

---

## Market Data Sources / 市场数据来源

| Market / 市场 | Primary Source / 主要来源 | Fallback / 备用来源 |
|---|---|---|
| China A-share / 中国 A 股 | Tencent Finance / 腾讯财经 | Cached real CSV observations / 已缓存真实 CSV 数据 |
| United States / 美国 | Sina Finance / 新浪财经 | Yahoo Finance, then cached real CSV / Yahoo Finance，其次真实 CSV 缓存 |
| South Korea / 韩国 | Naver Stock | Cached real CSV observations / 已缓存真实 CSV 数据 |

The U.S. workflow checks data freshness before accepting the Sina series when a newer fallback series may be required.

美国股票数据会进行 freshness check；当新浪数据明显滞后时，程序可切换到 Yahoo Finance 备用源。

---

## Data Integrity Rules / 数据完整性规则

The workflow follows these rules / 研究流程遵循以下规则：

- no artificial price generation / 不生成虚假价格
- no future-data generation / 不生成未来数据
- no forward filling or backward filling / 不使用前向填充或后向填充
- no manual insertion of unavailable prices / 不人工补入缺失价格
- no interpolation of missing price paths / 不对缺失价格路径做插值
- preserve actual exchange-specific trading dates / 保留各交易所真实交易日
- use daily closing prices unless a separate OHLC source is explicitly documented / 除非另有明确 OHLC 数据源，否则统一使用每日收盘价
- allow cached CSV fallback only for previously retrieved real observations / CSV 缓存仅允许保存和调用此前真实获取的数据

For Figure 2, observed trading dates may be displayed as equally spaced categories for readability. This changes presentation only and does not create synthetic observations.

图 2 为提高可读性，可将真实观测交易日按等距类别显示。该调整仅影响展示方式，不会生成任何虚假交易数据。

---

## Project Structure / 项目结构

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

最终归档研报将在数据冻结后加入仓库。

---

## Reproducibility / 可复现性

Install dependencies / 安装依赖：

```bash
pip install -r requirements.txt
```

Run from the repository root / 在仓库根目录运行：

```bash
python src/generate_report_charts.py
```

The script will / 脚本将：

1. retrieve available market data / 获取当前可用市场数据
2. validate and clean observations / 验证并清洗观测值
3. preserve actual exchange trading dates / 保留真实交易日
4. apply figure-specific baseline rules / 应用图表专属基准规则
5. calculate NCR and MA7 / 计算 NCR 与 MA7
6. save market-data CSV files to `data/` / 将市场数据保存至 `data/`
7. export charts to `output/charts/` / 将图表输出至 `output/charts/`

---

## Research Limitations / 研究局限

This project is descriptive.

本项目属于描述性量化研究。

It does not / 本项目不：

- estimate expected returns / 估计预期收益
- estimate market-model alpha or beta / 估计市场模型 alpha 或 beta
- calculate AR or CAR / 计算 AR 或 CAR
- establish that the CXMT IPO caused observed price movements / 证明 CXMT IPO 导致了观察到的全部价格变化
- infer institutional buying from price data alone / 仅凭价格数据推断机构买入
- provide technical trading signals / 提供技术交易信号
- provide investment recommendations / 提供投资建议

Observed differences may reflect company-specific information, semiconductor-industry conditions, broader market sentiment, macroeconomic factors, and cross-market trading differences.

观察到的差异可能同时受到公司自身信息、半导体行业环境、整体市场情绪、宏观经济因素以及跨市场交易制度差异影响。

---

## Research Status / 研究状态

### Locked Before Final Data Freeze / 数据冻结前已锁定

- research identity / 研究定位
- event date / 事件日
- research window / 研究窗口
- NCR definition / NCR 定义
- Figure 1 baseline / 图 1 基准
- Figure 2 common IPO baseline / 图 2 统一 IPO 基准
- Figure 3 metric / 图 3 指标
- MA7 definition / MA7 定义
- source mapping / 数据源映射
- calendar handling / 交易日处理
- data-integrity rules / 数据完整性规则
- interpretation boundaries / 解释边界

### Final Refresh After August 7 Close / 8 月 7 日收盘后最终刷新

The final refresh will update only / 最终刷新仅更新：

- date-dependent values / 日期相关数值
- final NCR endpoints / 最终 NCR 终点值
- final MA7 values / 最终 MA7 数值
- Figures 1–3 / 图 1–3
- final research report / 最终研报
- final GitHub release / 最终 GitHub Release
- Zenodo archival information / Zenodo 归档信息

Zenodo archival and DOI assignment will follow the final research freeze. The DOI will be added after the archived version is created.

Zenodo 归档与 DOI 分配将在最终研究冻结后进行，归档版本创建完成后再将 DOI 回填到仓库和研报中。

---

## Documentation / 文档

- [`methodology/research_methodology.md`](methodology/research_methodology.md)
- [`methodology/mathematical_models.md`](methodology/mathematical_models.md)
- [`methodology/variables_definition.md`](methodology/variables_definition.md)
- [`references/data_sources.md`](references/data_sources.md)
- [`references/industry_reports.md`](references/industry_reports.md)
- [`references/academic_references.md`](references/academic_references.md)

---

## License / 许可证

This repository uses the **MIT License**. See [`LICENSE`](LICENSE) for details.

本仓库采用 **MIT License（MIT 许可证）**。具体条款请参阅 [`LICENSE`](LICENSE)。
