import os
import streamlit as st
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
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
            return instructions + get_output_format()
    except Exception as e:
        logging.error(f"Error getting current prompt: {e}")
        st.error("Error getting current prompt. Please check your Anthropic API key.")
        return 'Error'


def set_current_prompt(instructions):
    with open('prompts/current.txt', 'w') as file:
        file.write(instructions)
    return instructions


def get_default_prompt(path=None):
    target = path if path and os.path.exists(path) else 'prompts/backup.txt'
    with open(target, 'r') as file:
        instructions = file.read()
    return instructions


def get_prompt_for_mode(mode):
    mode_files = {
        "Standard": "prompts/backup.txt",
        "Comparative": "prompts/comparative.txt",
        "DCF Valuation": "prompts/dcf_extraction.txt",
    }
    path = mode_files.get(mode, "prompts/backup.txt")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return get_default_prompt()


def set_assistant_instructions(instructions):
    set_current_prompt(instructions)
    st.toast("Instructions updated successfully!")


def get_assistant_instructions():
    try:
        return get_current_prompt()
    except Exception as e:
        logging.error(f"Error getting assistant instructions: {e}")
        st.error("Error getting assistant instructions.")
        return 'Error'
