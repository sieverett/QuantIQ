# utils/auth.py

import streamlit as st
import os
from anthropic import Anthropic


def get_assistant():
    """Validate the Anthropic API key by making a test request."""
    try:
        client = Anthropic(api_key=st.session_state.anthropic_api_key)
        # Validate key with a minimal request
        client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        st.session_state.authenticated_flag = True
    except Exception:
        st.warning("Check your API key.")
        st.session_state.authenticated_flag = False


def get_client():
    try:
        client = Anthropic(api_key=st.session_state.anthropic_api_key)
        st.session_state.authenticated_flag = True
    except Exception:
        st.warning("Set your API key.")
        st.session_state.authenticated_flag = False


def store_keys(params, file_path=".streamlit/secrets.toml"):
    """
    Stores API keys securely.

    Args:
        params (dict): Dictionary containing key-value pairs of secrets.
        file_path (str): Path to the secrets file.
    """
    with open(file_path, "w") as env_file:
        for key, value in params.items():
            env_file.write(f'{key}="{value}"\n')
