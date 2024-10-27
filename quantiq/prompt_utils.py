import streamlit as st
from openai import OpenAI
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


def get_output_format():
    with open('prompts/output_format.txt', 'r') as file:
        output_format = file.read()
    return output_format


def get_current_prompt(method=None):
    try:
        with open('prompts/current.txt', 'r') as file:
            instructions = file.read()
        if method == 'output format only':
            return get_output_format()
        elif method == 'less output format':
            return instructions
        else:
            return instructions+get_output_format()
    except Exception as e:
        logging.error(f"Error getting current prompt: {e}")
        st.error(
            "Error getting current prompt. Please check your OpenAI API key and Assistant ID.")
        return 'Error'


def set_current_prompt(instructions):
    with open('prompts/current.txt', 'w') as file:
        file.write(instructions)
    return instructions


def get_default_prompt(method=None):
    with open('prompts/backup.txt', 'r') as file:
        instructions = file.read()
    if method == 'output format only':
        return get_output_format()
    elif method == 'less output format':
        return instructions
    else:
        return instructions + get_output_format()


def set_assistant_instructions(instructions):
    client = OpenAI(api_key=st.session_state.openai_api_key)
    my_updated_assistant = client.beta.assistants.update(
        st.session_state.openai_assistant_id,
        instructions=instructions
    )
    st.toast("Assistant updated successfully!")


def get_assistant_instructions():
    try:
        assistant = get_assistant()
        instructions = assistant.instructions
        return instructions
    except Exception as e:
        logging.error(f"Error getting assistant instructions: {e}")
        st.error(
            "Error getting assistant instructions. Please check your OpenAI API key and Assistant ID.")
        return 'Error'
