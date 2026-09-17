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
    }
    .pick-rank {
        color: #6b7280;
        font-size: 14px;
        width: 28px;
    }
    .pick-ticker {
        font-weight: 700;
        font-size: 16px;
        color: #f5f5f5;
        width: 70px;
    }
    .pick-name {
        color: #9ca3af;
        font-size: 13px;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin: 0 12px;
    }
    .pick-score {
        font-weight: 700;
        font-size: 16px;
        color: #34d399;
        width: 70px;
        text-align: right;
    }
    .pick-sentiment {
        font-size: 12px;
        width: 60px;
        text-align: right;
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

for i, row in top_picks.iterrows():
    sentiment = row.get("news_sentiment", 0)
    if pd.notna(sentiment) and sentiment != 0:
        sentiment_str = f"{sentiment:+.2f}"
        sentiment_color = "#34d399" if sentiment > 0 else "#f87171"
    else:
        sentiment_str = "\u2014"
        sentiment_color = "#6b7280"

    st.markdown(
        f"""
        <div class="pick-row">
            <span class="pick-rank">{i+1}</span>
            <span class="pick-ticker">{row['ticker']}</span>
            <span class="pick-name">{row['name']}</span>
            <span class="pick-sentiment" style="color:{sentiment_color}">{sentiment_str}</span>
            <span class="pick-score">{row['final_score']*100:.1f}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption(
    "This is a personal research tool, not financial advice. Predictions are "
    "based on historical patterns and carry no guarantee of future performance."
)

# Popular Anarchy -- Queen Ventures LLC
