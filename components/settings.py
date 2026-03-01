# Settings UI

import os
import streamlit as st
from utils.auth import store_keys


def render_settings():
    st.text("API key")
    api_key = st.text_input(
        label="Enter your Anthropic API key",
        placeholder="Anthropic API Key",
        type="password",
        help="Go to [Anthropic API key](https://console.anthropic.com/settings/keys) for platform authentication.",
    )
    if api_key:
        st.session_state.anthropic_api_key = api_key

    if st.button(
        "Set Keys",
        key="add_keys",
        help="Save and validate your API key.",
        use_container_width=True,
    ):
        if not st.session_state.get("anthropic_api_key"):
            st.error("Enter an API key first.")
        else:
            os.makedirs(".streamlit", exist_ok=True)
            store_keys(
                params={"ANTHROPIC_API_KEY": st.session_state.anthropic_api_key}
            )
            # Validate the key
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=st.session_state.anthropic_api_key)
                client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "ping"}],
                )
                st.session_state.authenticated_flag = True
                st.success("API key saved and validated.")
            except Exception as e:
                error_msg = str(e)
                if "credit balance" in error_msg or "billing" in error_msg.lower():
                    st.session_state.authenticated_flag = True
                    st.warning("API key is valid but your account has no credits. "
                               "Visit [Plans & Billing](https://console.anthropic.com/settings/billing) to add credits.")
                elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    st.session_state.authenticated_flag = False
                    st.error("Invalid API key. Check it and try again.")
                else:
                    st.session_state.authenticated_flag = False
                    st.error(f"Validation failed: {e}")
