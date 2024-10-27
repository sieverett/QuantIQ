# utils/session.py

import streamlit as st


def initialize_session_state(defaults):
    """
    Initialize Streamlit session state variables if they don't already exist.

    Args:
        defaults (dict): A dictionary of session state variable names and their default values.
    """
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
