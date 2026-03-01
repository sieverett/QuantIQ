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
                help=(
                    "**Standard** — Analyzes each company individually. "
                    "Scores revenue growth, profitability, and liquidity on a 1-5 scale. "
                    "Upload a .zip with one or more company folders, or individual PDF/DOCX files.\n\n"
                    "**Comparative** — Side-by-side analysis of 2+ companies. "
                    "Produces a metrics comparison table, rankings across dimensions, "
                    "and per-company strengths/weaknesses. "
                    "Upload a .zip containing a subfolder per company.\n\n"
                    "**DCF Valuation** — Builds a discounted cash flow model for a single company. "
                    "Extracts financials from your documents, calculates WACC, "
                    "projects 5-year free cash flow, estimates enterprise and equity value, "
                    "and runs a sensitivity analysis. Upload financial statements for one company."
                ),
            )

    return selected
