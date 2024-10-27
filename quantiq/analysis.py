# quantiq/analysis.py

import os
import logging
import streamlit as st
from openai import OpenAI
from quantiq.reporting import output_report, output_report_
from quantiq.file_handler import ingest_files
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def quantiq_analysis(client, file_paths, report_name):
    """
    Analyze one or multiple files using the OpenAI client and prepare a report.

    Parameters:
    - client: OpenAI client instance.
    - file_paths: List of file paths to process.
    - report_name: Name to use in the report and output filename.

    Returns:
    - str: Content of the analysis report.
    """
    try:
        assistant_id = st.session_state.openai_assistant_id

        # Upload all files and collect their file IDs
        attachments = []
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            logger.info(f"Sending file to vector store: {file_path}")

            # Upload the file
            if file_path.lower().endswith(".xlsx"):
                file = read_xlsx(file_path)
                txt_path = file_path.replace(".xlsx", ".txt")
                with open(txt_path, "w") as f:
                    f.write(file)
                with open(txt_path, "rb") as f:
                    message_file = client.files.create(file=f, purpose="assistants")
            else:
                with open(file_path, "rb") as file:
                    message_file = client.files.create(file=file, purpose="assistants")

            # Add the file ID to the attachments list
            attachments.append(
                {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
            )

        # Create thread with all file attachments
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Please prepare a comprehensive report for {report_name} based on the attached files.",
                    "attachments": attachments,
                }
            ]
        )
        logger.info(f"Thread created with ID: {thread.id}")

        # Poll the thread run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant_id
        )
        logger.debug(f"Run created and polled successfully. Run ID: {run.id}")

        # Retrieve messages
        messages = list(
            client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        )
        if messages:
            message_content = messages[0].content[0].text
            logger.debug(f"Received message content: {message_content[:100]}...")
            logger.info(
                f"Analysis completed for files: {', '.join([os.path.basename(fp) for fp in file_paths])}"
            )
            return message_content
        else:
            logger.error("No messages received from assistant.")
            return None

    except Exception as e:
        logger.error(f"Error in quantiq_analysis function: {e}")
        return None


def quantiq_analysis_(client, file_paths, report_name):
    """
    Alternate analysis function using prompts.

    Parameters:
    - client: OpenAI client instance.
    - file_paths: List of file paths to process.
    - report_name: Name to use in the report and output filename.

    Returns:
    - str: Content of the analysis report.
    """
    try:
        prompt_instructions = st.session_state.editor_content
        report_data = ingest_files(file_paths)

        # Assuming structured_outputs is defined elsewhere
        from quantiq.utils import structured_outputs

        ReportDataStructure = structured_outputs()

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": prompt_instructions},
                {
                    "role": "user",
                    "content": f"Company: {report_name}. Report data:" + report_data,
                },
            ],
            response_format=ReportDataStructure,
        )

        result = completion.choices[0].message
        return result

    except Exception as e:
        logger.error(f"Error in quantiq_analysis_ function: {e}")
        return None
