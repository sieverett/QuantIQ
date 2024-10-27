# components/sidebar.py

import streamlit as st
from streamlit_option_menu import option_menu
from utils.auth import get_assistant, get_client
from quantiq import quantiq__ as qiq


def render_sidebar():
    """
    Renders the sidebar with the main menu and settings.
    """
    with st.sidebar:
        # Title and Logo
        qiq.handle_logo()
        st.title("QUANT-IQ")

        # Main Menu
        selected = option_menu(
            "Main Menu",
            ["Analyze", "Prompt", "Settings"],
            icons=["magic", "list-task", "gear"],
            menu_icon="cast",
            default_index=0,
        )

        # Assistant Mode Toggle
        with st.expander("Mode"):
            st.session_state.assistant_mode = st.radio(
                "Assistant Mode",
                ["On", "Off"],
                index=1,
                help="On uses AI Assistant or off use Completions.",
            )

            # Authenticate based on mode
            if st.session_state.assistant_mode == "On":
                get_assistant()
            else:
                get_client()

    return selected
