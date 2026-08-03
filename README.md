# CXMT-Semiconductor-Analysis

## 长鑫存储半导体产业链分析项目

A semiconductor stock analysis project focusing on CXMT (ChangXin Memory
Technologies) and global semiconductor companies.

本项目围绕
CXMT（长鑫存储）以及全球半导体产业链企业进行真实市场数据分析与可视化。

------------------------------------------------------------------------

# Features \| 项目特点

## English

-   Real market trading data analysis
-   Semiconductor industry chain comparison
-   Historical return comparison
-   CXMT IPO performance tracking
-   Global semiconductor company comparison
-   Automated chart generation
-   No artificial price generation
-   No future data generation
-   No filling of missing trading data

## 中文

-   使用真实市场行情数据
-   支持半导体产业链企业比较
-   支持 CXMT IPO 后表现跟踪
-   支持全球半导体企业对比分析
-   自动生成分析图表
-   不生成虚假价格
-   不生成未来数据
-   不人为填充缺失交易数据

------------------------------------------------------------------------

# Data Policy \| 数据原则

## English

This project follows a strict real-data policy.

-   Missing trading dates are not filled artificially.
-   Future market data is never generated.
-   Non-trading days remain empty.
-   Different market schedules are respected.

## 中文

本项目遵循严格的数据真实性原则。

-   不人为补充不存在的交易数据
-   不生成未来行情数据
-   不使用模拟价格填补空缺
-   尊重不同交易市场时间安排

------------------------------------------------------------------------

# Project Structure \| 项目结构

``` text
CXMT-Semiconductor-Analysis/

├── data/
│   ├── AMEC_688012_SH.csv
│   ├── CXMT_688825_SH.csv
│   ├── SK_HYNIX_000660_KS.csv
│   ├── SAMSUNG_005930_KS.csv
│   ├── MICRON_MU_US.csv
│   ├── APPLE_AAPL_US.csv
│   └── NVIDIA_NVDA_US.csv
│
├── output/
│   └── charts/
│       ├── upstream_downstream_chain.png
│       ├── memory_sector_comparison.png
│       └── cxmt_price_trend.png
│
├── src/
│   └── generate_report_charts.py
│
├── README.md
└── LICENSE
```

------------------------------------------------------------------------

# Installation \| 安装

## Requirements \| 环境要求

-   Python 3.10+
-   pip package manager

## Install Dependencies \| 安装依赖

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# Usage \| 使用方法

``` bash
python src/generate_report_charts_EN.py
```

------------------------------------------------------------------------

# Disclaimer \| 免责声明

This project is for research and educational purposes only.

本项目仅用于研究和学习用途。

------------------------------------------------------------------------

# License \| 许可证

This project is licensed under the MIT License.

本项目采用 MIT 开源许可证。

------------------------------------------------------------------------

---

# Author | 作者

Ritz-Liu

Project creator and maintainer.

项目创建者与维护者。
