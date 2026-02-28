# Settings UI

import streamlit as st
from utils.auth import store_keys


def render_settings():
    """ """
    st.text("API key")
    api_key = st.text_input(
        label="Enter your Anthropic API key",
        placeholder="Anthropic API Key",
        type="password",
        help="Go to [Anthropic API key](https://console.anthropic.com/settings/keys) for platform authentication.",
    )
    if api_key:
        st.session_state.anthropic_api_key = api_key
        st.session_state.key_set = True

    # Save Keys Button
    if st.session_state.key_set:
        if st.button(
            "Set Keys",
            key="add_keys",
            help="Set keys for use.",
            use_container_width=True,
        ):
            store_keys(
                params={
                    "ANTHROPIC_API_KEY": st.session_state.anthropic_api_key,
                }
            )
            st.session_state.key_set = False
            st.rerun()

            if st.session_state.authenticated_flag:
                st.toast(":old_key: Authorized")
            else:
                st.toast(":confounded: Not Authorized!")
