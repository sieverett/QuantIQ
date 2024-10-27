# utils/auth.py

import streamlit as st
import os
from openai import OpenAI


def get_assistant():
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        client.beta.assistants.retrieve(st.session_state.openai_assistant_id)
        st.session_state.authenticated_flag = True
    except Exception:
        st.warning("Check your API key and/or Assistant ID.")
        st.session_state.authenticated_flag = False


def get_client():
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
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
