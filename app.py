# app.py

import os
import streamlit as st
from utils.session import initialize_session_state
from components.sidebar import render_sidebar
from components.analyzer import render_analyzer
from components.prompt_editor import render_prompt_editor
from components.settings import render_settings
from quantiq import (
    set_logging,
    quantiq_analysis,
    quantiq_analysis_,
    output_report,
    output_report_,
    download_zip_file,
    reset_run,
    feedback,
)
from quantiq.logo_manager import render_logo
from quantiq.download_manager import download_file
from quantiq import prompt_utils as pu

# Import custom modules
from quantiq.logging_setup import set_logging

# Set logging
logger = set_logging()

# Set page config
st.set_page_config(
    page_title="QUANT-IQ: Quantitative Analysis Tool for Intelligent Financial Review",
    layout="wide",
    page_icon="cyclone",
    menu_items={
        'Get Help': 'https://sieverett.github.io/QuantIQ/FAQ.html',
        'Report a bug': 'https://github.com/sieverett/QuantIQ/issues/new',
        'About': """
            ## About QUANT-IQ
            **QUANT-IQ** is a powerful tool designed to streamline the analysis of financial statements using AI.
            With a user-friendly interface, the app supports document uploads in PDF, DOCX, and ZIP formats, and
            leverages OpenAI's GPT to generate insightful reports. Whether for individual documents or bulk processing,
            QUANT-IQ simplifies financial analysis for both professionals and organizations.

            **Author**: Silas Everett
            **GitHub**: [sieverett.github.io](https://sieverett.github.io)
        """
    },
    initial_sidebar_state="expanded"
)

# Apply custom CSS
if os.path.exists("styles/custom.css"):
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    logger.warning("Custom CSS file not found at 'styles/custom.css'.")

# Initialize session state variables
defaults = {
    "img_dir": "imgs",
    "chat_history": [],
    "bulk_file_uploaded": False,
    "thread_id": None,
    "bulk_dir": "bulk",
    "output_dir": "output",
    "file_counter": 0,
    "reset_clicked": False,
    "uploaded_files": [],
    "bulk_output_dir": "bulk_output",
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_assistant_id": os.getenv("OPENAI_ASSISTANT_ID", ""),
    "authenticated_flag": False,
    "key_set": True,
    "editor_content": pu.get_default_prompt(
        "prompts/default_prompt.txt"
    ),  # Initialize as empty; will be set in prompt editor
    "default_prompt": pu.get_default_prompt(
        "prompts/default_prompt.txt"
    ),  # Initialize as empty; will be loaded from prompts/default_prompt.txt
    "assistant_instructions": "",
    "current_logo": "quantiq_logo_75x75.jpg",
    "logo_clicked": None,
    "assistant_mode": "Off",
}

initialize_session_state(defaults)

# Handle query parameters if needed
if "logo_clicked" not in st.query_params:
    st.query_params["logo_clicked"] = None

# Ensure necessary directories exist
os.makedirs(st.session_state.bulk_dir, exist_ok=True)
os.makedirs(st.session_state.output_dir, exist_ok=True)
os.makedirs(st.session_state.bulk_output_dir, exist_ok=True)
os.makedirs(st.session_state.img_dir, exist_ok=True)

# Render Sidebar and get selected menu
selected = render_sidebar()

# Render main content based on selection
if selected == "Settings":
    render_settings()
elif selected == "Analyze":
    render_analyzer()
elif selected == "Prompt":
    render_prompt_editor()
