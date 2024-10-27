# quantiq/logo_manager.py

import os
import logging
import streamlit as st
from PIL import Image
from io import BytesIO
import base64
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def load_image(LOGO_FILENAME, img_dir="imgs"):
    """
    Load the current logo image. If a new logo has been uploaded, it uses that.
    Otherwise, it loads the default logo from the specified directory.

    Args:
        LOGO_FILENAME (str): Name of the logo file.
        img_dir (str): Directory where logo images are stored.

    Returns:
        Image: PIL Image object or None if failed.
    """
    logo_path = os.path.join(img_dir, LOGO_FILENAME)
    if os.path.exists(logo_path):
        try:
            image = Image.open(logo_path)
            logger.info(f"Loaded logo image: {logo_path}")
            return image
        except Exception as e:
            st.error(f"Error loading the logo image: {e}")
            logger.error(f"Error loading the logo image {logo_path}: {e}")
            return None
    else:
        st.error("Default logo not found!")
        logger.error(f"Default logo not found at {logo_path}.")
        return None


def render_logo():
    """
    Renders the logo in the Streamlit app and handles logo updates.
    """
    image = load_image(LOGO_FILENAME=st.session_state["current_logo"])
    if image is None:
        st.error(f"Error: Unable to load the image {st.session_state['current_logo']}.")
        return

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

    # Handle logo update
    if st.query_params.get("logo_clicked") == "true":
        st.write("")
        st.info("Upload .jpg logo to replace the current logo.")
        uploaded_file = st.file_uploader(" - ", type=["jpg"], key="file_uploader_logo")

        if uploaded_file is not None:
            try:
                save_path = os.path.join("imgs", st.session_state["current_logo"])
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state["logo_clicked"] = False
                st.experimental_rerun()
                logger.info(f"Logo updated to {st.session_state['current_logo']}.")
            except Exception as e:
                st.error(f"Error saving the new logo: {e}")
                logger.error(f"Error saving the new logo: {e}")

    # Restore default logo
    if st.session_state["current_logo"] == "user_logo.jpg":
        if st.button("Reset Logo"):
            default_logo = "quantiq_logo_75x75.jpg"
            source_path = os.path.join(st.session_state.img_dir, default_logo)
            dest_path = os.path.join(st.session_state.img_dir, "user_logo.jpg")
            try:
                shutil.copy(source_path, dest_path)
                st.session_state["current_logo"] = default_logo
                st.experimental_rerun()
                logger.info("Logo reset to default.")
            except Exception as e:
                st.error(f"Error resetting the logo: {e}")
                logger.error(f"Error resetting the logo: {e}")
