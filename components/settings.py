# Settings UI

import streamlit as st
from utils.auth import store_keys


def render_settings():
    """ """
    st.text("API key \nand Assistant ID")
    api_key = st.text_input(
        label="Enter your OpenAI API key",
        placeholder="OpenAI API Key",
        type="password",
        help="Go to [OpenAI API key](https://platform.openai.com/api-keys) for platform authentication.",
    )
    if api_key:
        st.session_state.openai_api_key = api_key
        st.session_state.key_set = True

    if st.session_state.assistant_mode == "On":
        assistant_key = st.text_input(
            label="Enter your OpenAI Assistant ID",
            placeholder="OpenAI Assistant ID",
            type="password",
            help="Go to [OpenAI Assistant ID](https://platform.openai.com/assistants/) create custom Assistant ID.",
        )

        if assistant_key:
            st.session_state.openai_assistant_id = assistant_key
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
                    "OPENAI_API_KEY": st.session_state.openai_api_key,
                    "OPENAI_ASSISTANT_ID": st.session_state.openai_assistant_id,
                }
            )
            st.session_state.key_set = False
            st.rerun()

            if st.session_state.authenticated_flag:
                st.toast(":old_key: Authorized")
            else:
                st.toast(":confounded: Not Authorized!")
