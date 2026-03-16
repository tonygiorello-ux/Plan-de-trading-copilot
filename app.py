import streamlit as st
import os

st.set_page_config(
    page_title="AVGT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
    background-color: #07070e !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
footer { display: none !important; }
.main > div { padding: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
iframe { display: block; border: none; }
</style>
""", unsafe_allow_html=True)

html_path = os.path.join(os.path.dirname(__file__), "avgt_trading.html")

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=1800, scrolling=True)
