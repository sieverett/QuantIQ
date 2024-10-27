# utils/file_handler.py

import os
import streamlit as st
from quantiq import zip_manager as zm
from quantiq import quantiq__ as qiq
import logging


def handle_file_upload(uploaded_file, bulk_dir):
    """
    Processes an uploaded file based on its type.

    Args:
        uploaded_file: The file uploaded by the user.
        bulk_dir (str): Directory to store uploaded files.

    Returns:
        str: Path to the saved file.
    """
    if uploaded_file.type == "application/x-zip-compressed":
        zm.handle_zipped_files(uploaded_file)
        logging.info(f"Processed zipped file: {uploaded_file.name}")
    else:
        file_path = qiq.handle_file_upload(uploaded_file, bulk_dir)
        if file_path:
            logging.info(f"File {uploaded_file.name} uploaded successfully.")
    return file_path
