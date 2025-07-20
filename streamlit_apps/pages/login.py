"""
Simple but Secure Login System for OkuoAgent
Uses environment variables for authentication
"""

import streamlit as st
import sys
import os

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from config import config

# Load environment variables
load_dotenv()
PASSWORD = os.getenv("STREAMLIT_PASSWORD")


def check_login():
    """Professional login check using sidebar"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # If already authenticated, show logout option
    if st.session_state.authenticated:
        st.sidebar.success("✅ Sesión activa")
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        return True
    
    # Login form with corporate styling
    st.sidebar.markdown(f"""
    <div style="
        background-color: {config.CORPORATE_COLORS[0]};
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    ">
        <h3 style="color: white; margin: 0;">🔐 Inicio de sesión</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Password input
    password = st.sidebar.text_input(
        "Contraseña", 
        type="password", 
        placeholder="Ingrese su contraseña",
        help="Contraseña por defecto: admin123"
    )
    
    # Login button
    if st.sidebar.button("🚀 Iniciar Sesión", type="primary", use_container_width=True):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.sidebar.success("✅ ¡Bienvenido!")
            st.rerun()
        else:
            st.sidebar.error("❌ Contraseña incorrecta")
            st.stop()
    
    # Cancel button
    if st.sidebar.button("❌ Cancelar", use_container_width=True):
        st.stop()
    
    
    # If not authenticated, stop here
    if not st.session_state.authenticated:
        st.stop()
    
    return True


if __name__ == "__main__":
    check_login() 