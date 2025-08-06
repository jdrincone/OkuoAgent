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
        st.sidebar.markdown(f"""
        <div style="
            background-color: {config.CORPORATE_COLORS[0]};
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        ">
            ✅ Sesión Activa
        </div>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        return True
    
    # Custom CSS for corporate colors
    st.markdown(f"""
    <style>
    /* Override Streamlit button colors with corporate colors */
    .stButton > button[kind="primary"] {{
        background-color: {config.CORPORATE_COLORS[0]} !important;
        border-color: {config.CORPORATE_COLORS[0]} !important;
        color: white !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {config.CORPORATE_COLORS[2]} !important;
        border-color: {config.CORPORATE_COLORS[2]} !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background-color: {config.CORPORATE_COLORS[4]} !important;
        border-color: {config.CORPORATE_COLORS[3]} !important;
        color: {config.CORPORATE_COLORS[2]} !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: {config.CORPORATE_COLORS[3]} !important;
        border-color: {config.CORPORATE_COLORS[0]} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Login form with corporate styling
    st.sidebar.markdown(f"""
    <div style="
        background-color: {config.CORPORATE_COLORS[0]};
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(28, 128, 116, 0.3);
    ">
        <h3 style="color: white; margin: 0; font-weight: bold;">🔐 Inicio de Sesión</h3>
        <p style="color: white; margin: 0.5rem 0 0 0; opacity: 0.9;">OkuoAgent</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Password input
    password = st.sidebar.text_input(
        "Contraseña", 
        type="password", 
        placeholder="Ingrese su contraseña",
        help="Contraseña por defecto: Pregunar a JuanDa"
    )
    
    # Login button
    if st.sidebar.button("🚀 Iniciar Sesión", type="primary", use_container_width=True):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.sidebar.markdown(f"""
            <div style="
                background-color: {config.CORPORATE_COLORS[0]};
                color: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            ">
                ✅ ¡Bienvenido a OkuoAgent!
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
        else:
            st.sidebar.markdown(f"""
            <div style="
                background-color: {config.CORPORATE_COLORS[2]};
                color: white;
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
            ">
                ❌ Contraseña Incorrecta
            </div>
            """, unsafe_allow_html=True)
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