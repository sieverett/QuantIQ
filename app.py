import os
import streamlit as st
from openai import OpenAI
from docx import Document
from markdown_pdf import MarkdownPdf, Section
from weasyprint import HTML
from quantiq import quantiq as qiq
import time
import io
from streamlit_quill import st_quill

logging = qiq.set_logging()


def initialize_session_state(defaults):
    """
    Initialize Streamlit session state variables if they don't already exist.

    Args:
    defaults (dict): A dictionary of session state variable names and their default values.
    """
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# Set page config
st.set_page_config(
    page_title="QUANT-IQ: Quantitative Analysis Tool for Intelligent Financial Review",
    layout="wide",
    page_icon="cyclone",
    menu_items={
        'Get Help': 'https://sieverett.github.io/QuantIQ/FAQ.html',
        'Report a bug': 'https://github.com/sieverett/QuantIQ/issues/new',
        'About': """
            ## About QUANT-IQ
            **QUANT-IQ** is a powerful tool designed to streamline the analysis of financial statements using AI.
            With a user-friendly interface, the app supports document uploads in PDF, DOCX, and ZIP formats, and
            leverages OpenAI's GPT to generate insightful reports. Whether for individual documents or bulk processing,
            QUANT-IQ simplifies financial analysis for both professionals and organizations.

            **Author**: Silas Everett
            **GitHub**: [sieverett.github.io](https://sieverett.github.io)
        """
    },
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
    <style>
        .stAppDeployButton {display: none;}
        #MainMenu {visibility: visible;}
        #header {visibility: hidden;}
        #footer {visibility: hidden;}
        #stDecoration {display:none;}
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        section[data-testid="stSidebar"] {
            width: 300px !important; # Set the width to your desired value
        }
        .stTabs [data-baseweb="tab-list"] {
		gap: 3px;
    }

	.stTabs [data-baseweb="tab"] {
		height: 20px;
        white-space: pre-wrap;
		background-color: #1d69b5;
		border-radius: 6px 6px 2px 2px;
		gap: 2px;
		padding-top: 15px;
		padding-bottom: 15px;
    }

	.stTabs [aria-selected="true"] {
  		background-color: #06111c;
        color:#ffffff;
	}

    [data-testid="stSidebar"] .stExpander  {
    border: none;
    box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state variables
defaults = {
    "img_dir": 'imgs',
    "chat_history": [],
    "bulk_file_uploaded": False,
    "thread_id": None,
    "bulk_dir": "bulk",
    "output_dir": "output",
    "file_counter": 0,
    "reset_clicked": False,
    "uploaded_files": [],
    "bulk_output_dir": "bulk_output",
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "openai_assistant_id": os.getenv("OPENAI_ASSISTANT_ID", "")
}

initialize_session_state(defaults)

# Ensure directories exist
os.makedirs(st.session_state.bulk_dir, exist_ok=True)
os.makedirs(st.session_state.output_dir, exist_ok=True)
os.makedirs(st.session_state.bulk_output_dir, exist_ok=True)

# Function to reset session state values

with st.sidebar:

    st.text("API key \nand Assistant ID")
    # OpenAI API key input logic
    if st.session_state.openai_api_key == os.getenv("OPENAI_API_KEY", ""):
        api_key = st.text_input(
            label="Enter your OpenAI API key",
            placeholder="OpenAI API Key",
            type="password",
            help="Go to [OpenAI API key](https://platform.openai.com/api-keys) for platform authentication."
        )
        st.write(api_key)
        if api_key:
            st.session_state.openai_api_key = api_key
            st.write("API key has been set.")

    # OpenAI Assistant key input logic
    if st.session_state.openai_assistant_id == os.getenv("OPENAI_ASSISTANT_ID", ""):
        assistant_key = st.text_input(
            label="Enter your OpenAI Assistant ID",
            placeholder="OpenAI Assistant ID",
            type="password",
            help="Go to [OpenAI Assistant ID](https://platform.openai.com/assistants/) create custom Assistant ID."
        )

        if assistant_key:
            st.session_state.openai_assistant_id = assistant_key
            st.write("Assistant ID has been set.")

    with st.expander('Active Keys', expanded=False):
        st.write("API key:", '•••••••••••' +
                 st.session_state.openai_api_key[-4:])
        st.write("Asst. ID:", '•••••••••••' +
                 st.session_state.openai_assistant_id[-4:])

    # Reset button logic for both keys
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Key Reset", key="reset_keys"):
            st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY", "")
            st.session_state.openai_assistant_id = os.getenv(
                "OPENAI_ASSISTANT_ID", "")
            st.rerun()
# Title
tab1, tab2 = st.tabs(["Analyzer", "Prompt Editor"])

with tab1:
    with st.container():

        col1, col2 = st.columns([2, 10], gap="small")

        # Displaying logo and title
        with col1:
            st.image(os.path.join(st.session_state.img_dir,
                     "quantiq_logo_75x75.jpg"))

        with col2:
            st.title("QUANT-IQ")

        st.subheader("Financial Statement Analyzer")

        # UI for file upload
        file_upload_box = st.empty()

        if not st.session_state["bulk_file_uploaded"]:
            st.session_state["files"] = file_upload_box.file_uploader(
                "Upload your documents to begin (.zip, .pdf or .docx)",
                accept_multiple_files=True,
                type=["zip", "pdf", "docx"],
                help="Start by uploading your financial documents in ZIP, PDF, or DOCX format."
            )

            # Process the uploaded files
            if st.session_state["files"]:
                for uploaded_file in st.session_state["files"]:
                    logging.info(f"File uploaded: {uploaded_file.name}")

                    if uploaded_file.type == 'application/x-zip-compressed':
                        qiq.handle_zipped_files(uploaded_file)
                        logging.info(
                            f"Processed zipped file: {uploaded_file.name}")
                    else:
                        file_path = qiq.handle_file_upload(
                            uploaded_file, st.session_state.bulk_dir)
                        if file_path:
                            st.success(
                                f"{uploaded_file.name} uploaded successfully!")
                            logging.info(
                                f"File {uploaded_file.name} uploaded successfully.")

                st.session_state["bulk_file_uploaded"] = True
                st.write("Files uploaded successfully!")
                st.session_state["reset_clicked"] = False
                logging.info("All files uploaded and session state updated.")
                st.rerun()

        if st.session_state["bulk_file_uploaded"] and st.session_state["files"]:

            uploaded_files_ = os.listdir(st.session_state.bulk_dir)
            bad_files = [
                f for f in uploaded_files_ if ".pdf" not in f and ".docx" not in f]

            if bad_files:
                st.error(
                    f"Only .pdf and .docx files will be analyzed. The following file(s) are not supported: {bad_files}")
                logging.warning(f"Unsupported files detected: {bad_files}")

            button_label = "Analyze Files" if len(
                uploaded_files_) > 1 else "Analyze File"

            if st.button(button_label, type="primary"):
                progress_text = "Analyzing: "
                my_bar = st.progress(0, text=progress_text)

                files_to_process = [f for f in os.listdir(
                    st.session_state.bulk_dir) if ".pdf" in f or ".docx" in f]
                num_files = len(files_to_process)

                client = OpenAI(api_key=st.session_state.openai_api_key)

                with st.spinner("Analyzing..."):
                    for idx, filename in enumerate(files_to_process):
                        idx += 1
                        my_bar.progress(idx / num_files,
                                        text=progress_text + filename)
                        logging.info(
                            f"Analyzing file {filename} ({idx}/{num_files})")

                        start_time = time.time()  # Capture start time
                        # Perform the analysis
                        message_content, citations = qiq.quantiq_analysis(
                            client, filename, input_dir=st.session_state.bulk_dir)

                        end_time = time.time()  # Capture end time
                        elapsed_time = end_time - start_time
                        # Log the results
                        logging.info(
                            f"Elapsed time for {filename}: {elapsed_time:.2f} seconds")
                        logo = qiq.fetch_logo()
                        logging.info(f"Logo: {logo}")
                        logging.info(f"Message content: {message_content}")
                        qiq.html_to_pdf(message_content.value, filename=filename.replace(".docx", ".pdf"),
                                        output_dir=st.session_state.bulk_output_dir)
                        qiq.oai_file_mgr(
                            client, show=False, delete_vsf=False, delete_vss=True, delete_files=True)

                    logging.info("Analysis completed for all files.")
                st.success('Done!')

                if len(os.listdir(st.session_state.bulk_output_dir)) > 0:
                    qiq.zipdir(
                        bulk_output_dir=st.session_state.bulk_output_dir)
                    logging.info("Output files zipped successfully.")

                st.session_state.bulk_file_uploaded = False
                st.session_state["files"] = []
                st.session_state.reset_clicked = False

        col1, col2 = st.columns([3, 1])

        with col1:
            if not st.session_state.reset_clicked and len(os.listdir(st.session_state.bulk_dir)) > 0:
                if st.button("Reset", type="secondary"):
                    qiq.reset_run()
                    logging.info("Run reset and state cleared.")
                    st.rerun()

        with col2:
            if os.path.isfile(os.path.join(st.session_state.bulk_output_dir, 'quantiq_results.zip')):
                qiq.download_zip_file(
                    bulk_output_dir=st.session_state.bulk_output_dir)

with tab2:

    st.subheader("Prompt Editor",
                 help="Edit the default prompt for the AI assistant.\nClick 'Save Edits' to update the AI Assistant.")
    # st.text(
    #     "Edit the default prompt for the AI assistant.\nClick 'Save Edits' to update the AI Assistant.")

    def get_current_prompt(method=None):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        my_assistant = client.beta.assistants.retrieve(
            os.getenv("OPENAI_ASSISTANT_ID"))
        with open('prompts/current.txt', 'w') as file:
            file.write(my_assistant.instructions)
        if method == 'output format only':
            return my_assistant.instructions[-335:]
        elif method == 'less output format':
            return my_assistant.instructions[:-335]
        else:
            return my_assistant.instructions

    def get_default_prompt(method=None):
        with open('prompts/backup.txt', 'r') as file:
            instructions = file.read()
        if method == 'output format only':
            return instructions[-335:]
        elif method == 'less output format':
            return instructions[:-335]
        else:
            return instructions

    def update_assistant(instructions):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        my_updated_assistant = client.beta.assistants.update(
            os.getenv("OPENAI_ASSISTANT_ID"),
            instructions=instructions
        )
        update_success.toast("Assistant updated successfully!")

    # Initialize session state to hold the editor content and the saved version
    if 'editor_content' not in st.session_state:
        st.session_state.editor_content = get_current_prompt(
            'less output format')

    if 'saved_content' not in st.session_state:
        st.session_state.saved_content = get_current_prompt(
            'less output format')

    with st.expander("Edit prompt", expanded=True):
        # Quill editor that allows the user to edit the content
        st.session_state.editor_content = st_quill(toolbar=[['bold', 'italic', 'underline'],
                                                            ['link', 'blockquote',
                                                                'code-block']],
                                                   value=st.session_state.editor_content, key="quill_editor")

    col1, col2, col3 = st.columns([1, 1, 5])

    update_success = st.empty()
    with col1:
        # Button to save the edited content
        if st.button("Save Edits"):
            st.session_state.saved_content = st.session_state.editor_content
            epoch_time = int(time.time())
            file_name = f"quantiq_prompt_{epoch_time}.txt"
            with open(f'prompts/{file_name}', 'w') as file:
                file.write(st.session_state.saved_content)

            update_assistant(instructions=st.session_state.saved_content +
                             get_default_prompt('output format only'))
        #     client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        #     my_updated_assistant = client.beta.assistants.update(
        #         os.getenv("OPENAI_ASSISTANT_ID"),
        #         instructions=st.session_state.saved_content +
        #         get_default_prompt('output format only')
        #     )
        # update_success.toast("Assistant updated successfully!")

    with col2:
        if st.session_state.saved_content:
            epoch_time = int(time.time())
            file_name = f"quantiq_prompt_{epoch_time}.txt"
            buffer = io.StringIO(st.session_state.saved_content)
            st.download_button(label="Download",
                               data=buffer.getvalue(),
                               file_name=file_name,
                               mime="text/plain")

    with col3:
        # Button to restore the default string
        if st.button("Restore Default Prompt"):
            st.session_state.editor_content = get_default_prompt(
                "less output format")
            st.toast("Click 'Save Edits' to restore defualt!")
            update_assistant(st.session_state.editor_content)
            st.rerun(scope="app")

    # with st.expander("Prompt Versions", expanded=True):
    #     selected_prompt = st.radio('Select Prompt Version', index=0, options=[
    #         None]+sorted(os.listdir('prompts'), reverse=True))
    #     if selected_prompt != None:
    #         with open(f'prompts/{selected_prompt}', 'r') as file:
    #             st.session_state.editor_content = file.read()
    #             st.write(st.session_state.editor_content)
    # #         st.write(f"Selected prompt: {selected_prompt}")
    #         selected_prompt = None
    #         st.rerun(scope="fragment")
