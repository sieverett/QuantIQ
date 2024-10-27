# components/analyzer.py

import os
import streamlit as st
from utils.file_handler import handle_file_upload
from openai import OpenAI
from quantiq import quantiq__ as qiq
import logging


def render_analyzer():
    """
    Renders the Financial Statement Analyzer section.
    """
    st.subheader("Financial Statement Analyzer")

    # File Upload
    file_upload_box = st.empty()
    if not st.session_state["bulk_file_uploaded"]:
        st.session_state["files"] = file_upload_box.file_uploader(
            "Upload your documents to begin (.zip, .pdf or .docx)",
            accept_multiple_files=True,
            type=["zip", "pdf", "docx"],
            help="Start by uploading your financial documents in ZIP, PDF, or DOCX format.",
        )
        if st.session_state.authenticated_flag == False:
            st.warning(
                "Set your OpenAI API key and Assistant ID in Settings to proceed."
            )
            st.stop()

        # Process Uploaded Files
        if st.session_state["files"]:
            for uploaded_file in st.session_state["files"]:
                handle_file_upload(uploaded_file, st.session_state.bulk_dir)
            st.session_state["bulk_file_uploaded"] = True
            st.write("Files uploaded successfully!")
            st.session_state["reset_clicked"] = False
            logging.info("All files uploaded and session state updated.")
            st.rerun()

    # Analyze Files
    if st.session_state["bulk_file_uploaded"] and st.session_state["files"]:
        if st.button("Analyze", type="primary"):
            files_to_process = [
                f
                for f in os.listdir(st.session_state.bulk_dir)
                if f.endswith((".pdf", ".docx"))
            ]
            num_files = len(files_to_process)
            with st.spinner("Analyzing..."):
                client = OpenAI(api_key=st.session_state.openai_api_key)
                qiq.process_bulk_directory(client)
            st.session_state.bulk_file_uploaded = False
            st.session_state["files"] = []
            st.session_state.reset_clicked = False
            st.success("Analysis complete!")

        # Reset and Download Buttons
        col1, col2, buffer = st.columns([3, 3, 5])
        with col1:
            if (
                not st.session_state.reset_clicked
                and len(os.listdir(st.session_state.bulk_dir)) > 0
            ):
                if st.button("  Reset  ", type="secondary", use_container_width=True):
                    qiq.reset_run()
                    logging.info("Run reset and state cleared.")
                    st.rerun()
        with col2:
            qiq.download_zip_file()
