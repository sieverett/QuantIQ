# quantiq/dcf.py

import os
import streamlit as st
from quantiq.file_handler import ingest_files
from quantiq.reporting import html_to_pdf
from quantiq.logging_setup import set_logging

logger = set_logging()


def _collect_files(bulk_dir):
    """Collect all processable files from bulk_dir and its subdirectories."""
    all_files = []
    for root, dirs, files in os.walk(bulk_dir):
        for f in files:
            if f.endswith((".pdf", ".docx", ".xlsx", ".csv")):
                all_files.append(os.path.join(root, f))
    return all_files


def _load_prompt(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return ""


def run_dcf_analysis(client):
    bulk_dir = st.session_state.bulk_dir
    output_dir = st.session_state.bulk_output_dir

    file_paths = _collect_files(bulk_dir)
    if not file_paths:
        st.error("No processable files found for DCF analysis.")
        return

    # Determine company name from first subdirectory or default
    subdirs = [d for d in os.listdir(bulk_dir) if os.path.isdir(os.path.join(bulk_dir, d))]
    company_name = subdirs[0] if subdirs else "Company"

    st.text(f"Extracting financials for: {company_name}")
    document_text = ingest_files(file_paths)

    extraction_prompt = _load_prompt("prompts/dcf_extraction.txt")
    dcf_model_prompt = _load_prompt("prompts/dcf_model.txt")

    # Turn 1: Extract structured financials
    messages = [
        {
            "role": "user",
            "content": f"Extract structured financial data for {company_name} from the following documents:\n\n{document_text}",
        }
    ]

    response_1 = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=extraction_prompt,
        messages=messages,
    )

    extraction_html = response_1.content[0].text
    logger.info(f"Financial extraction complete for {company_name}")

    # Turn 2: Build DCF model using extracted data
    st.text(f"Building DCF model for: {company_name}")

    messages.append({"role": "assistant", "content": extraction_html})
    messages.append({
        "role": "user",
        "content": "Using the financial data you just extracted, build a complete DCF valuation model. Include all calculations, assumptions, and sensitivity analysis.",
    })

    response_2 = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=dcf_model_prompt,
        messages=messages,
    )

    dcf_html = response_2.content[0].text
    logger.info(f"DCF model complete for {company_name}")

    # Combine extraction + DCF into single PDF
    combined_html = f"<h1>{company_name} — Financial Data Extraction</h1>\n"
    combined_html += extraction_html
    combined_html += '<div class="page-break"></div>\n'
    combined_html += f"<h1>{company_name} — DCF Valuation Model</h1>\n"
    combined_html += dcf_html

    output_filename = f"{company_name}_dcf_valuation.pdf"
    html_to_pdf(combined_html, output_filename, output_dir)
    logger.info(f"DCF report generated: {output_filename}")
