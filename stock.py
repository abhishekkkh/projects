import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Stock Dashboard")

# Sidebar Inputs
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, MSFT)", value="AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2021-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("today"))

# Fetch Data
data = yf.download(ticker, start=start_date, end=end_date)

if data.empty:
    st.error("⚠️ No data found. Try a different ticker or date range.")
    st.stop()

# Flatten MultiIndex columns (if present)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [' '.join(col).strip() for col in data.columns]
else:
    data.columns = [col.strip() for col in data.columns]

# Auto-detect 'Adj Close' or fallback to 'Close'
close_col = None
for col in data.columns:
    if 'adj close' in col.lower():
        close_col = col
        break
if not close_col:
    for col in data.columns:
        if 'close' in col.lower():
            close_col = col
            st.warning("⚠️ 'Adj Close' not found. Using 'Close' instead.")
            break

if not close_col:
    st.error("❌ Neither 'Adj Close' nor 'Close' found in data.")
    st.write("Available columns:", data.columns.tolist())
    st.stop()

# Price Chart
fig = px.line(data, x=data.index, y=close_col, title=f"{ticker.upper()} - {close_col} Price")
st.plotly_chart(fig, use_container_width=True)

# Tabs
pricing_data, fundamental_data, news = st.tabs(["📈 Pricing Data", "📊 Fundamental Data", "📰 Top 10 News"])

# ---------------- PRICING TAB ----------------
with pricing_data:
    st.header("📈 Price Movements & Risk Metrics")

    data2 = data.copy()
    data2['% Change'] = data2[close_col].pct_change()
    data2.dropna(inplace=True)
    st.dataframe(data2[[close_col, '% Change']].tail(10))

    # Annual Return
    annual_return = data2['% Change'].mean() * 252 * 100
    st.metric("📈 Annual Return", f"{annual_return:.2f}%")

    # Standard Deviation
    stdev = np.std(data2['% Change']) * np.sqrt(252)
    st.metric("📊 Standard Deviation", f"{stdev * 100:.2f}%")

    # Risk-Adjusted Return
    risk_adj_return = annual_return / (stdev * 100) if stdev != 0 else np.nan
    st.metric("⚖️ Risk-Adjusted Return", f"{risk_adj_return:.2f}")

# ---------------- FUNDAMENTAL TAB ----------------
with fundamental_data:
    st.header("📊 Fundamental Data")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader("🔑 Key Metrics")
        metrics = {
            "Market Cap": info.get("marketCap"),
            "PE Ratio (TTM)": info.get("trailingPE"),
            "Forward PE": info.get("forwardPE"),
            "Price to Book": info.get("priceToBook"),
            "Profit Margin": info.get("profitMargins"),
            "Return on Equity": info.get("returnOnEquity"),
            "EPS (TTM)": info.get("trailingEps"),
            "Beta": info.get("beta"),
            "Dividend Yield": info.get("dividendYield"),
            "Earnings Date": info.get("earningsDate")
        }

        for key, value in metrics.items():
            if value is not None:
                st.write(f"**{key}:** {value:.2f}" if isinstance(value, float) else f"**{key}:** {value}")
            else:
                st.write(f"**{key}:** Not available")

        st.subheader("🏢 Company Profile")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Website:** {info.get('website', 'N/A')}")
        st.write(f"**Summary:** {info.get('longBusinessSummary', 'N/A')}")

    except Exception as e:
        st.error(f"❌ Failed to load fundamentals: {e}")

# ---------------- NEWS TAB ----------------
with news:
    st.header("📰 Top 10 News")
    st.info("News integration coming soon! You can use APIs like NewsAPI, Finviz, or Yahoo Finance RSS.")


