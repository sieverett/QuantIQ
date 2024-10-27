import os
import io
import time
import base64
import streamlit as st
from openai import OpenAI
from quantiq import quantiq_ as qiq
from quantiq import prompt_utils as pu
from quantiq import zip_manager as zm
from streamlit_quill import st_quill
from streamlit_option_menu import option_menu


# Optionally, clean up the extracted files if no longer needed


# Set loggingzm
logging = qiq.set_logging()


def trigger_download(content, file_name):
    # Convert the content to base64
    b64 = base64.b64encode(content.encode()).decode()
    # Create the download link in HTML format
    download_link = f"""<a href="data:text/plain;base64,{b64}" download="{
        file_name}">Click Here to Download the File</a>"""
    #  Display the download link (this will auto-trigger if necessary)
    st.markdown(download_link, unsafe_allow_html=True)


def initialize_session_state(defaults):
    """
    Initialize Streamlit session state variables if they don't already exist.

    Args:
    defaults (dict): A dictionary of session state variable names and their default values.
    """
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def store_keys(params, file_path=".streamlit/secrets.toml"):
    # Open the file in write mode (or append mode, if you want to keep existing values)
    with open(file_path, "w") as env_file:
        for key, value in params.items():
            env_file.write(f'{key}="{value}"\n')


def get_assistant():
    try:
        client = OpenAI(api_key=st.session_state.openai_api_key)
        my_assistant = client.beta.assistants.retrieve(
            st.session_state.openai_assistant_id
        )
        st.session_state.authenticated_flag = True
    except Exception as e:
        st.warning("Set your API key and Assistant ID.")
        st.session_state.authenticated_flag = False


# process_zip_and_files(zip_file_path, extract_directory)


# Set page config
st.set_page_config(
    page_title="QUANT-IQ: Quantitative Analysis Tool for Intelligent Financial Review",
    layout="wide",
    page_icon="cyclone",
    menu_items={
        "Get Help": "https://sieverett.github.io/QuantIQ/FAQ.html",
        "Report a bug": "https://github.com/sieverett/QuantIQ/issues/new",
        "About": """
            ## About QUANT-IQ
            **QUANT-IQ** is a powerful tool designed to streamline the analysis of financial statements using AI.
            With a user-friendly interface, the app supports document uploads in PDF, DOCX, and ZIP formats, and
            leverages OpenAI's GPT to generate insightful reports. Whether for individual documents or bulk processing,
            QUANT-IQ simplifies financial analysis for both professionals and organizations.

            **Author**: Silas Everett
            **GitHub**: [sieverett.github.io](https://sieverett.github.io)
        """,
    },
    initial_sidebar_state="expanded",
)

# Apply custom CSS to page
st.markdown(
    """
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
  		background-color: #077af2;
        color:#ffffff;
	}

    [data-testid="stSidebar"] .stExpander  {
    border: none;
    box-shadow: none;
    }       
            
    div[data-testid="stFileDropzoneInstructions"]>div>span::after {
       content:"INSTRUCTIONS_TEXT";
       visibility:visible;
       display:block;
    }

    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state variables
defaults = {
    "img_dir": "imgs",
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
    "openai_assistant_id": os.getenv("OPENAI_ASSISTANT_ID", ""),
    "authenticated_flag": False,
    "key_set": True,
    "editor_content": pu.get_current_prompt(method="less output format"),
    "default_prompt": pu.get_default_prompt(method="less output format"),
    "assistant_instructions": pu.get_current_prompt(),
    "current_logo": "user_logo.jpg",
    "logo_clicked": None,
    "img_dir": "imgs",
}

initialize_session_state(defaults)

if "logo_clicked" not in st.query_params:
    st.query_params["logo_clicked"] = None

# Ensure directories exist
os.makedirs(st.session_state.bulk_dir, exist_ok=True)
os.makedirs(st.session_state.output_dir, exist_ok=True)
os.makedirs(st.session_state.bulk_output_dir, exist_ok=True)


# 1. as sidebar menu
with st.sidebar:

    # Title
    qiq.handle_logo()
    st.title("QUANT-IQ")
    selected = option_menu(
        "Main Menu",
        ["Analyze", "Prompt", "Settings"],
        icons=["magic", "list-task", "gear"],
        menu_icon="cast",
        default_index=0,
    )
    get_assistant()

if selected == "Settings":

    st.text("API key \nand Assistant ID")
    # OpenAI API key input logic
    api_key = st.text_input(
        label="Enter your OpenAI API key",
        placeholder="OpenAI API Key",
        type="password",
        help="Go to [OpenAI API key](https://platform.openai.com/api-keys) for platform authentication.",
    )
    if api_key:
        st.session_state.openai_api_key = api_key
        # st.toast("API key has been set.")
        st.session_state.key_set = True

    # OpenAI Assistant key input logic

    assistant_key = st.text_input(
        label="Enter your OpenAI Assistant ID",
        placeholder="OpenAI Assistant ID",
        type="password",
        help="Go to [OpenAI Assistant ID](https://platform.openai.com/assistants/) create custom Assistant ID.",
    )

    if assistant_key:
        st.session_state.openai_assistant_id = assistant_key
        # st.toast("Assistant ID has been set.")
        st.session_state.key_set = True

        # save keys for session
        if st.button(
            "set Keys",
            key="add_keys",
            help="Set keys for use.",
            use_container_width=True,
        ):
            store_keys(
                params={
                    "OPENAI_API_KEY": st.session_state.openai_api_key,
                    "OPENAI_ASSISTANT_ID": st.session_state.openai_assistant_id,
                }
            )
            st.session_state.key_set = False
            st.rerun(scope="app")

            if st.session_state.authenticated_flag:
                st.toast(":old_key: Authorized")
            else:
                st.toast(":confounded: Not Authorized!")
    # tab1, tab2 = st.tabs(["Analyzer", "Prompt Editor"])

if selected == "Analyze":
    with st.container():
        st.subheader("Financial Statement Analyzer")
        # UI for file upload
        file_upload_box = st.empty()
        if not st.session_state["bulk_file_uploaded"]:
            st.session_state["files"] = file_upload_box.file_uploader(
                "Upload your documents to begin (.zip, .pdf or .docx)",
                accept_multiple_files=True,
                type=["zip", "pdf", "docx"],
                help="Start by uploading your financial documents in ZIP, PDF, or DOCX format.",
            )
            if st.session_state.authenticated_flag == False:
                st.warning(
                    "Set your OpenAI API key and Assistant ID in Settings to proceed."
                )
                st.stop()
            # Process the uploaded files
            if st.session_state["files"]:
                for uploaded_file in st.session_state["files"]:
                    logging.info(f"File uploaded: {uploaded_file.name}")
                    if uploaded_file.type == "application/x-zip-compressed":
                        zm.handle_zipped_files(uploaded_file)
                        logging.info(f"Processed zipped file: {uploaded_file.name}")
                    else:
                        file_path = qiq.handle_file_upload(
                            uploaded_file, st.session_state.bulk_dir
                        )
                        if file_path:
                            logging.info(
                                f"File {uploaded_file.name} uploaded successfully."
                            )
                st.session_state["bulk_file_uploaded"] = True
                st.write("Files uploaded successfully!")
                st.session_state["reset_clicked"] = False
                logging.info("All files uploaded and session state updated.")
                st.rerun()

        if st.session_state["bulk_file_uploaded"] and st.session_state["files"]:
            uploaded_files_ = os.listdir(st.session_state.bulk_dir)
            if st.button("Analyze", type="primary"):
                files_to_process = [
                    f
                    for f in os.listdir(st.session_state.bulk_dir)
                    if ".pdf" in f or ".docx" in f
                ]
                num_files = len(files_to_process)
                with st.spinner("Analyzing..."):
                    client = OpenAI(api_key=st.session_state.openai_api_key)
                    qiq.process_bulk_directory(client)
                st.session_state.bulk_file_uploaded = False
                st.session_state["files"] = []
                st.session_state.reset_clicked = False
        col1, col2, buffer = st.columns([3, 3, 5])
        with col1:
            if (
                not st.session_state.reset_clicked
                and len(os.listdir(st.session_state.bulk_dir)) > 0
            ):
                if st.button("  Reset  ", type="secondary", use_container_width=True):
                    qiq.reset_run()
                    logging.info("Run reset and state cleared.")
                    st.rerun()
        with col2:
            qiq.download_zip_file()

if selected == "Prompt":

    st.subheader(
        "Prompt Editor",
        help="Edit the default prompt for the AI assistant.\nClick 'Save' to update the AI Assistant.",
    )

    # default_prompt = pu.get_default_prompt('less output format')

    selected2 = option_menu(
        None,
        ["Edit", "Save", "Download", "Restore"],
        icons=["list-task", "robot", "cloud-download", "reply"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if selected2 == "Edit":
        with st.expander("Prompt", expanded=True):
            # Quill editor that allows the user to edit the content
            with st.container():
                current_content = st_quill(
                    toolbar=[
                        ["bold", "italic", "underline"],
                        ["link", "blockquote", "code-block"],
                    ],
                    value=st.session_state.editor_content,
                    key="quill",
                )

                if st.session_state.editor_content != current_content:
                    # st.write("Content updated.")
                    st.session_state.editor_content = current_content
                    pu.set_current_prompt(current_content)

    # col1, col2, col3, buffer = st.columns([4, 5, 4, 9])
    update_success = st.empty()

    if selected2 == "Save":
        if (
            st.session_state.assistant_instructions
            != st.session_state.editor_content + pu.get_output_format()
        ):
            # Button to save the edited content
            # if st.button("Update Assistant", help="Updates prompt for Openai Assistant use."):
            epoch_time = int(time.time())
            file_name = f"quantiq_prompt_{epoch_time}.txt"
            with open(f"prompts/{file_name}", "w") as file:
                file.write(st.session_state.editor_content)
            pu.set_assistant_instructions(
                instructions=st.session_state.editor_content + pu.get_output_format()
            )
            st.session_state.assistant_instructions = (
                st.session_state.editor_content + pu.get_output_format()
            )
            update_success.success("Assistant updated successfully!")
        else:
            update_success.warning("No changes to save.")

    if selected2 == "Restore":
        # col1, col2, buffer = st.columns([6, 3, 2])
        # # Button to restore the default string
        # with col1:
        #     st.text("Warning! Clicking this will restore to default prompt:")
        # with col2:
        #     if st.button("Restore Default Prompt"):
        if st.session_state.editor_content != st.session_state.default_prompt:
            current_content = st.session_state.default_prompt
            st.session_state.editor_content = st.session_state.default_prompt
            pu.set_current_prompt(st.session_state.default_prompt)
            pu.set_assistant_instructions(
                instructions=st.session_state.default_prompt + pu.get_output_format()
            )
            st.toast("Default prompt restored.")
            selected2 = "Edit"
            st.rerun()
        else:
            st.toast("Default prompt is active.")

    if selected2 == "Download":
        # Link to download the current prompt
        epoch_time = int(time.time())
        file_name = f"quantiq_prompt_{epoch_time}.txt"
        buffer = io.StringIO(st.session_state.editor_content)
        trigger_download(buffer.getvalue(), file_name)
