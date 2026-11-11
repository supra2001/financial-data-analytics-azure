# Nifty 50 Financial Market Analytics

An end-to-end financial data analytics project using **Python, Azure Data Explorer (ADX), KQL, Pandas and Streamlit** to explore historical Nifty 50 stock market data.

The project focuses on historical price trends, volatility, stock correlations and trading activity through data analysis and an interactive dashboard.

---

## 1. Project Overview

The objective of this project is to build a financial analytics solution using historical Nifty 50 stock market data.

The project follows a data analytics workflow:

1. Understand and inspect the raw dataset.
2. Ingest the data into Azure Data Explorer.
3. Query financial data using KQL and Python.
4. Clean and prepare the dataset.
5. Perform Exploratory Data Analysis (EDA).
6. Build an interactive Streamlit dashboard.
7. Generate insights from historical stock market data.

**Dataset Period:** January 2000 – April 2021

**Selected Stocks for Analysis:**
- RELIANCE
- HDFCBANK
- TCS
- INFY

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and analysis |
| Pandas | Data manipulation and cleaning |
| NumPy | Numerical operations |
| Azure Data Explorer | Cloud-based data storage and querying |
| KQL | Querying and aggregating financial data |
| Azure Kusto Python SDK | Connecting Python to ADX |
| Matplotlib | Data visualization during EDA |
| Seaborn | Correlation heatmap |
| Plotly | Interactive dashboard visualizations |
| Streamlit | Dashboard development |
| Jupyter Notebook | Analysis and experimentation |

---

## 3. Dataset

**Dataset:** NIFTY-50 Stock Market Data

**Source:** Kaggle – Nifty 50 Stock Market Data

The dataset contains historical daily stock market information for Nifty 50 companies.

### Dataset Information

| Attribute | Value |
|---|---|
| Total Records | 235,192 |
| Original Columns | 15 |
| Unique Stock Symbols | 65 |
| Start Date | 2000-01-03 |
| End Date | 2021-04-30 |
| Record Granularity | One record per stock per trading date |

### Important Columns

| Column | Description |
|---|---|
| Date | Trading date |
| Symbol | Stock symbol |
| Prev Close | Previous closing price |
| Open | Opening price |
| High | Highest price during the trading day |
| Low | Lowest price during the trading day |
| Last | Last traded price |
| Close | Closing price |
| VWAP | Volume Weighted Average Price |
| Volume | Number of shares traded |
| Turnover | Trading turnover |
| Trades | Number of trades |
| Deliverable Volume | Quantity of deliverable shares |
| %Deliverble | Percentage of deliverable volume |

---

## 4. Project Workflow

### Step 1: Data Understanding

The raw CSV dataset was loaded using Pandas.

Initial data inspection included:

- Dataset dimensions and data types.
- Statistical summary.
- Missing value analysis.
- Duplicate record detection.
- Zero-value investigation.
- Turnover consistency investigation.

**Key Findings:**

- No duplicate records were found using `(Date, Symbol)` as the natural key.
- The `Trades` column contained significant missing values in earlier years.
- Missing values were retained instead of applying unnecessary imputation.
- One record contained zero values in `Prev Close` and `Open`, which were treated as invalid and converted to null values.

### Step 2: Azure Data Explorer Setup

Azure Data Explorer was used as the cloud database for storing and querying the financial dataset.

**Database:** `Financial_Data`

**Table:** `NIFTY50_all`

The dataset was ingested into ADX and queried using KQL.

Important KQL operations demonstrated:

- `where` – Filtering records.
- `project` – Selecting relevant columns.
- `summarize` – Aggregating financial data.
- `arg_max` – Retrieving the latest record.
- `bin()` – Time-based aggregation.

### Step 3: Python and ADX Integration

The Azure Kusto Python SDK was used to establish a connection between Python and Azure Data Explorer.

A reusable helper function was created to execute KQL queries and return results as Pandas DataFrames.

This allowed financial data to be retrieved directly from ADX for further processing and analysis.

### Step 4: Data Cleaning and Preparation

The raw dataset was preserved in ADX.

A corrected turnover column was created during querying:

```python
Turnover_corrected = Turnover / 100000
```

This conversion was applied because the original turnover values were approximately 100,000 times the corresponding rupee-denominated values.

The corrected dataset was retrieved from ADX and saved in Parquet format for efficient local analysis.

**Output File:** `nifty50_cleaned.parquet`

---

## 5. Exploratory Data Analysis (EDA)

EDA was performed using Python, Pandas, Matplotlib and Seaborn.

Four major analyses were completed.

### 5.1 Trend Analysis

**Objective:** Compare historical closing price movements across RELIANCE, HDFCBANK, TCS and INFY.

**Methodology:**
- Selected four stocks.
- Aggregated closing prices into 30-day intervals using KQL.
- Visualized historical price movements using line charts.
- Investigated unusually large price discontinuities.

**Key Insights:**
- The selected stocks showed different long-term price movement patterns.
- Historical market disruptions were visible in the price trends.
- Large price discontinuities may be associated with corporate actions such as stock splits and bonus issues.
- Raw closing prices are not directly comparable across stocks because their nominal price levels differ.

### 5.2 Volatility Analysis

**Objective:** Compare the historical price volatility of the selected stocks.

**Methodology:**
- Calculated daily percentage returns.
- Measured volatility using the standard deviation of daily returns.
- Investigated extreme negative returns.
- Compared initial volatility with volatility after excluding 10 suspected corporate-action-related observations.

**Key Insights:**
- INFY initially recorded the highest volatility among the selected stocks.
- After filtering the identified extreme negative observations, RELIANCE recorded the highest volatility.
- All four stocks showed a reduction in measured volatility after filtering.

### 5.3 Correlation Analysis

**Objective:** Understand how the daily returns of selected stocks move in relation to each other.

**Methodology:**
- Aligned daily returns by trading date.
- Calculated Pearson correlation coefficients.
- Visualized the results using a correlation heatmap.

**Key Insights:**

| Stock Pair | Correlation |
|---|---:|
| INFY – TCS | 0.510 |
| HDFCBANK – RELIANCE | 0.402 |
| RELIANCE – TCS | 0.380 |
| HDFCBANK – TCS | 0.341 |
| HDFCBANK – INFY | 0.226 |
| INFY – RELIANCE | 0.219 |

- INFY and TCS showed the strongest positive correlation.
- INFY and RELIANCE showed the weakest correlation.
- All six stock pairs showed positive correlations.
- Correlation indicates association, not causation.

### 5.4 Trading Activity Analysis

**Objective:** Compare the trading activity of the selected stocks using volume and turnover.

**Methodology:**
- Calculated average daily trading volume.
- Calculated average daily turnover using corrected turnover values.
- Compared both metrics using bar charts.

**Key Insights:**

| Stock | Average Daily Volume | Average Daily Turnover |
|---|---:|---:|
| RELIANCE | 5.58 million | ₹60.77 crore |
| INFY | 4.50 million | ₹51.48 crore |
| HDFCBANK | 2.10 million | ₹24.49 crore |
| TCS | 1.68 million | ₹29.52 crore |

- RELIANCE recorded the highest average daily volume and turnover.
- INFY ranked second in both measures.
- TCS had lower average volume than HDFCBANK but higher turnover.
- Trading volume and turnover provide different perspectives on market activity.

---

## 6. Streamlit Dashboard

An interactive dashboard was developed using Streamlit and Plotly.

The dashboard allows users to select stocks and date ranges to explore financial information.

### Dashboard Sections

**1. Market Overview**
- Selected stock count.
- Average latest stock price.
- Average daily trading volume.
- Average daily turnover.
- Latest available stock prices.

**2. Performance Analysis**
- Historical closing price movement.
- Normalized price comparison.

**3. Risk Analysis**
- Daily return volatility comparison.
- Stock return correlation heatmap.

**4. Trading Activity**
- Average daily trading volume.
- Average daily trading turnover.

### Interactive Features

- Stock selection.
- Historical date range selection.
- Interactive Plotly charts.
- Financial metrics and summary tables.

---

## 7. Project Structure

```text
nifty50-financial-market-analytics/
│
├── Data/
│   ├── NIFTY50_all.csv
│   └── nifty50_cleaned.parquet
│
├── notebooks/
│   ├── 01_data_sanity_check.ipynb
│   ├── 02_database_connection_and_cleaning.ipynb
│   └── 03_EDA.ipynb
│
├── src/
│   └── adx_connection.py
│
├── app.py
├── config.toml
├── requirements.txt
└── README.md
```

---

**Live WebApp**: https://financialapp242001.streamlit.app/