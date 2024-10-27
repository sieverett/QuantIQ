# quantiq/download_manager.py

import os
import zipfile
import shutil
import streamlit as st
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def download_file(file_selected, output_dir):
    """
    Provides a download button for a specific file.

    Args:
        file_selected (str): Name of the file to download.
        output_dir (str): Directory where the file is located.
    """
    try:
        file_path = os.path.join(output_dir, file_selected)
        with open(file_path, "rb") as file:
            file_data = file.read()

        # Determine the MIME type based on the file extension
        if file_selected.lower().endswith(".docx"):
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_selected.lower().endswith(".pdf"):
            mime_type = "application/pdf"
        else:
            mime_type = "application/octet-stream"

        # Create a download button in the Streamlit app
        st.download_button(
            label="Download file",
            data=file_data,
            file_name=file_selected,
            mime=mime_type,
        )
        logger.info(f"Download button created for file: {file_selected}")

    except Exception as e:
        st.error(f"Error downloading file {file_selected}: {e}")
        logger.error(f"Error downloading file {file_selected}: {e}")


def zipdir(bulk_output_dir):
    """
    Zips all PDF files in the specified directory.

    Args:
        bulk_output_dir (str): Directory containing PDF files to zip.
    """
    try:
        files = [f for f in os.listdir(bulk_output_dir) if f.endswith(".pdf")]
        zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")

        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(bulk_output_dir, file)
                zipf.write(file_path, arcname=file)
        logger.info("Output files zipped successfully.")
    except Exception as e:
        logger.error(f"Error zipping files: {e}")


def download_zip_file(bulk_output_dir, reset_run_callback):
    """
    Provides a download button for the zipped analysis results.

    Args:
        bulk_output_dir (str): Directory containing analysis PDF files.
        reset_run_callback (function): Callback function to reset the run after download.
    """
    try:
        if len([i for i in os.listdir(bulk_output_dir) if not i.endswith(".zip")]) > 0:
            zipdir(bulk_output_dir)
            logger.info("Output files zipped successfully.")
            zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")
            with open(zip_file_path, "rb") as f:
                bytes_data = f.read()
            btn = st.download_button(
                label="Download Analysis Results",
                type="primary",
                data=bytes_data,
                file_name="quantiq_results.zip",
                mime="application/zip",
                on_click=reset_run_callback,
                use_container_width=True,
            )
            if btn:
                st.success("Downloaded")
                logger.info("Analysis results downloaded and run reset triggered.")
    except Exception as e:
        st.error(f"Error downloading ZIP file: {e}")
        logger.error(f"Error downloading ZIP file: {e}")
