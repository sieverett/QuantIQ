# quantiq/comparative.py

import os
import streamlit as st
from quantiq.analysis import quantiq_analysis
from quantiq.reporting import html_to_pdf
from quantiq.prompt_utils import get_prompt_for_mode
from quantiq.logging_setup import set_logging

logger = set_logging()


def run_comparative_analysis(client):
    bulk_dir = st.session_state.bulk_dir
    output_dir = st.session_state.bulk_output_dir

    subdirs = [
        d for d in os.listdir(bulk_dir)
        if os.path.isdir(os.path.join(bulk_dir, d))
    ]

    if len(subdirs) < 2:
        st.error("Comparative analysis requires documents for at least 2 companies. "
                 "Upload a .zip file with subdirectories per company, or multiple files "
                 "that will be auto-grouped by company name.")
        return

    # Pass 1: Individual analyses
    individual_results = {}
    progress = st.progress(0)
    total = len(subdirs)

    for idx, subdir in enumerate(subdirs):
        company_dir = os.path.join(bulk_dir, subdir)
        file_paths = [
            os.path.join(company_dir, f)
            for f in os.listdir(company_dir)
            if os.path.isfile(os.path.join(company_dir, f))
            and f.endswith((".pdf", ".docx", ".xlsx", ".csv"))
        ]
        if not file_paths:
            logger.warning(f"No files for {subdir}, skipping")
            continue

        st.text(f"Analyzing: {subdir} ({idx + 1}/{total})")
        result = quantiq_analysis(client, file_paths, subdir)
        if result:
            individual_results[subdir] = result

        progress.progress((idx + 1) / total)

    progress.empty()

    if len(individual_results) < 2:
        st.error("Could not analyze enough companies for comparison.")
        return

    # Pass 2: Comparative synthesis
    st.text("Generating comparative analysis...")
    comparative_prompt = get_prompt_for_mode("Comparative")

    companies_block = ""
    for company, analysis in individual_results.items():
        companies_block += f"\n\n--- {company} ---\n{analysis}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=comparative_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Compare the following {len(individual_results)} companies based on their individual analyses:{companies_block}",
            }
        ],
    )

    comparison_html = response.content[0].text

    # Build combined PDF: comparison summary + individual analyses with page breaks
    combined_html = comparison_html
    for company, analysis in individual_results.items():
        combined_html += f'<div class="page-break"></div>\n'
        combined_html += f"<h1>{company} — Individual Analysis</h1>\n"
        combined_html += analysis

    html_to_pdf(combined_html, "comparative_analysis.pdf", output_dir)
    logger.info("Comparative analysis complete.")
