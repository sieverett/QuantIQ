# components/sidebar.py

import streamlit as st
from streamlit_option_menu import option_menu
from quantiq.logo_manager import render_logo


def render_sidebar():
    with st.sidebar:
        render_logo()
        st.title("QUANT-IQ")

        selected = option_menu(
            "Main Menu",
            ["Analyze", "Prompt", "Settings"],
            icons=["magic", "list-task", "gear"],
            menu_icon="cast",
            default_index=0,
        )

        with st.expander("Analysis Mode"):
            st.session_state.analysis_mode = st.radio(
                "Mode",
                ["Standard", "Comparative", "DCF Valuation"],
                index=["Standard", "Comparative", "DCF Valuation"].index(
                    st.session_state.get("analysis_mode", "Standard")
                ),
                help="Standard: single-company scoring. Comparative: multi-company side-by-side. DCF Valuation: discounted cash flow model.",
            )

    return selected
