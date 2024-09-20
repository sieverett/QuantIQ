import os
import sys
import streamlit as st
from docx import Document
from markdown_pdf import MarkdownPdf, Section
import pandas as pd
import zipfile
from weasyprint import HTML
import logging
from logging.handlers import RotatingFileHandler


def set_logging():
    # Set up a rotating file handler with max file size and backup count
    log_file_handler = RotatingFileHandler(
        "quantiq_analysis.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB max file size
        backupCount=1  # Keep up to 3 backup log files
    )

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            log_file_handler,  # Rotating file handler
            logging.StreamHandler()  # Output logs to console
        ]
    )
    return logging


def handle_file_upload(uploaded_file, upload_dir):
    """
    Handle the uploaded file, saving it to the specified directory.
    """
    try:
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(
            f"File {uploaded_file.name} uploaded successfully to {file_path}.")
        return file_path
    except Exception as e:
        st.error(f"Error uploading file {uploaded_file.name}: {e}")
        logging.error(f"Error uploading file {uploaded_file.name}: {e}")
        return None


def handle_zipped_files(uploaded_file):
    """
    Handle uploaded zip file, extracting its contents to the bulk directory.
    """
    temp_file_path = os.path.join("temp.zip")
    try:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(f"Temp zip file created at {temp_file_path}.")

        with zipfile.ZipFile(temp_file_path, 'r') as z:
            z.extractall(st.session_state.bulk_dir)
        st.success("Files successfully extracted")
        logging.info(f"Files extracted to {st.session_state.bulk_dir}.")

        st.subheader("Extracted Files:")
        for root, dirs, files in os.walk(st.session_state.bulk_dir):
            for file in files:
                st.toast(os.path.join(root, file))
                logging.debug(f"Extracted file: {os.path.join(root, file)}")

        os.remove(temp_file_path)
        logging.info(f"Temp zip file {temp_file_path} deleted.")
    except Exception as e:
        logging.error(f"Error handling zip file: {e}")
        st.error(f"Error extracting files: {e}")


def oai_file_mgr(client, show=False, delete_vsf=False, delete_vss=False, delete_files=False):
    """
    Manage files in the OAI client, listing, deleting vector stores or files as needed.
    """
    vsl, l = [], []
    try:
        logging.debug("Starting file management operations.")
        for vs in client.beta.vector_stores.list().data:
            if vs.file_counts.completed > 0:
                if show:
                    logging.info(
                        f"Available vector store: {vs.id} - {vs.name}")
                res = client.beta.vector_stores.files.list(vs.id)
                for d in res.data:
                    vsl.append((d.id, d.vector_store_id, d))
                    if delete_vsf and d:
                        client.beta.vector_stores.files.delete(
                            vector_store_id=vs.id, file_id=d.id)
                        logging.info(f"Deleted vector store file: {d.id}")
                if delete_vss:
                    client.beta.vector_stores.delete(vs.id)
                    logging.info(f"Deleted vector store: {vs.id} - {vs.name}")

        # Process client files
        for fid in client.files.list().data:
            if show:
                logging.info(f"File in OAI: {fid.id} - {fid.filename}")
            if delete_files:
                client.files.delete(fid.id)
                logging.info(f"Deleted file: {fid.id} - {fid.filename}")
            else:
                l.append((fid.filename, fid.id))

        df = pd.DataFrame(vsl, columns=['fid', 'vs_id', 'vs_metadata']).merge(
            pd.DataFrame(l, columns=['filename', 'fid'])
        )
        logging.info("File management operation completed successfully.")
        return df[["vs_id", "fid", "filename", "vs_metadata"]]

    except Exception as e:
        logging.error(f"Error in file manager: {e}")
        return pd.DataFrame()


def markdown_to_pdf(report_text, filename, output_dir):
    """Completion text is directly converted to pdf"""
    st.session_state.file_counter += 1
    save_path = os.path.join(output_dir, filename.replace(
        ".pdf", "_quantiq_analysis")+".pdf")
    abs_string = os.path.abspath("../imgs/quantiq_logo_75x75.svg")
    print(abs_string)
    report_text = f"![Alt text]({abs_string})\n"+report_text
    pdf = MarkdownPdf()
    pdf.add_section(Section(report_text, toc=False))
    pdf.save(save_path)
    print(f"analysis saved as {save_path}")


def add_style(html_content):
    """
    Function to add styling to the given HTML content and return the updated content.
    """
    try:
        style = """
            <html>
            <head>
            <style>
                /* Global Styles */
                body {
                    font-family: Arial, Helvetica, sans-serif;
                    margin: 40px;
                    color: #333333;
                }
                /* Header Styles */
                header {
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #eaeaea;
                }
                h1 {
                    font-size: 24px;
                    color: #1a1a1a;
                }
                h2 {
                    font-size: 20px;
                    color: #1a1a1a;
                }
                /* Table Styling */
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                table, th, td {
                    border: 1px solid #cccccc;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                /* Alternating row colors for readability */
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                /* Footer Styles */
                footer {
                    text-align: center;
                    margin-top: 40px;
                    font-size: 12px;
                    color: #777777;
                }
            </style>
            """
        # Extract the HTML content within the code block
        logging.debug("Extracting HTML content.")
        html_content = html_content.split("```")[1]
        # Log first 100 characters for brevity
        logging.debug(f"Split HTML content: {html_content}...")

        # Replace unwanted HTML tags and add the style
        html_content = html_content.replace("html\n<!DOCTYPE html>\n", "")
        logo = fetch_logo()
        html_content = logo + html_content.replace('<html>\n<head>\n', style)
        logging.info(f"Logo info: {logo}...")
        logging.info(f"Parsed HTML content: {html_content}...")
        logging.info("HTML content styled successfully.")
        return html_content

    except Exception as e:
        logging.error(f"Error in add_style function: {e}")
        return None


def fetch_logo():
    if 'linux' in sys.platform:
        # abs_string = os.path.abspath("../imgs/quantiq_logo_75x75.svg")
        logo = '<img src="file:///app/imgs/quantiq_logo_75x75.svg" alt="Logo">'
        # logo = '<p><img src="/app/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
    else:
        logo = '<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
    return logo


def html_to_pdf(html_content, filename, output_dir):
    """
    Convert HTML content to a PDF and save it to the specified output directory.
    """
    try:
        # Add styling to the HTML content
        logging.debug(f"Converting HTML content to PDF for {filename}.")
        string = add_style(html_content)

        if string is None:
            raise ValueError(
                "Styled HTML content is None. Skipping PDF generation.")

        # Define the save path for the PDF file
        save_path = os.path.join(output_dir, filename)

        # Generate the PDF from the HTML content
        HTML(string=string).write_pdf(save_path)

        logging.info(f"PDF generated and saved at {save_path}.")

    except Exception as e:
        logging.error(f"Error in html_to_pdf function: {e}")


def quantiq_analysis(client, filename, input_dir=None):
    """
    Analyze the file using the OpenAI client and prepare a report.
    """
    try:

        assistant_id = st.session_state.openai_assistant_id

        logging.debug(f"Assistant ID: {assistant_id}")

        # Check if input_dir is provided
        if input_dir is None:
            raise ValueError("Input directory is not provided")

        logging.debug(f"Input directory: {input_dir}")

        # Build file path
        input_filepath = os.path.join(input_dir, filename)
        logging.debug(f"Input file path: {input_filepath}")

        # Upload the file
        with open(input_filepath, "rb") as file:
            message_file = client.files.create(file=file, purpose="assistants")
        logging.info(
            f"File {filename} uploaded successfully. File ID: {message_file.id}")
        # Create thread with file attachment
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "prepare a report",
                    "attachments": [
                        {"file_id": message_file.id, "tools": [
                            {"type": "file_search"}]}
                    ],
                }
            ]
        )
        logging.info(f"Thread created with ID: {thread.id}")

        # Poll the thread run

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant_id
        )
        logging.info(f"Run created and polled successfully. Run ID: {run.id}")

        # Retrieve messages
        messages = list(client.beta.threads.messages.list(
            thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text
        # Log part of the content
        logging.info(f"Received message content: {message_content}...")

        # Extract annotations
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")
                logging.debug(f"Citation found: {cited_file.filename}")

        logging.info(f"Analysis completed for file {filename}")
        return message_content, citations

    except Exception as e:
        logging.error(f"Error in quantiq_analysis function: {e}")
        return None, []


def download_file(file_selected):
    # File path
    file_path = os.path.join(st.session_state.output_dir, file_selected)
    with open(file_path, "rb") as file:
        file_data = file.read()
    # Read the file
    if ".docx" in file_path:
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ".pdf" in file_path:
        mime_type = "application/pdf"
    else:
        mime_type = "application/zip"
    # Create a download button in the Streamlit app
    st.download_button(
        label="Download file",
        data=file_data,
        file_name=file_path,
        mime=mime_type
    )


def zipdir(bulk_output_dir=None):
    files = [f for f in os.listdir(bulk_output_dir) if f.endswith(".pdf")]
    zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = os.path.join(bulk_output_dir, file)
            # Add file to zip without including the directory structure
            zipf.write(file_path, arcname=file)


def download_zip_file(bulk_output_dir=None):
    with open(os.path.join(bulk_output_dir, "quantiq_results.zip"), "rb") as f:
        bytes = f.read()
        btn = st.download_button(
            label="Download Zip File",
            data=bytes,
            file_name="quantiq_results.zip",
            mime="application/pdf",
            on_click=reset_run
        )
        if btn:
            st.success("Downloaded")


def delete_dir_contents():
    try:
        old_zip_file = os.path.join(
            st.session_state.bulk_output_dir, "quantiq_results.zip")
        os.remove(old_zip_file)
    except OSError:
        pass

    dirs = [st.session_state.output_dir, st.session_state.bulk_dir,
            st.session_state.bulk_output_dir]
    for dir_ in dirs:
        for file in os.listdir(dir_):
            file_path = os.path.join(dir_, file)
            print("deleting", file_path)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)


def reset_run():
    delete_dir_contents()
    st.session_state.bulk_file_uploaded = False
    st.query_params.clear()
    st.session_state.reset_clicked = True


def feedback():
    sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
    selected = st.feedback("thumbs")
    print(selected)
    if selected is not None:
        st.markdown(f"You selected: {sentiment_mapping[selected]}")
