import pandas as pd
import streamlit as st


def render_chapter_selector(df):
    """Render timeline slider in sidebar. Returns selected pd.Timestamp."""
    min_date = df["assumed_date"].min()
    max_date = df["assumed_date"].max()

    selected = st.sidebar.slider(
        "Timeline Date",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=min_date.to_pydatetime(),
        format="MMM YYYY",
    )
    return pd.Timestamp(selected)
