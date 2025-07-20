#!/usr/bin/env python3
"""
Entry point for OkuoAgent Streamlit application
This script handles the proper import paths for the reorganized project structure
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the Streamlit app
from streamlit_apps.data_analysis_streamlit_app import main

if __name__ == "__main__":
    main() 