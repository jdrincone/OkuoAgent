import streamlit as st
import sys
import os

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import config
from utils.config_validator import ConfigValidator
from utils.logger import logger
from streamlit_apps.pages.login import check_login

def main():
    logger.info("Starting OkuoAgent application")

    # Validate configuration
    validation_results = ConfigValidator.validate_all()
    if ConfigValidator.has_errors(validation_results):
        error_msg = ConfigValidator.format_errors(validation_results)
        logger.error(f"Configuration validation failed: {error_msg}")
        st.error("Configuration Errors Found:")
        st.markdown(error_msg)
        st.stop()
    else:
        logger.info("Configuration validation passed")

    # Set Streamlit configuration
    st.set_page_config(
        layout="wide", 
        page_title=config.STREAMLIT_PAGE_TITLE, 
        page_icon=config.STREAMLIT_PAGE_ICON
    )

    # Check authentication
    check_login()

    # Import and run the visualization agent directly
    try:
        from streamlit_apps.pages.python_visualisation_agent import main as viz_main
        viz_main()
    except Exception as e:
        st.error(f"Error loading visualization agent: {str(e)}")
        logger.error(f"Error loading visualization agent: {str(e)}")

if __name__ == "__main__":
    main()
