# quantiq/reporting.py

import os
import logging
import streamlit as st
from weasyprint import HTML
from markdown_pdf import MarkdownPdf, Section
from bs4 import BeautifulSoup
import re
from quantiq.logging_setup import set_logging
from quantiq.file_handler import read_xlsx

# Initialize logger
logger = set_logging()


def markdown_to_pdf(report_text, filename, output_dir):
    """
    Converts markdown text directly to PDF.

    Args:
        report_text (str): Markdown text to convert.
        filename (str): Name of the output PDF file.
        output_dir (str): Directory to save the PDF.
    """
    try:
        st.session_state.file_counter += 1
        save_path = os.path.join(
            output_dir, filename.replace(".pdf", "_quantiq_analysis") + ".pdf"
        )
        abs_string = os.path.abspath("../imgs/quantiq_logo_75x75.svg")
        report_text = f"![Alt text]({abs_string})\n" + report_text
        pdf = MarkdownPdf()
        pdf.add_section(Section(report_text, toc=False))
        pdf.save(save_path)
        logger.info(f"Analysis saved as {save_path}")
    except Exception as e:
        logger.error(f"Error in markdown_to_pdf function: {e}")


def add_style(html_content):
    """
    Adds CSS styling to the given HTML content.

    Args:
        html_content (str): Original HTML content.

    Returns:
        str: Styled HTML content.
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

        logger.info(f"Adding styles to HTML content.")

        if "<!DOCTYPE html>" in html_content:
            styled_html = re.sub(r"(<!DOCTYPE html>)", r"\1\n" + style, html_content)
        else:
            styled_html = style + html_content

        # Insert logo
        logo = fetch_logo()
        styled_html_logo = logo + styled_html
        logger.debug(f"Inserted logo into HTML content.")
        logger.info("HTML content styled successfully.")
        return styled_html_logo.replace("```html", "").replace("```", "")

    except Exception as e:
        logger.error(f"Error in add_style function: {e}")
        return None


def fetch_logo():
    """
    Fetches the logo HTML based on the operating system.

    Returns:
        str: HTML string for the logo image.
    """
    try:
        if "linux" in os.sys.platform:
            logo = '<img src="file:///app/imgs/user_logo.jpg" alt="Logo">'
        else:
            logo = '<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/user_logo.jpg" alt="Alt text" width="100" height="100" /></p>'
        return logo
    except Exception as e:
        logger.error(f"Error in fetch_logo function: {e}")
        return ""


def html_to_pdf(html_content, filename, output_dir):
    """
    Converts HTML content to a PDF and saves it.

    Args:
        html_content (str): Styled HTML content.
        filename (str): Name of the output PDF file.
        output_dir (str): Directory to save the PDF.
    """
    try:
        string = add_style(html_content)
        if string is None:
            raise ValueError("Styled HTML content is None. Skipping PDF generation.")

        save_path = os.path.join(output_dir, filename)
        HTML(string=string).write_pdf(save_path)
        logger.info(f"PDF generated and saved at {save_path}.")
    except Exception as e:
        logger.error(f"Error in html_to_pdf function: {e}")


def insert_style_and_image(html_content, image_path):
    """
    Inserts CSS styles and an image into the HTML content.

    Args:
        html_content (str): Original HTML content.
        image_path (str): Path to the image to insert.

    Returns:
        str: Modified HTML content with styles and image.
    """
    try:
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
        if soup.head:
            soup.head.append(style_tag)
        else:
            head = soup.new_tag("head")
            head.append(style_tag)
            soup.insert(0, head)

        # Create an <img> tag with the class applied
        img_tag = soup.new_tag(
            "img", src=image_path, alt="Logo", style="width: 100px; height: auto;"
        )

        # Insert the <img> tag before the first <p> tag in the <body>
        if soup.body:
            first_p = soup.body.find("p")
            if first_p:
                first_p.insert_before(img_tag)
            else:
                soup.body.insert(0, img_tag)
        else:
            body = soup.new_tag("body")
            body.append(img_tag)
            soup.append(body)

        logger.debug("Inserted style and image into HTML content.")
        return str(soup)

    except Exception as e:
        logger.error(f"Error in insert_style_and_image function: {e}")
        return ""


def fetch_template(template_path="template.html"):
    """
    Loads the HTML template.

    Args:
        template_path (str): Path to the HTML template.

    Returns:
        Template: Jinja2 template object.
    """
    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(template_path)
        logger.info(f"Template {template_path} loaded successfully.")
        return template
    except Exception as e:
        logger.error(f"Error fetching template: {e}")
        return None


def output_report(client, message_content, filename, mode="On"):
    """
    Generates and outputs the report based on analysis.

    Args:
        client: OpenAI client instance.
        message_content (str): Content from the analysis.
        filename (str): Name of the output PDF file.
        mode (str): Assistant mode ("On" or "Off").
    """
    try:
        styled_html = add_style(message_content)
        if mode == "On":
            output_report(client, message_content, filename)
        else:
            output_report_(client, message_content, filename)
        logger.info(f"Report {filename} generated successfully.")
        st.toast(f"{filename} Completed!")
    except Exception as e:
        logger.error(f"Error in output_report function: {e}")


def output_report_(client, message_content, output_filename):
    """
    Alternate report output function for assistant mode off.

    Args:
        client: OpenAI client instance.
        message_content (str): Content from the analysis.
        output_filename (str): Name of the output PDF file.
    """
    try:
        styled_html = add_style_(message_content)
        html_to_pdf_(styled_html, output_filename)
        logger.info(
            f"Report {output_filename} generated successfully in assistant mode Off."
        )
    except Exception as e:
        logger.error(f"Error in output_report_ function: {e}")
