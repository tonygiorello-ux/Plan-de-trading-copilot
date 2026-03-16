import streamlit as st
import os

st.set_page_config(
    page_title="AVGT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

html_path = os.path.join(os.path.dirname(__file__), "avgt_trading.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=1800, scrolling=True)
