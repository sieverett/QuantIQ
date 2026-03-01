# utils/file_handler.py

import os
import logging
import streamlit as st
from quantiq import zip_manager as zm
from quantiq.file_handler import handle_file_upload as save_file


def handle_file_upload(uploaded_file, bulk_dir):
    if uploaded_file.type in ("application/x-zip-compressed", "application/zip"):
        zm.handle_zipped_files(uploaded_file)
        logging.info(f"Processed zipped file: {uploaded_file.name}")
    else:
        file_path = save_file(uploaded_file, bulk_dir)
        if file_path:
            logging.info(f"File {uploaded_file.name} uploaded successfully.")
        return file_path
