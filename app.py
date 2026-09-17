# Popular Anarchy -- Queen Ventures LLC
"""
app.py

The Streamlit website version of your predictor. Reads latest_predictions.csv
(the file predict.py already saves every time you run it) and displays it as
a clean, browsable page -- no API keys or model needed here, this is purely
a DISPLAY layer on top of work predict.py already did.

To run locally:
  streamlit run app.py

To deploy: push this file (plus latest_predictions.csv) to a GitHub repo,
then connect that repo at share.streamlit.io.
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import os

st.set_page_config(
    page_title="Stock Predictor",
    page_icon="\U0001F4C8",
    layout="centered",
)

# ---- Simple, clean styling ----
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    .pick-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px;
        margin-bottom: 8px;
        border-radius: 10px;
        background-color: #1c1f26;
        border: 1px solid #2a2e37;
        flex-wrap: wrap;
        gap: 4px 0;
    }
    .pick-left {
        display: flex;
        align-items: center;
        min-width: 0;
        flex: 1 1 260px;
    }
    .pick-right {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 0 0 auto;
    }
    .pick-rank {
        color: #6b7280;
        font-size: 14px;
        width: 26px;
        flex-shrink: 0;
    }
    .pick-ticker {
        font-weight: 700;
        font-size: 16px;
        color: #f5f5f5;
        width: 62px;
        flex-shrink: 0;
    }
    .pick-name {
        color: #9ca3af;
        font-size: 13px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
    }
    .pick-price {
        font-size: 13px;
        color: #d1d5db;
        width: 68px;
        text-align: right;
    }
    .pick-change {
        font-size: 12px;
        width: 58px;
        text-align: right;
    }
    .pick-volume {
        font-size: 12px;
        color: #6b7280;
        width: 56px;
        text-align: right;
    }
    .pick-score {
        font-weight: 700;
        font-size: 16px;
        color: #34d399;
        width: 60px;
        text-align: right;
    }
    .pick-header {
        display: flex;
        justify-content: flex-end;
        gap: 16px;
        padding: 0 18px;
        margin-bottom: 4px;
        color: #4b5563;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    /* Make the "details" button sit flush under each card, low-key styling */
    div[data-testid="stButton"] {
        margin-top: -10px;
        margin-bottom: 10px;
    }
    div[data-testid="stButton"] button {
        width: 100%;
        background-color: #1c1f26;
        border: 1px solid #2a2e37;
        border-top: none;
        border-radius: 0 0 10px 10px;
        color: #6b7280;
        font-size: 11px;
        padding: 2px 0;
        height: auto;
    }
    div[data-testid="stButton"] button:hover {
        color: #34d399;
        border-color: #34d399;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("\U0001F4C8 Stock Predictor")
st.caption("Which stocks are most likely to rise over the next trading week")

PREDICTIONS_FILE = "latest_predictions.csv"

if not os.path.exists(PREDICTIONS_FILE):
    st.warning(
        "No predictions found yet. Run `python predict.py` first to generate "
        "`latest_predictions.csv`, then refresh this page."
    )
    st.stop()

df = pd.read_csv(PREDICTIONS_FILE)

# Show when this data was generated
file_time = datetime.fromtimestamp(os.path.getmtime(PREDICTIONS_FILE))
st.caption(f"Last updated: {file_time.strftime('%B %d, %Y at %I:%M %p')}")

top_n = st.slider("Show top", min_value=10, max_value=100, value=25, step=5)

top_picks = df.sort_values("final_score", ascending=False).head(top_n).reset_index(drop=True)

st.markdown(
    """
    <div class="pick-header">
        <span style="width:68px">Price</span>
        <span style="width:58px">1D</span>
        <span style="width:56px">Vol</span>
        <span style="width:70px">Confidence</span>
    </div>
    """,
    unsafe_allow_html=True,
)

def _format_volume(v):
    if pd.isna(v):
        return "\u2014"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}K"
    return f"{v:.0f}"


@st.dialog("Stock Details")
def show_details(row):
    st.subheader(f"{row['ticker']} \u2014 {row['name']}")
    st.metric("Confidence", f"{row['final_score']*100:.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        price = row.get("close")
        st.metric("Price", f"${price:,.2f}" if pd.notna(price) else "\u2014")
        daily_change = row.get("return_1d")
        st.metric("1-day change", f"{daily_change*100:+.2f}%" if pd.notna(daily_change) else "\u2014")
    with col2:
        volume = row.get("volume")
        st.metric("Volume", _format_volume(volume) if pd.notna(volume) else "\u2014")
        rsi = row.get("rsi_14")
        st.metric("RSI (14-day)", f"{rsi:.1f}" if pd.notna(rsi) else "\u2014")

    st.markdown("**Trend vs. moving averages**")
    for label, col in [("10-day", "price_vs_sma10"), ("20-day", "price_vs_sma20"), ("50-day", "price_vs_sma50")]:
        val = row.get(col)
        if pd.notna(val):
            st.write(f"{label}: {val*100:+.1f}% vs. average")

    st.caption("Not financial advice \u2014 a research tool based on historical patterns.")


for i, row in top_picks.iterrows():
    price = row.get("close")
    price_str = f"${price:,.2f}" if pd.notna(price) else "\u2014"

    daily_change = row.get("return_1d")
    if pd.notna(daily_change):
        change_str = f"{daily_change*100:+.1f}%"
        change_color = "#34d399" if daily_change > 0 else "#f87171"
    else:
        change_str = "\u2014"
        change_color = "#6b7280"

    volume_str = _format_volume(row.get("volume"))

    st.markdown(
        f"""
        <div class="pick-row">
            <div class="pick-left">
                <span class="pick-rank">{i+1}</span>
                <span class="pick-ticker">{row['ticker']}</span>
                <span class="pick-name">{row['name']}</span>
            </div>
            <div class="pick-right">
                <span class="pick-price">{price_str}</span>
                <span class="pick-change" style="color:{change_color}">{change_str}</span>
                <span class="pick-volume">{volume_str}</span>
                <span class="pick-score">{row['final_score']*100:.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("View details \u25be", key=f"details_{row['ticker']}_{i}"):
        show_details(row)

st.markdown("---")
st.caption(
    "This is a personal research tool, not financial advice. Predictions are "
    "based on historical patterns and carry no guarantee of future performance."
)

# Popular Anarchy -- Queen Ventures LLC
