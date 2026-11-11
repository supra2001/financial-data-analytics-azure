import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nifty 50 Financial Analytics",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# 2. LOAD DATA
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_PATH = PROJECT_ROOT / "Data" / "nifty50_cleaned.parquet"


@st.cache_data
def load_data():

    df = pd.read_parquet(DATA_PATH)

    df["Date"] = pd.to_datetime(df["Date"], utc=True)
    df["Date"] = df["Date"].dt.tz_localize(None)

    df = df.sort_values(["Symbol", "Date"])

    # Calculate daily percentage returns
    df["Daily_Return_Pct"] = (
        (df["Close"] / df["Prev Close"]) - 1
    ) * 100

    # Remove invalid returns
    df.loc[
        ~np.isfinite(df["Daily_Return_Pct"]),
        "Daily_Return_Pct"
    ] = np.nan

    # Exclude the 10 extreme negative observations
    # identified during the EDA corporate-action investigation.
    df["Filtered_Return_Pct"] = df["Daily_Return_Pct"].where(
        ~df["Daily_Return_Pct"].between(-85, -45)
    )

    return df


try:
    df = load_data()

except Exception as e:

    st.error(f"Unable to load dataset: {e}")
    st.stop()


# ============================================================
# 3. CONSTANTS
# ============================================================

DEFAULT_STOCKS = [
    "RELIANCE",
    "HDFCBANK",
    "TCS",
    "INFY"
]

AVAILABLE_STOCKS = sorted(
    df["Symbol"].dropna().unique()
)


# ============================================================
# 4. SIDEBAR FILTERS
# ============================================================

st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("---")


selected_stocks = st.sidebar.multiselect(
    "Select Stocks",
    AVAILABLE_STOCKS,
    default=DEFAULT_STOCKS
)


if not selected_stocks:

    st.warning("Please select at least one stock.")
    st.stop()


min_date = df["Date"].min().date()
max_date = df["Date"].max().date()


date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


if len(date_range) != 2:

    st.warning("Please select both a start date and an end date.")
    st.stop()


start_date, end_date = date_range


if start_date > end_date:

    st.error("Start date cannot be after end date.")
    st.stop()


# Filter dataset
filtered_df = df[
    (df["Symbol"].isin(selected_stocks)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
].copy()


if filtered_df.empty:

    st.warning("No data available for the selected filters.")
    st.stop()


# ============================================================
# 5. DASHBOARD HEADER
# ============================================================

st.title("Nifty 50 Financial Analytics Dashboard")

st.markdown(
    """
    An interactive financial analytics dashboard built using
    Python, Azure Data Explorer, Pandas and Streamlit.

    Explore historical stock performance, risk metrics,
    correlation and trading activity.
    """
)

st.markdown("---")


# ============================================================
# 6. MARKET OVERVIEW
# ============================================================

st.header("1. Market Overview")


# Latest available record for each selected stock
latest_data = (
    df[df["Symbol"].isin(selected_stocks)]
    .sort_values("Date")
    .groupby("Symbol")
    .tail(1)
)

latest_data = latest_data.sort_values("Symbol")


# Calculate summary metrics
total_avg_volume = filtered_df["Volume"].mean()

total_avg_turnover = filtered_df["Turnover_corrected"].mean()

latest_avg_price = latest_data["Close"].mean()


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Selected Stocks",
    len(selected_stocks)
)

col2.metric(
    "Average Latest Price",
    f"₹{latest_avg_price:,.2f}"
)

col3.metric(
    "Average Daily Volume",
    f"{total_avg_volume:,.0f}"
)

col4.metric(
    "Average Daily Turnover",
    f"₹{total_avg_turnover / 1e7:,.2f} Cr"
)


# Latest stock prices
st.subheader("Latest Stock Prices")


display_latest = latest_data[
    [
        "Symbol",
        "Date",
        "Close",
        "Volume",
        "Turnover_corrected"
    ]
].copy()


display_latest["Date"] = display_latest["Date"].dt.date

display_latest["Turnover_corrected"] = (
    display_latest["Turnover_corrected"] / 1e7
)


display_latest = display_latest.rename(
    columns={
        "Close": "Latest Price (₹)",
        "Volume": "Volume",
        "Turnover_corrected": "Turnover (₹ Crore)"
    }
)


st.dataframe(
    display_latest,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 7. PERFORMANCE ANALYSIS
# ============================================================

st.markdown("---")

st.header("2. Performance Analysis")


# Historical closing price
st.subheader("Historical Closing Price")


fig_price = px.line(
    filtered_df,
    x="Date",
    y="Close",
    color="Symbol",
    title="Historical Closing Price Movement"
)


fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Closing Price (₹)",
    hovermode="x unified"
)


st.plotly_chart(
    fig_price,
    use_container_width=True
)


# Normalized price comparison
st.subheader("Normalized Price Comparison")


st.caption(
    "Each stock starts at an index value of 100. "
    "This compares relative price movements rather than nominal prices."
)


normalized_data = filtered_df.sort_values(
    ["Symbol", "Date"]
).copy()


normalized_data["Normalized_Price"] = (
    normalized_data.groupby("Symbol")["Close"]
    .transform(
        lambda x: (x / x.iloc[0]) * 100
    )
)


fig_normalized = px.line(
    normalized_data,
    x="Date",
    y="Normalized_Price",
    color="Symbol",
    title="Normalized Price Performance (Base = 100)"
)


fig_normalized.update_layout(
    xaxis_title="Date",
    yaxis_title="Normalized Price Index",
    hovermode="x unified"
)


st.plotly_chart(
    fig_normalized,
    use_container_width=True
)


# ============================================================
# 8. RISK ANALYSIS
# ============================================================

st.markdown("---")

st.header("3. Risk Analysis")


risk_data = filtered_df.dropna(
    subset=["Filtered_Return_Pct"]
).copy()


# Daily return volatility
st.subheader("Daily Return Volatility")


volatility_summary = (
    risk_data.groupby("Symbol")["Filtered_Return_Pct"]
    .std()
    .reset_index(name="Daily_Volatility")
)


fig_volatility = px.bar(
    volatility_summary,
    x="Symbol",
    y="Daily_Volatility",
    color="Symbol",
    title="Daily Return Standard Deviation"
)


fig_volatility.update_layout(
    xaxis_title="Stock",
    yaxis_title="Daily Volatility (%)",
    showlegend=False
)


st.plotly_chart(
    fig_volatility,
    use_container_width=True
)


# Correlation analysis
st.subheader("Stock Return Correlation")


correlation_data = risk_data.pivot(
    index="Date",
    columns="Symbol",
    values="Filtered_Return_Pct"
)


correlation_matrix = correlation_data.corr()


fig_corr = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Correlation Matrix of Daily Returns"
)


fig_corr.update_layout(
    height=600
)


st.plotly_chart(
    fig_corr,
    use_container_width=True
)


# ============================================================
# 9. TRADING ACTIVITY
# ============================================================

st.markdown("---")

st.header("4. Trading Activity")


trading_summary = (
    filtered_df.groupby("Symbol")
    .agg(
        Average_Volume=("Volume", "mean"),
        Average_Turnover=("Turnover_corrected", "mean")
    )
    .reset_index()
)


col1, col2 = st.columns(2)


# Average trading volume
with col1:

    fig_volume = px.bar(
        trading_summary,
        x="Symbol",
        y="Average_Volume",
        color="Symbol",
        title="Average Daily Trading Volume"
    )

    fig_volume.update_layout(
        xaxis_title="Stock",
        yaxis_title="Average Shares Traded",
        showlegend=False
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True
    )


# Average trading turnover
with col2:

    trading_summary["Average_Turnover_Crore"] = (
        trading_summary["Average_Turnover"] / 1e7
    )

    fig_turnover = px.bar(
        trading_summary,
        x="Symbol",
        y="Average_Turnover_Crore",
        color="Symbol",
        title="Average Daily Trading Turnover"
    )

    fig_turnover.update_layout(
        xaxis_title="Stock",
        yaxis_title="Average Turnover (₹ Crore)",
        showlegend=False
    )

    st.plotly_chart(
        fig_turnover,
        use_container_width=True
    )


# ============================================================
# 10. FOOTER
# ============================================================

st.markdown("---")