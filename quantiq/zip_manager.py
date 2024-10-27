import os
import zipfile
import logging
import streamlit as st
from collections import defaultdict
import re
import shutil
import spacy
from rapidfuzz import fuzz
import subprocess
import sys


def ensure_spacy_model(model_name='en_core_web_sm'):
    """
    Ensures that the specified spaCy model is installed.
    If not installed, it downloads the model using a subprocess.
    
    Parameters:
    - model_name (str): The name of the spaCy model to ensure.
    """
    try:
        spacy.load(model_name)
        logging.info(f"spaCy model '{model_name}' is already installed.")
    except OSError:
        logging.warning(f"spaCy model '{model_name}' not found. Installing...")
        st.info(f"spaCy model '{model_name}' not found. Installing...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", model_name])
            logging.info(f"Successfully installed spaCy model '{model_name}'.")
            st.success(f"Successfully installed spaCy model '{model_name}'.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install spaCy model '{model_name}': {e}")
            st.error(f"""Failed to install spaCy model '{
                     model_name}'. Please install it manually.""")
            raise e


def sanitize_folder_name(name):
    """
    Sanitizes the folder name by removing or replacing characters not allowed in file system names.
    
    Parameters:
    - name (str): The folder name to sanitize.
    
    Returns:
    - str: A sanitized folder name.
    """
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


def get_representative_company_name(names):
    """
    Determines a representative company name for a cluster based on the most common names.
    
    Parameters:
    - names (list): A list of company names extracted from filenames.
    
    Returns:
    - str: A representative company name for the cluster.
    """
    name_counts = defaultdict(int)
    for name in names:
        name_counts[name] += 1
    sorted_names = sorted(name_counts.items(),
                          key=lambda item: (-item[1], item[0]))
    return sorted_names[0][0] if sorted_names else 'Cluster'


def organize_files_with_ner(files, output_dir, similarity_threshold=80, nlp=None):
    """
    Organizes a list of files into directories based on company names extracted using NER.
    
    Parameters:
    - files (list): List of file paths to organize.
    - output_dir (str): The directory where organized folders will be created.
    - similarity_threshold (int): The minimum similarity score to consider company names as similar (0-100).
    - nlp (spacy.lang): The spaCy language model.
    """
    company_names = []
    base_names = [os.path.basename(f) for f in files]

    # Extract company names using NER
    for name in base_names:
        # Remove file extension
        name_without_ext = os.path.splitext(name)[0]
        doc = nlp(name_without_ext)
        orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        if orgs:
            company_name = ' '.join(orgs)
        else:
            # Fallback to regex to extract capitalized words at the start
            match = re.match(r'^((?:[A-Z][\w&]*\s?)+)', name_without_ext)
            company_name = match.group(
                1).strip() if match else name_without_ext
        company_names.append(company_name)

    # Initialize clusters
    clusters = []
    clustered = [False] * len(company_names)

    for i, name_i in enumerate(company_names):
        if clustered[i]:
            continue
        # Start a new cluster
        cluster = [i]
        clustered[i] = True
        for j in range(i + 1, len(company_names)):
            if clustered[j]:
                continue
            # Compute similarity score between company names
            score = fuzz.token_set_ratio(name_i, company_names[j])
            if score >= similarity_threshold:
                cluster.append(j)
                clustered[j] = True
        clusters.append(cluster)

    # Create folders and move files
    for idx, cluster in enumerate(clusters):
        # Determine a representative company name for the cluster
        cluster_company_names = [company_names[i] for i in cluster]
        company_name = get_representative_company_name(cluster_company_names)
        # Sanitize the company_name for use as a folder name
        company_name = sanitize_folder_name(company_name)
        group_folder = os.path.join(output_dir, company_name)
        os.makedirs(group_folder, exist_ok=True)
        for i in cluster:
            src_file = files[i]
            dst_file = os.path.join(group_folder, os.path.basename(src_file))
            try:
                shutil.move(src_file, dst_file)
                logging.info(f"Moved '{src_file}' to '{dst_file}'.")
                # st.toast(f"Moved '{os.path.basename(src_file)}' to '{
                #          company_name}' folder.")
            except Exception as e:
                logging.error(f"""Failed to move '{
                              src_file}' to '{dst_file}': {e}""")
                st.error(f"""Failed to move '{os.path.basename(
                    src_file)}' to '{company_name}' folder.""")


def handle_zipped_files(uploaded_file):
    """
    Handle uploaded zip file, extracting its contents to the bulk directory.
    If subdirectories exist, they are preserved.
    Root-level files are sorted into directories using NER.
    
    Parameters:
    - uploaded_file: The uploaded zip file object.
    
    Returns:
    - dict: A dictionary mapping relative directory paths to lists of file paths.
    """
    temp_zip_path = "temp.zip"
    temp_extract_dir = "temp_extract_dir"

    try:
        # Ensure spaCy model is installed
        ensure_spacy_model('en_core_web_sm')

        # Load spaCy model
        nlp = spacy.load('en_core_web_sm')
        logging.info("spaCy model loaded successfully.")

        # Save the uploaded zip file temporarily
        with open(temp_zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(f"Temp zip file created at '{temp_zip_path}'.")
        # st.info("Uploaded zip file saved temporarily.")

        # Extract all contents to a temporary directory
        with zipfile.ZipFile(temp_zip_path, 'r') as z:
            z.extractall(temp_extract_dir)
        logging.info(f"""Files extracted to temporary directory '{
                     temp_extract_dir}'.""")
        # st.info("Files extracted to temporary directory.")

        # List all files and directories in the extracted content
        root_files = []
        subdirectories = []
        for item in os.listdir(temp_extract_dir):
            item_path = os.path.join(temp_extract_dir, item)
            if os.path.isfile(item_path):
                root_files.append(item_path)
            elif os.path.isdir(item_path):
                subdirectories.append(item_path)

        # Create the bulk directory if it doesn't exist
        os.makedirs(st.session_state.bulk_dir, exist_ok=True)
        logging.info(f"Bulk directory '{st.session_state.bulk_dir}' is ready.")
        # st.info("Bulk directory is ready.")

        # Move subdirectories to the bulk directory
        for subdir in subdirectories:
            dst_dir = os.path.join(
                st.session_state.bulk_dir, os.path.basename(subdir))
            try:
                shutil.move(subdir, dst_dir)
                logging.info(f"Moved subdirectory '{subdir}' to '{dst_dir}'.")
                # st.toast(f"Moved subdirectory '{os.path.basename(subdir)}'.")
            except Exception as e:
                logging.error(f"""Failed to move subdirectory '{
                              subdir}' to '{dst_dir}': {e}""")
                st.error(f"""Failed to move subdirectory '{
                         os.path.basename(subdir)}'.""")

        # If there are root-level files, organize them using NER
        if root_files:
            logging.info("Organizing root-level files using NER.")
            # st.info("Organizing root-level files based on company names.")
            organize_files_with_ner(
                root_files, st.session_state.bulk_dir, nlp=nlp)
        else:
            logging.info("No root-level files to organize.")
            # st.info("No root-level files found to organize.")

        st.success("Files successfully ingested.")
        st.subheader("Ingested Files:")

        # Iterate through directories and group files by subdirectory
        all_subdirectories = {}
        for root, dirs, files in os.walk(st.session_state.bulk_dir):
            if files:
                relative_dir = os.path.relpath(root, st.session_state.bulk_dir)
                all_subdirectories[relative_dir] = [
                    os.path.join(root, file) for file in files]
                # st.toast(f"Found {len(files)} files in '{relative_dir}'")
                logging.debug(f"Found {len(files)} files in '{relative_dir}'.")

        # Clean up temporary files and directories
        try:
            os.remove(temp_zip_path)
            logging.info(f"Temporary zip file '{temp_zip_path}' deleted.")
            shutil.rmtree(temp_extract_dir)
            logging.info(f"""Temporary extraction directory '{
                         temp_extract_dir}' deleted.""")
        except Exception as e:
            logging.warning(f"Failed to clean up temporary files: {e}")
            st.warning("Failed to clean up some temporary files.")

        return all_subdirectories

    except Exception as e:
        logging.error(f"Error handling zip file: {e}")
        st.error(f"Error processing files: {e}")
        return None
