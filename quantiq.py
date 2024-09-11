import os
import streamlit as st
from openai import OpenAI
from docx import Document
from markdown_pdf import MarkdownPdf, Section
import pandas as pd
import zipfile
import pdfkit


# Moderation check function
def moderation_endpoint(text):
    response = client.moderations.create(input=text)
    return response.results[0].flagged

def handle_file_upload(uploaded_file, upload_dir):
    """
    Handle the uploaded file, saving it to the specified directory.
    """
    try:
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error uploading file {uploaded_file.name}: {e}")
        return None

def handle_zipped_files(uploaded_file):
    temp_file_path = os.path.join("temp.zip")
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with zipfile.ZipFile(temp_file_path, 'r') as z:
        z.extractall(st.session_state.bulk_dir)
    st.success(f"Files successfully extracted")
    st.subheader("Extracted Files:")
    for root, dirs, files in os.walk(st.session_state.bulk_dir):
        for file in files:
            st.toast(os.path.join(root, file))
    os.remove(temp_file_path)

def oai_file_mgr(client, show = False, delete_vsf = False, delete_vss = False, delete_files = False):
    vsl,l=[],[]
    for vs in client.beta.vector_stores.list().data:
        if vs.file_counts.completed > 0:
            if show:
                print("available vector stores:",vs.id, vs.name)
            res = client.beta.vector_stores.files.list(vs.id)
            for d in res.data:
                vsl.append((d.id,d.vector_store_id,d))
                if delete_vsf and d:
                    deleted_vector_store_file = client.beta.vector_stores.files.delete(
                    vector_store_id=vs.id,
                    file_id=d.id
                )
                    print("vector store file:", deleted_vector_store_file, "deleted")
            if delete_vss:
                client.beta.vector_stores.delete(vs.id)
                print("vector store:",vs.id, vs.name, "deleted")
    for fid in client.files.list().data:
        if show:
            print("files in oai:",fid.id, fid.filename)
        if delete_files:
            print("deleting files:", fid.id, fid.filename)
            client.files.delete(fid.id)
        else:
            l.append((fid.filename,fid.id))
    df=pd.DataFrame(vsl, columns=['fid','vs_id','vs_metadata']).merge(pd.DataFrame(l, columns=['filename','fid']))
    return df[["vs_id","fid","filename","vs_metadata"]]

def markdown_to_pdf(report_text,filename,output_dir):
    """Completion text is directly converted to pdf"""
    st.session_state.file_counter += 1
    save_path=os.path.join(output_dir,filename.replace(".pdf","_quantiq_analysis")+".pdf")
    report_text="![Alt text](imgs/quantiq_logo_75x75.svg)\n"+report_text
    pdf = MarkdownPdf()
    pdf.add_section(Section(report_text, toc=False))
    pdf.save(save_path)
    print(f"analysis saved as {save_path}")

def html_to_pdf(html_content, filename, output_dir):
    save_path=os.path.join(output_dir,filename.replace(".pdf","_quantiq_analysis")+".pdf")
    style="""
        <html>
        <head>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    color: #333;
                    margin: 40px;
                }
                h1, h2 {
                    text-align: center;
                    font-family: 'Times New Roman', serif;
                    color: #000;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: right;
                }
                th {
                    background-color: #f4f4f4;
                    font-weight: bold;
                }
                .total-row {
                    font-weight: bold;
                    background-color: #eaeaea;
                }
            </style>
                """
    html_content=html_content.replace("html\n<!DOCTYPE html>\n","").replace("```","")
    logo='<p><img src="file:///C:/Users/silas/Projects/QuantIQ/imgs/quantiq_logo_75x75.svg" alt="Alt text" /></p>'
    html_content=logo+html_content.replace('<html>\n<head>\n', style)
    pdfkit.from_string(html_content, save_path, options={'enable-local-file-access': ''})

def quantiq_analysis(client,filename,input_dir=None):

    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

    print(input_dir)

    input_filepath = os.path.join(input_dir , filename)
    message_file = client.files.create(
    file = open(input_filepath, "rb"), purpose="assistants"
    )
    thread = client.beta.threads.create(
    messages=[
       {
         "role": "user",
         "content": "prepare a report",
         # Attach the new file to the message.
         "attachments": [
           { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
         ],
       }
     ]
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id = thread.id, assistant_id=assistant_id
        )
    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")
    return message_content, citations

def download_file(file_selected):
    # File path
    file_path=os.path.join(st.session_state.output_dir, file_selected)
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

def zipdir(bulk_output_dir = None):
    files = [f for f in os.listdir(bulk_output_dir) if f.endswith(".pdf")]
    zip_file_path = os.path.join(bulk_output_dir, "quantiq_results.zip")
    
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            file_path = os.path.join(bulk_output_dir, file)
            # Add file to zip without including the directory structure
            zipf.write(file_path, arcname=file)

def download_zip_file(bulk_output_dir = None):
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
        old_zip_file = os.path.join(st.session_state.bulk_output_dir, "quantiq_results.zip")
        os.remove(old_zip_file)
    except OSError:
        pass

    dirs = [st.session_state.output_dir,st.session_state.bulk_dir,st.session_state.bulk_output_dir]
    for dir_ in dirs:
        for file in os.listdir(dir_):
            file_path = os.path.join(dir_, file)
            print("deleting",file_path)
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

# Set page config
st.set_page_config(page_title="QUANT-IQ: Quantitative Analysis Tool for Intelligent Financial Review", 
                   layout="centered",
                    page_icon="cyclone", # "chart_with_upwards_trend",
                   menu_items={
                       'Get Help': 'https://sieverett.github.io/QuantIQ/',
                       'Report a bug': "https://github.com/sieverett/QuantIQ/issues/new",
                       'About': "# This is a header. This is an *extremely* cool app!"
                   }
                   )


# Apply custom CSS
st.markdown("""
    <style>
        #MainMenu {visibility: visible}
        .stDeployButton {display:none;}
        #header {visibility: hidden}
        #footer {visibility: hidden}
        #stDecoration {display:none;}
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state(defaults):
    """
    Initialize Streamlit session state variables if they don't already exist.
    
    Args:
    defaults (dict): A dictionary of session state variable names and their default values.
    """
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

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
    "bulk_output_dir": "bulk_output"
}

initialize_session_state(defaults)

# Ensure directories exist
os.makedirs(st.session_state.bulk_dir, exist_ok=True)
os.makedirs(st.session_state.output_dir, exist_ok=True)
os.makedirs(st.session_state.bulk_output_dir, exist_ok=True)

# Title

with st.container():
    col1,col2=st.columns([2, 10],gap="small")
    with col1:
        st.image(os.path.join(st.session_state.img_dir,"quantiq_logo_75x75.jpg"))
    with col2:
        st.title("QUANT-IQ")
    st.subheader("Financial Statement Analyzer")

    # UI for file upload
    file_upload_box = st.empty()

    if not st.session_state["bulk_file_uploaded"]:
        st.session_state["files"] = file_upload_box.file_uploader("Upload your documents to begin (.zip, .pdf or .docx)", 
                                                                  accept_multiple_files=True, 
                                                                  type=["zip","pdf","docx"],
                                                                  help="Start by uploading your financial documents in ZIP, PDF, or DOCX format.")
        if st.session_state["files"] !=[]:
            for uploaded_file in st.session_state["files"]:
                if uploaded_file.type == 'application/x-zip-compressed':
                    handle_zipped_files(uploaded_file)
                else:
                    file_path = handle_file_upload(uploaded_file, st.session_state.bulk_dir)
                    if file_path:
                        st.success(f"{uploaded_file.name} uploaded successfully!")

            st.session_state["bulk_file_uploaded"] = True
            st.write("Files uploaded successfully!")
            st.session_state["reset_clicked"] = False
            st.rerun()

    if st.session_state["bulk_file_uploaded"] and st.session_state["files"] != []:

        uploaded_files_=os.listdir(st.session_state.bulk_dir)
        bad_files=[f for f in uploaded_files_ if ".pdf" not in f and ".docx" not in f]
        if bad_files:
            st.error(f"Only .pdf and .docx files will be analyzed. The following file(s) are not supported: {bad_files}")
        button_label = "Analyze Files" if len(uploaded_files_) > 1 else "Analyze File"
        if st.button(button_label, type="primary"):    
            progress_text = "Analyzing: "
            my_bar = st.progress(0, text=progress_text)

            files_to_process = [f for f in os.listdir(st.session_state.bulk_dir) if ".pdf" in f or ".docx" in f]
            num_files=len(files_to_process)
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            with st.spinner("Analyzing..."):
                for idx,filename in enumerate(files_to_process):
                    idx+=1
                    my_bar.progress(idx / num_files, text=progress_text + filename)
                    message_content, citations = quantiq_analysis(client,filename,
                                                                          input_dir=st.session_state.bulk_dir)
                    print(message_content,citations)
                    html_to_pdf(message_content.value+"\n".join(citations),
                                    filename=filename,
                                    output_dir=st.session_state.bulk_output_dir)
                    oai_file_mgr(client, show = False, delete_vsf = False, delete_vss = True, delete_files = True)
            st.success('Done!')

            if len(os.listdir(st.session_state.bulk_output_dir)) > 0:
                zipdir(bulk_output_dir = st.session_state.bulk_output_dir)

            st.session_state.bulk_file_uploaded = False
            st.session_state["files"] = []
            st.session_state.reset_clicked = False

    col1,col2=st.columns([6,1])

    with col1:
        if not st.session_state.reset_clicked and len(os.listdir(st.session_state.bulk_dir)) > 0:
            if st.button("Reset",type="secondary"):
                reset_run()
                st.rerun()

    with col2:
        if os.path.isfile(os.path.join(st.session_state.bulk_output_dir, 'quantiq_results.zip')):
            download_zip_file(bulk_output_dir=st.session_state.bulk_output_dir)