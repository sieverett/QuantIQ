# components/analyzer.py

import os
import streamlit as st
from utils.file_handler import handle_file_upload
from anthropic import Anthropic
from quantiq.orchestrator import process_bulk_directory
from quantiq.utils import reset_run
from quantiq.download_manager import download_zip_file
import logging


def render_analyzer():
    st.subheader("Financial Statement Analyzer")

    mode = st.session_state.get("analysis_mode", "Standard")

    help_text = {
        "Standard": "Upload your documents to begin (.zip, .pdf or .docx)",
        "Comparative": "Upload a .zip with documents for 2+ companies to compare",
        "DCF Valuation": "Upload financial statements for a single company (.zip, .pdf or .docx)",
    }

    file_upload_box = st.empty()
    if not st.session_state["bulk_file_uploaded"]:
        st.session_state["files"] = file_upload_box.file_uploader(
            help_text.get(mode, help_text["Standard"]),
            accept_multiple_files=True,
            type=["zip", "pdf", "docx"],
            help="Start by uploading your financial documents in ZIP, PDF, or DOCX format.",
        )
        if not st.session_state.authenticated_flag:
            st.warning("Set your Anthropic API key in Settings to proceed.")
            st.stop()

        if st.session_state["files"]:
            for uploaded_file in st.session_state["files"]:
                handle_file_upload(uploaded_file, st.session_state.bulk_dir)
            st.session_state["bulk_file_uploaded"] = True
            st.write("Files uploaded successfully!")
            st.session_state["reset_clicked"] = False
            logging.info("All files uploaded and session state updated.")
            st.rerun()

    if st.session_state["bulk_file_uploaded"] and st.session_state["files"]:
        if st.button("Analyze", type="primary"):
            with st.spinner("Analyzing..."):
                client = Anthropic(api_key=st.session_state.anthropic_api_key)
                if mode == "Comparative":
                    from quantiq.comparative import run_comparative_analysis
                    run_comparative_analysis(client)
                elif mode == "DCF Valuation":
                    from quantiq.dcf import run_dcf_analysis
                    run_dcf_analysis(client)
                else:
                    process_bulk_directory(client)
            st.session_state.bulk_file_uploaded = False
            st.session_state["files"] = []
            st.session_state.reset_clicked = False
            st.success("Analysis complete!")

        col1, col2, buffer = st.columns([3, 3, 5])
        with col1:
            if (
                not st.session_state.reset_clicked
                and len(os.listdir(st.session_state.bulk_dir)) > 0
            ):
                if st.button("  Reset  ", type="secondary", use_container_width=True):
                    reset_run()
                    logging.info("Run reset and state cleared.")
                    st.rerun()
        with col2:
            download_zip_file(st.session_state.bulk_output_dir, reset_run)
