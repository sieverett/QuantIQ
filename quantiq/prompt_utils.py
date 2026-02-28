import streamlit as st
from anthropic import Anthropic
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
            "Error getting current prompt. Please check your Anthropic API key.")
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
    """Store instructions locally. No longer pushes to a remote assistant."""
    set_current_prompt(instructions)
    st.toast("Instructions updated successfully!")


def get_assistant_instructions():
    try:
        instructions = get_current_prompt()
        return instructions
    except Exception as e:
        logging.error(f"Error getting assistant instructions: {e}")
        st.error(
            "Error getting assistant instructions. Please check your Anthropic API key.")
        return 'Error'
