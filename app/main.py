import pandas as pd
import streamlit as st

from app.components.chapter_selector import render_chapter_selector
from app.data import compute_positions, load_data
from app.map import build_map

st.set_page_config(page_title="Bobiverse Tactical Tracker", layout="wide")
st.title("🌌 Bobiverse Tactical Movement Map")

try:
    df = load_data()
    selected_date = render_chapter_selector(df)
    positions = compute_positions(df, selected_date)
    fig, status_list = build_map(positions)

    st.plotly_chart(fig, use_container_width=True)
    st.subheader(f"Tactical Status: {selected_date.date()}")
    st.table(pd.DataFrame(status_list))

except Exception as e:
    st.error(f"Error: {e}")
