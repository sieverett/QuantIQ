# quantiq/analysis.py

import os
import logging
import streamlit as st
from anthropic import Anthropic
from quantiq.reporting import output_report
from quantiq.file_handler import ingest_files
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def quantiq_analysis(client, file_paths, report_name):
    """
    Analyze one or multiple files using the Anthropic client and prepare a report.

    Parameters:
    - client: Anthropic client instance.
    - file_paths: List of file paths to process.
    - report_name: Name to use in the report and output filename.

    Returns:
    - str: Content of the analysis report.
    """
    try:
        # Extract text content from all files
        report_data = ingest_files(file_paths)

        prompt_instructions = st.session_state.get("editor_content", "")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=prompt_instructions if prompt_instructions else "You are a financial analyst. Prepare comprehensive reports based on the provided financial documents.",
            messages=[
                {
                    "role": "user",
                    "content": f"Please prepare a comprehensive report for {report_name} based on the following document data:\n\n{report_data}",
                },
            ],
        )

        message_content = response.content[0].text
        logger.debug(f"Received message content: {message_content[:100]}...")
        logger.info(
            f"Analysis completed for files: {', '.join([os.path.basename(fp) for fp in file_paths])}"
        )
        return message_content

    except Exception as e:
        logger.error(f"Error in quantiq_analysis function: {e}")
        return None


def quantiq_analysis_(client, file_paths, report_name):
    """
    Alternate analysis function using prompts.

    Parameters:
    - client: Anthropic client instance.
    - file_paths: List of file paths to process.
    - report_name: Name to use in the report and output filename.

    Returns:
    - str: Content of the analysis report.
    """
    try:
        prompt_instructions = st.session_state.editor_content
        report_data = ingest_files(file_paths)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=prompt_instructions,
            messages=[
                {
                    "role": "user",
                    "content": f"Company: {report_name}. Report data:" + report_data,
                },
            ],
        )

        result = response.content[0].text
        return result

    except Exception as e:
        logger.error(f"Error in quantiq_analysis_ function: {e}")
        return None
