# quantiq/utils.py

import os
import shutil
import streamlit as st
from quantiq.logging_setup import set_logging

# Initialize logger
logger = set_logging()


def delete_dir_contents(directories):
    """
    Deletes the directories at the given paths and recreates them.

    Args:
        directories (list): List of directory paths to refresh.
    """
    for dir_ in directories:
        path = os.path.normpath(dir_)
        logger.info(f"Refreshing directory: {path}")
        try:
            if os.path.exists(path):
                shutil.rmtree(path)  # Delete the directory and its contents
                logger.info(f"Deleted directory: {path}")
            os.makedirs(path)  # Recreate the directory
            logger.info(f"Recreated directory: {path}")
        except Exception as e:
            logger.error(f"Error deleting or recreating directory {path}: {e}")


def reset_run():
    """
    Resets the application by deleting and recreating necessary directories and resetting session state.
    """
    try:
        directories = [
            st.session_state.output_dir,
            st.session_state.bulk_dir,
            st.session_state.bulk_output_dir,
        ]
        delete_dir_contents(directories)
        st.session_state.bulk_file_uploaded = False
        st.session_state.reset_clicked = True
        st.experimental_rerun()
        logger.info("Application run reset successfully.")
    except Exception as e:
        logger.error(f"Error in reset_run function: {e}")


def feedback():
    """
    Provides a feedback mechanism with thumbs up/down.
    """
    sentiment_mapping = [":material/thumb_down:", ":material/thumb_up:"]
    selected = st.feedback("thumbs")
    if selected is not None:
        st.markdown(f"You selected: {sentiment_mapping[selected]}")
        logger.info(f"User feedback received: {sentiment_mapping[selected]}")
