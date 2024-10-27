from openai import OpenAI  # Ensure you have the OpenAI client imported
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
import shutil
from io import BytesIO
from PIL import Image
import base64
import re
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import csv
import docx
import PyPDF2
from pydantic import BaseModel
from typing import List


def set_logging():
    # Set up a rotating file handler with max file size and backup count
    log_file_handler = RotatingFileHandler(
        "quantiq_analysis.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB max file size
        backupCount=1,  # Keep up to 3 backup log files
    )

    # Set up logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            log_file_handler,  # Rotating file handler
            logging.StreamHandler(),  # Output logs to console
        ],
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
        logging.info(f"File {uploaded_file.name} uploaded successfully to {file_path}.")
        return file_path
    except Exception as e:
        st.error(f"Error uploading file {uploaded_file.name}: {e}")
        logging.error(f"Error uploading file {uploaded_file.name}: {e}")
        return None


def handle_zipped_files(uploaded_file):
    """
    Handle uploaded zip file, extracting its contents to the bulk directory.
    If subdirectories exist, files in each subdirectory will be processed in batches.
    """
    temp_file_path = os.path.join("temp.zip")
    try:
        # Save the uploaded zip file temporarily
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logging.info(f"Temp zip file created at {temp_file_path}.")

        # Extract the zip file to the bulk directory
        with zipfile.ZipFile(temp_file_path, "r") as z:
            z.extractall(st.session_state.bulk_dir)
        st.success("Files successfully extracted")
        logging.info(f"Files extracted to {st.session_state.bulk_dir}.")

        st.subheader("Extracted Files:")

        # Iterate through directories and group files by subdirectory
        subdirectories = {}
        for root, dirs, files in os.walk(st.session_state.bulk_dir):
            if files:
                relative_dir = os.path.relpath(root, st.session_state.bulk_dir)
                subdirectories[relative_dir] = [
                    os.path.join(root, file) for file in files
                ]
                st.toast(f"Extracted {len(files)} files from {relative_dir}")
                logging.debug(f"Extracted {len(files)} files from {relative_dir}")

        os.remove(temp_file_path)
        logging.info(f"Temp zip file {temp_file_path} deleted.")

        return subdirectories

    except Exception as e:
        logging.error(f"Error handling zip file: {e}")
        st.error(f"Error extracting files: {e}")
        return None


def oai_file_mgr(
    client, show=False, delete_vsf=False, delete_vss=False, delete_files=False
):
    """
    Manage files in the OAI client, listing, deleting vector stores or files as needed.
    """
    vsl, l = [], []
    try:
        logging.debug("Starting file management operations.")
        for vs in client.beta.vector_stores.list().data:
            if vs.file_counts.completed > 0:
                if show:
                    logging.debug(f"Available vector store: {vs.id} - {vs.name}")
                res = client.beta.vector_stores.files.list(vs.id)
                for d in res.data:
                    vsl.append((d.id, d.vector_store_id, d))
                    if delete_vsf and d:
                        client.beta.vector_stores.files.delete(
                            vector_store_id=vs.id, file_id=d.id
                        )
                        logging.info(f"Deleted vector store file: {d.id}")
                if delete_vss:
                    client.beta.vector_stores.delete(vs.id)
                    logging.info(f"Deleted vector store: {vs.id} - {vs.name}")

        # Process client files
        for fid in client.files.list().data:
            if show:
                logging.debug(f"File in OAI: {fid.id} - {fid.filename}")
            if delete_files:
                client.files.delete(fid.id)
                logging.debug(f"Deleted file: {fid.id} - {fid.filename}")
            else:
                l.append((fid.filename, fid.id))

        df = pd.DataFrame(vsl, columns=["fid", "vs_id", "vs_metadata"]).merge(
            pd.DataFrame(l, columns=["filename", "fid"])
        )
        logging.info("File management operation completed successfully.")
        return df[["vs_id", "fid", "filename", "vs_metadata"]]

    except Exception as e:
        logging.error(f"Error in file manager: {e}")
        return pd.DataFrame()


def markdown_to_pdf(report_text, filename, output_dir):
    """Completion text is directly converted to pdf"""
    st.session_state.file_counter += 1
    save_path = os.path.join(
        output_dir, filename.replace(".pdf", "_quantiq_analysis") + ".pdf"
    )
    abs_string = os.path.abspath("../imgs/quantiq_logo_75x75.svg")
    report_text = f"![Alt text]({abs_string})\n" + report_text
    pdf = MarkdownPdf()
    pdf.add_section(Section(report_text, toc=False))
    pdf.save(save_path)
    print(f"analysis saved as {save_path}")


def add_style(html_content):
    """
    Function to add styling to report the given HTML content and return the updated content.
    """
    try:
        style = """
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
                table, th, td {
                border: 1px solid black;
                border-radius: 10px;
                }

            </style>
            """

        # Extract the HTML content within the code block
        logging.info("Extracting HTML content.{html_content}")
        if "<!DOCTYPE html>" in html_content:
            styled_html = re.sub(r"(<!DOCTYPE html>)", r"\1\n" + style, html_content)
        else:
            # styled_html = re.sub(r"(<head>)", r"\1\n" + style,
            #                      html_content)
            styled_html = style + html_content

        # Log first 100 characters for brevity
        logging.debug(f"Split HTML content: {styled_html}...")

        # Replace unwanted HTML tags and add the style
        # html_content = html_content.replace("html\n<!DOCTYPE html>\n", "")
        logo = fetch_logo()
        styled_html_logo = logo + styled_html
        logging.debug(f"Logo info: {logo}...")
        logging.info(f"Parsed HTML content: {styled_html_logo}...")
        logging.debug("HTML content styled successfully.")
        return styled_html_logo.replace("```html", "").replace("```", "")

    except Exception as e:
        logging.error(f"Error in add_style function: {e}")
        return None


def fetch_logo():
    if "linux" in sys.platform:
        # abs_string = os.path.abspath("../imgs/quantiq_logo_75x75.svg")
        logo = '<img src="file:///app/imgs/user_logo.jpg" alt="Logo">'
        # logo = '<p><img src="/app/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
    else:
        # logo = '<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
        logo = '<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/user_logo.jpg" alt="Alt text" width="100" height="100" /></p>'
    return logo


def html_to_pdf(html_content, filename):
    """
    Convert HTML content to a PDF and save it to the specified output directory.
    """
    try:

        # Add styling to the HTML content
        logging.debug(f"Converting HTML content to PDF for {filename}.")
        string = add_style(html_content)

        if string is None:
            raise ValueError("Styled HTML content is None. Skipping PDF generation.")

        output_dir = st.session_state.bulk_output_dir

        # Define the save path for the PDF file
        save_path = os.path.join(output_dir, filename)

        # Generate the PDF from the HTML content
        HTML(string=string).write_pdf(save_path)

        logging.info(f"PDF generated and saved at {save_path}.")

    except Exception as e:
        logging.error(f"Error in html_to_pdf function: {e}")


def quantiq_analysis(client, file_paths, report_name):
    """
    Analyze one or multiple files using the OpenAI client and prepare a report.

    Parameters:
    - client: OpenAI client instance.
    - file_paths: List of file paths to process.
    - report_name: Name to use in the report and output filename.
    """
    try:
        assistant_id = st.session_state.openai_assistant_id

        # Upload all files and collect their file IDs
        attachments = []
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            logging.info(f"Sending file to vector store: {file_path}")

            # Upload the file
            if file_path.lower().endswith(".xlsx"):
                file = read_xlsx(file_path)
                with open(file_path.replace(".xlsx", ".txt"), "w") as f:
                    f.write(file)
                with open(file_path.replace(".xlsx", ".txt"), "rb") as f:
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
        logging.info(f"Thread created with ID: {thread.id}")

        # Poll the thread run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, assistant_id=assistant_id
        )
        logging.debug(f"Run created and polled successfully. Run ID: {run.id}")

        # Retrieve messages
        messages = list(
            client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id)
        )
        if messages:
            message_content = messages[0].content[0].text
            # Log part of the content
            logging.debug(f"Received message content: {message_content}...")
            logging.info(
                f"""Analysis completed for files: {
                         ', '.join([os.path.basename(fp) for fp in file_paths])}"""
            )
            return message_content
        else:
            logging.error("No messages received from assistant.")
            return None

    except Exception as e:
        logging.error(f"Error in quantiq_analysis function: {e}")
        return None


def output_report(client, message_content, filename):

    # logo = fetch_logo()
    # logging.debug(f"Logo: {logo}")
    # logging.info(f"Message content: {message_content}")
    # with open("report_tmp.html", "w") as f:
    #     f.write(message_content.value)

    html_to_pdf(message_content.value, filename=filename)
    oai_file_mgr(
        client, show=False, delete_vsf=False, delete_vss=True, delete_files=True
    )
    logging.info("Analysis completed for all files.")
    st.toast(f"{filename} Completed!")


def process_bulk_directory(client):
    """
    Processes files in the bulk directory according to the specified rules:
    - Files in the parent directory are processed individually.
    - Files in each subdirectory are processed together.
    Only .pdf and .docx files are processed.

    Parameters:
    - client: OpenAI client instance.
    """
    output_directory = st.session_state.bulk_output_dir
    bulk_directory = st.session_state.bulk_dir

    try:
        if not os.path.isdir(bulk_directory):
            raise ValueError(f"Bulk directory {bulk_directory} does not exist")

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            logging.info(f"Created output directory: {output_directory}")

        # Define the allowed file extensions
        allowed_extensions = [".pdf", ".docx", ".xlsx", ".csv"]

        # Process files directly under bulk_directory
        parent_files = []
        process_info_file = st.empty()
        for entry in os.listdir(bulk_directory):
            entry_path = os.path.join(bulk_directory, entry)
            if os.path.isfile(entry_path):
                process_info_file.write(f"Processing '{entry}'")
                # Check file extension
                _, ext = os.path.splitext(entry)
                if ext.lower() in allowed_extensions:
                    parent_files.append(entry_path)
                else:
                    logging.info(f"Skipping unsupported file: {entry}")

        for file_path in parent_files:
            filename = os.path.basename(file_path)
            logging.info(f"Processing parent directory file: {filename}")
            if st.session_state.assistant_mode == "On":
                message_content = quantiq_analysis(
                    client, [file_path], report_name=filename
                )
            else:
                message_content = quantiq_analysis_(
                    client, [file_path], report_name=filename
                )
            if message_content:
                # Save the analysis result to a file in the output directory
                output_filename = f"{os.path.splitext(filename)[0]}_report.pdf"
                output_filepath = os.path.join(output_directory, output_filename)

                if st.session_state.assistant_mode == "On":
                    output_report(client, message_content, output_filename)
                else:
                    output_report_(client, message_content, output_filename)
                logging.info(f"Saved analysis result to {output_filepath}")
            else:
                logging.error(f"Failed to analyze file: {filename}")

        # Process each subdirectory
        process_info = st.empty()
        for entry in os.listdir(bulk_directory):
            entry_path = os.path.join(bulk_directory, entry)
            if os.path.isdir(entry_path):
                process_info.write(f"Processing '{entry}'")
                subdir_name = entry
                file_paths = []
                for root, dirs, files in os.walk(entry_path):
                    for filename in files:
                        # Check file extension
                        _, ext = os.path.splitext(filename)
                        if ext.lower() in allowed_extensions:
                            file_path = os.path.join(root, filename)
                            file_paths.append(file_path)
                        else:
                            logging.info(
                                f"""Skipping unsupported file:
                                         {filename} in {subdir_name}"""
                            )
                    break  # Do not recurse into subdirectories of subdirectories

                if file_paths:
                    logging.info(
                        f"""Processing subdirectory '{subdir_name}' with files:
                                 {', '.join([os.path.basename(fp) for fp in file_paths])}"""
                    )
                    if st.session_state.assistant_mode == "On":
                        message_content = quantiq_analysis(
                            client, file_paths, report_name=subdir_name
                        )
                    else:
                        message_content = quantiq_analysis_(
                            client, file_paths, report_name=subdir_name
                        )

                    if message_content:
                        # Save the analysis result to a file in the output directory
                        output_filename = f"{subdir_name}_report.pdf"
                        output_filepath = os.path.join(
                            output_directory, output_filename
                        )

                        if st.session_state.assistant_mode == "On":
                            output_report(client, message_content, output_filename)
                        else:
                            output_report_(client, message_content, output_filename)
                    else:
                        logging.error(f"Failed to analyze subdirectory: {subdir_name}")
                else:
                    logging.warning(
                        f"No supported files found in subdirectory {subdir_name}"
                    )

    except Exception as e:
        logging.error(f"Error in process_bulk_directory function: {e}")


def download_file(file_selected):
    # File path
    file_path = os.path.join(st.session_state.output_dir, file_selected)
    with open(file_path, "rb") as file:
        file_data = file.read()
    # Determine the MIME type based on the file extension
    if file_selected.lower().endswith(".docx"):
        mime_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    elif file_selected.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        mime_type = "application/octet-stream"
    # Create a download button in the Streamlit app
    st.download_button(
        label="Download file", data=file_data, file_name=file_selected, mime=mime_type
    )


def zipdir(bulk_output_dir):
    files = [f for f in os.listdir(bulk_output_dir) if f.endswith(".pdf")]
    zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")

    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = os.path.join(bulk_output_dir, file)
            # Add file to zip without including the directory structure
            zipf.write(file_path, arcname=file)


def download_zip_file():
    bulk_output_dir = st.session_state.bulk_output_dir
    if len([i for i in os.listdir(bulk_output_dir) if ".zip" not in i]) > 0:
        zipdir(bulk_output_dir)
        logging.info("Output files zipped successfully.")
        zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")
        with open(zip_file_path, "rb") as f:
            bytes_data = f.read()
        btn = st.download_button(
            label="Download Analysis Results",
            type="primary",
            data=bytes_data,
            file_name="quantiq_results.zip",
            mime="application/zip",
            on_click=reset_run,
            use_container_width=True,
        )
        if btn:
            st.success("Downloaded")


def delete_dir_contents():
    """
    Deletes the directories at the given paths and recreates them.
    """
    dirs = [
        st.session_state.output_dir,
        st.session_state.bulk_dir,
        st.session_state.bulk_output_dir,
    ]

    for dir_ in dirs:
        path = os.path.normpath(dir_)
        print(f"Refreshing directory: {path}")
        if os.path.exists(path):
            shutil.rmtree(path)  # Delete the directory and its contents
            print(f"Deleted directory: {path}")
        os.makedirs(path)  # Recreate the directory
        print(f"Recreated directory: {path}")


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


def load_image(LOGO_FILENAME):
    """
    Load the current logo image. If a new logo has been uploaded, it uses that.
    Otherwise, it loads the default logo from the specified directory.
    """
    logo_path = os.path.join(st.session_state.img_dir, LOGO_FILENAME)
    if os.path.exists(logo_path):
        try:
            image = Image.open(logo_path)
            return image
        except Exception as e:
            st.error(f"Error loading the logo image.{e}")
            return None
    else:
        st.error("Default logo not found!")
        return None


def render_logo():
    image = load_image(LOGO_FILENAME=st.session_state["current_logo"])
    if image is None:
        st.error(
            f"""Error: Unable to load the image.{
                 st.session_state['current_logo']}"""
        )
    # Convert image to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded_image = base64.b64encode(buffer.getvalue()).decode()
    clickable_image_html = f"""
            <a href="?logo_clicked=true">
            <img src="data:image/png;base64,{encoded_image}" alt="Logo" style="cursor: pointer; width: 95px; height: 95px;">
            </a>
    """
    st.markdown(
        clickable_image_html, unsafe_allow_html=True, help="Click logo to change"
    )


def handle_logo():

    render_logo()

    if st.query_params["logo_clicked"] == "true":
        st.write("")
        st.info("Upload .jpg logo to replace the current logo.")
        uploaded_file = st.file_uploader(" - ", type=["jpg"], key="file_uploader")

        # save uploaded file and set as current logo
        if uploaded_file is not None:
            save_path = os.path.join("imgs", st.session_state["current_logo"])
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.query_params["logo_clicked"] = None
            uploaded_file = None
            st.rerun()

    # restore default logo
    if st.session_state["current_logo"] == "user_logo.jpg":
        if st.button("Reset Logo"):
            st.session_state["current_logo"] = "quantiq_logo_75x75.jpg"
            with open(
                os.path.join(
                    st.session_state.img_dir, st.session_state["current_logo"]
                ),
                "rb",
            ) as f:
                img = f.read()
            with open(
                os.path.join(st.session_state.img_dir, "user_logo.jpg"), "wb"
            ) as f:
                f.write(img)
            st.query_params["logo_clicked"] = None
            st.rerun()


# --------------------------------- NEW QUANTIQ ANALYSIS ---------------------------------


def structured_outputs():

    class ScoreItem(BaseModel):
        criteria: str
        score: str
        description: str

    class ReportData(BaseModel):
        title: str
        summary: str
        evidence: str
        score_items: List[ScoreItem]
        overall_score: str
        questions: List[str]
        # note: str = "All figures are in thousands."

    return ReportData


# Sample HTML report


def insert_style_and_image(html_content, image_path):
    soup = BeautifulSoup(html_content, "html.parser")

    # Create a <style> tag with the provided CSS
    style_tag = soup.new_tag("style")
    style_tag.string = """
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
        table, th, td {
            border: 1px solid black;
            border-radius: 10px;
        }
    """

    # Insert the <style> tag into the <head> section
    soup.head.append(style_tag)

    # Create an <img> tag with the class applied
    img_tag = soup.new_tag(
        "img",
        src=image_path,
        alt="Alt text",
        class_="company-logo",
        style="width: 100px; height: auto;",
    )

    # Insert the <img> tag before the first <p> tag in the <body>
    body = soup.body
    body.insert(0, img_tag)

    # Convert the modified soup back to a string
    return str(soup)


def fetch_template():
    # Load the template from the current directory
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("template.html")
    return template


def ingest_files(file_paths):
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
            print(f"Unsupported file type: {file_extension}")

    return combined_content


def read_pdf(file_path):
    content = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            content += page.extract_text()
    return content


def read_docx(file_path):
    doc = docx.Document(file_path)
    content = ""
    for paragraph in doc.paragraphs:
        content += paragraph.text + "\n"
    return content


def read_xlsx(file_path):
    content = ""
    excel_data = pd.read_excel(file_path)
    content += excel_data.to_string(index=False)
    return content


def read_csv(file_path):
    content = ""
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            content += ",".join(row) + "\n"
    return content


def quantiq_analysis_(client, file_paths, report_name):

    prompt_instructions = st.session_state.editor_content

    report_data = ingest_files(file_paths)

    ReportDataStructure = structured_outputs()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": prompt_instructions},
            {
                "role": "user",
                "content": f"""Company: {
                report_name}. Report data:"""
                + report_data,
            },
        ],
        response_format=ReportDataStructure,
    )

    result = completion.choices[0].message

    return result


def html_to_pdf_(html_content, file_name):
    output_dir = "bulk_output"  # st.session_state.bulk_output_dir
    save_path = os.path.join(output_dir, file_name)
    HTML(string=html_content).write_pdf(save_path)


def add_style_(result):
    template = fetch_template()
    report = template.render(**result.parsed.model_dump())
    image_path = "file:///" + os.path.abspath("imgs/user_logo.jpg")
    updated_html = insert_style_and_image(report, image_path)

    return updated_html


def output_report_(client, message_content, output_filename):
    styled_html = add_style_(message_content)
    html_to_pdf_(styled_html, output_filename)
