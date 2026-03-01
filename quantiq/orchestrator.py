import os
import streamlit as st
from quantiq.analysis import quantiq_analysis
from quantiq.reporting import add_style, html_to_pdf
from quantiq.download_manager import zipdir
from quantiq.logging_setup import set_logging

logger = set_logging()


def process_bulk_directory(client):
    bulk_dir = st.session_state.bulk_dir
    output_dir = st.session_state.bulk_output_dir

    subdirs = [
        d for d in os.listdir(bulk_dir)
        if os.path.isdir(os.path.join(bulk_dir, d))
    ]

    if not subdirs:
        files = [
            os.path.join(bulk_dir, f)
            for f in os.listdir(bulk_dir)
            if f.endswith((".pdf", ".docx", ".xlsx", ".csv"))
        ]
        if files:
            subdirs = [None]

    progress = st.progress(0)
    total = len(subdirs)

    for idx, subdir in enumerate(subdirs):
        if subdir is None:
            company_name = "Analysis"
            file_dir = bulk_dir
        else:
            company_name = subdir
            file_dir = os.path.join(bulk_dir, subdir)

        file_paths = [
            os.path.join(file_dir, f)
            for f in os.listdir(file_dir)
            if os.path.isfile(os.path.join(file_dir, f))
            and f.endswith((".pdf", ".docx", ".xlsx", ".csv"))
        ]

        if not file_paths:
            logger.warning(f"No processable files in {file_dir}")
            continue

        st.text(f"Analyzing: {company_name}")
        result = quantiq_analysis(client, file_paths, company_name)

        if result:
            output_filename = f"{company_name}_quantiq_analysis.pdf"
            html_to_pdf(result, output_filename, output_dir)
            logger.info(f"Generated report for {company_name}")

        progress.progress((idx + 1) / total)

    progress.empty()
    logger.info("Bulk processing complete.")
