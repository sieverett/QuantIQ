# components/prompt_editor.py

import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_quill import st_quill
import time
import io
from quantiq import prompt_utils as pu
import os


def render_prompt_editor():
    """
    Renders the Prompt Editor section.
    """
    st.subheader(
        "Prompt Editor",
        help="Edit the default prompt for the AI assistant.\nClick 'Save' to update the AI Assistant.",
    )

    # Prompt Editor Tabs
    selected2 = option_menu(
        None,
        ["Edit", "Save", "Download", "Restore"],
        icons=["list-task", "robot", "cloud-download", "reply"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected2 == "Edit":
        with st.expander("Prompt", expanded=True):
            # Quill editor that allows the user to edit the content
            with st.container():
                current_content = st_quill(
                    toolbar=[
                        ["bold", "italic", "underline"],
                        ["link", "blockquote", "code-block"],
                    ],
                    value=st.session_state.editor_content,
                    key="quill",
                )

                if st.session_state.editor_content != current_content:
                    st.session_state.editor_content = current_content

    update_success = st.empty()

    if selected2 == "Save":
        if st.session_state.assistant_mode == "On":
            if (
                st.session_state.assistant_instructions
                != st.session_state.editor_content + pu.get_output_format()
            ):
                epoch_time = int(time.time())
                file_name = f"quantiq_prompt_{epoch_time}.txt"
                os.makedirs("prompts/prompt_logs", exist_ok=True)
                with open(f"prompts/prompt_logs/{file_name}", "w") as file:
                    file.write(st.session_state.editor_content)
                pu.set_assistant_instructions(
                    instructions=st.session_state.editor_content
                    + pu.get_output_format()
                )
                st.session_state.assistant_instructions = (
                    st.session_state.editor_content + pu.get_output_format()
                )
                update_success.success("Assistant updated successfully!")
        elif st.session_state.editor_content == pu.get_current_prompt(
            "less output format"
        ):
            update_success.warning("No changes to save.")
        else:
            pu.set_current_prompt(st.session_state.editor_content)
            update_success.success("Prompt saved successfully.")

    if selected2 == "Restore":

        if st.session_state.editor_content != st.session_state.default_prompt:
            current_content = st.session_state.default_prompt
            st.session_state.editor_content = st.session_state.default_prompt
            pu.set_current_prompt(st.session_state.default_prompt)

            if st.session_state.assistant_mode == "On":
                pu.set_assistant_instructions(
                    instructions=st.session_state.default_prompt
                    + pu.get_output_format()
                )

            st.toast("Default prompt restored.")
            selected2 = "Edit"
            st.rerun()
        else:
            st.toast("Default prompt is active.")

    if selected2 == "Download":
        # Link to download the current prompt
        epoch_time = int(time.time())
        filename = f"quantiq_prompt_{epoch_time}.txt"
        # buffer = io.StringIO(st.session_state.editor_content)
        # trigger_download(buffer.getvalue(), file_name)
        content = pu.get_current_prompt()
        st.download_button(
            label="**Download Current Prompt**",
            data=content,
            type="primary",
            use_container_width=True,
        )
