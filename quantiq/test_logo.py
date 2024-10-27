
import streamlit as st
from PIL import Image
import os
import base64
from io import BytesIO
import cairosvg

# Define image directory and filename
IMG_DIR = "../imgs"  # Replace with your actual image directory path
# DEFAULT_LOGO_FILENAME = "user_logo.jpg"


def load_image(LOGO_FILENAME):
    """
    Load the current logo image. If a new logo has been uploaded, it uses that.
    Otherwise, it loads the default logo from the specified directory.
    """
    IMG_DIR = "../imgs"
    convert_jpg_to_svg(f"{IMG_DIR}/user_logo.jpg", f"{IMG_DIR}/user_logo.svg")
    logo_path = os.path.join(IMG_DIR, LOGO_FILENAME)
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


def render_logo(LOGO_FILENAME):
    image = load_image(LOGO_FILENAME=LOGO_FILENAME)
    if image is None:
        st.error("Error: Unable to load the image.")
    # Convert image to base64
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded_image = base64.b64encode(buffer.getvalue()).decode()
    clickable_image_html = f"""
            <a href="?logo_clicked=true">
            <img src="data:image/png;base64,{encoded_image}" alt="Logo" style="cursor: pointer; width: 95px; height: 95px;">
            </a>
    """
    st.markdown(clickable_image_html, unsafe_allow_html=True,
                help="Click logo to change")


def handle_logo():

    render_logo(st.session_state['current_logo'])

    if st.query_params['logo_clicked'] == 'true':
        st.write("")
        st.info("Upload .jpg logo to replace the current logo.")
        uploaded_file = st.file_uploader(
            " - ",
            type=["jpg"],
            key="file_uploader"
        )

        # save uploaded file and set as current logo
        if uploaded_file is not None:
            save_path = os.path.join(IMG_DIR, st.session_state['current_logo'])
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.query_params["logo_clicked"] = None
            uploaded_file = None
            st.rerun()

    # restore default logo
    if st.session_state['current_logo'] == "user_logo.jpg":
        if st.button("Reset Logo"):
            st.session_state['current_logo'] = "quantiq_logo_75x75.jpg"
            with open(os.path.join(IMG_DIR, st.session_state['current_logo']), "rb") as f:
                img = f.read()
            with open(os.path.join(IMG_DIR, 'user_logo.jpg'), "wb") as f:
                f.write(img)
            st.query_params["logo_clicked"] = None
            st.rerun()


# Initialize session state


def convert_jpg_to_svg(input_jpg_path, output_svg_path):
    # Convert the JPG to PNG first because CairoSVG works better with PNG
    img = Image.open(input_jpg_path)
    png_path = input_jpg_path.replace('.jpg', '.png')
    img.save(png_path)

    # Convert PNG to SVG using CairoSVG
    cairosvg.svg2svg(url=png_path, write_to=output_svg_path)


if 'current_logo' not in st.session_state:
    st.session_state['current_logo'] = 'user_logo.jpg'

if 'logo_clicked' not in st.query_params:
    st.query_params['logo_clicked'] = None


with st.sidebar:

    handle_logo()
