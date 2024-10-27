# quantiq/file_handler.py

import os
import zipfile
import shutil
import logging
import streamlit as st
from io import BytesIO
from PIL import Image
import PyPDF2
import docx
import pandas as pd
import csv
from bs4 import BeautifulSoup
import re
from markdown_pdf import MarkdownPdf, Section
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def handle_file_upload(uploaded_file, upload_dir):
    """
    Handle the uploaded file, saving it to the specified directory.

    Args:
        uploaded_file: The file uploaded by the user.
        upload_dir (str): Directory to save the uploaded file.

    Returns:
        str: Path to the saved file or None if failed.
    """
    try:
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"File {uploaded_file.name} uploaded successfully to {file_path}.")
        return file_path
    except Exception as e:
        st.error(f"Error uploading file {uploaded_file.name}: {e}")
        logger.error(f"Error uploading file {uploaded_file.name}: {e}")
        return None


def handle_zipped_files(uploaded_file, bulk_dir):
    """
    Handle uploaded zip file, extracting its contents to the bulk directory.
    If subdirectories exist, files in each subdirectory will be processed in batches.

    Args:
        uploaded_file: The zip file uploaded by the user.
        bulk_dir (str): Directory to extract files to.

    Returns:
        dict: Subdirectories with their respective files or None if failed.
    """
    temp_file_path = os.path.join("temp.zip")
    try:
        # Save the uploaded zip file temporarily
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"Temp zip file created at {temp_file_path}.")

        # Extract the zip file to the bulk directory
        with zipfile.ZipFile(temp_file_path, "r") as z:
            z.extractall(bulk_dir)
        st.success("Files successfully extracted")
        logger.info(f"Files extracted to {bulk_dir}.")

        st.subheader("Extracted Files:")

        # Iterate through directories and group files by subdirectory
        subdirectories = {}
        for root, dirs, files in os.walk(bulk_dir):
            if files:
                relative_dir = os.path.relpath(root, bulk_dir)
                subdirectories[relative_dir] = [
                    os.path.join(root, file) for file in files
                ]
                st.toast(f"Extracted {len(files)} files from {relative_dir}")
                logger.debug(f"Extracted {len(files)} files from {relative_dir}")

        os.remove(temp_file_path)
        logger.info(f"Temp zip file {temp_file_path} deleted.")

        return subdirectories

    except Exception as e:
        logger.error(f"Error handling zip file: {e}")
        st.error(f"Error extracting files: {e}")
        return None


def ingest_files(file_paths):
    """
    Reads and combines content from various file types.

    Args:
        file_paths (list): List of file paths to ingest.

    Returns:
        str: Combined content from all files.
    """
    combined_content = ""

    for file_path in file_paths:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".pdf":
            combined_content += read_pdf(file_path)
        elif file_extension == ".docx":
            combined_content += read_docx(file_path)
        elif file_extension == ".xlsx":
            combined_content += read_xlsx(file_path)
        elif file_extension == ".csv":
            combined_content += read_csv(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")

    return combined_content


def read_pdf(file_path):
    """
    Extracts text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text.
    """
    content = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                extracted_text = page.extract_text()
                if extracted_text:
                    content += extracted_text + "\n"
        logger.info(f"Extracted text from PDF: {file_path}")
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
    return content


def read_docx(file_path):
    """
    Extracts text from a DOCX file.

    Args:
        file_path (str): Path to the DOCX file.

    Returns:
        str: Extracted text.
    """
    try:
        doc = docx.Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
        logger.info(f"Extracted text from DOCX: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading DOCX {file_path}: {e}")
        return ""


def read_xlsx(file_path):
    """
    Extracts text from an XLSX file.

    Args:
        file_path (str): Path to the XLSX file.

    Returns:
        str: Extracted text.
    """
    try:
        excel_data = pd.read_excel(file_path)
        content = excel_data.to_string(index=False)
        logger.info(f"Extracted data from XLSX: {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error reading XLSX {file_path}: {e}")
        return ""


def read_csv(file_path):
    """
    Extracts text from a CSV file.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        str: Extracted text.
    """
    content = ""
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                content += ",".join(row) + "\n"
        logger.info(f"Extracted data from CSV: {file_path}")
    except Exception as e:
        logger.error(f"Error reading CSV {file_path}: {e}")
    return content


def delete_dir_contents(directories):
    """
    Deletes the contents of specified directories and recreates them.

    Args:
        directories (list): List of directory paths to refresh.
    """
    for dir_path in directories:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.info(f"Deleted directory: {dir_path}")
            os.makedirs(dir_path)
            logger.info(f"Recreated directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error deleting or recreating directory {dir_path}: {e}")
