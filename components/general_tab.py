import streamlit as st # pyright: ignore[reportMissingImports]
from services.utils import State_Keys_Map, show_existing_images

def render_general_tab():
    st.selectbox(
        "Quais ferramentas Google o cliente utiliza?", (
            "Selecione", 
            "Google Analytics", 
            "Google Ads", 
            "Search Ads 360",
            "Display & Video 360", 
            "Campaign Manager 360"),
        key=State_Keys_Map.GENERAL_PLATFORMS.value
    )