"""
Componente de estilos para la aplicación Streamlit.
Contiene todos los estilos CSS y componentes visuales reutilizables.
"""

import streamlit as st
from config import config


def apply_corporate_theme():
    """Aplica el tema corporativo de la aplicación."""
    st.set_page_config(
        page_title=config.STREAMLIT_PAGE_TITLE,
        page_icon=config.STREAMLIT_PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )


def load_corporate_styles():
    """Carga los estilos CSS corporativos."""
    st.markdown("""
    <style>
    /* Corporate color variables */
    :root {
        --primary-color: #1C8074;
        --secondary-color: #666666;
        --dark-green: #1A494C;
        --light-green: #94AF92;
        --very-light-green: #E6ECD8;
        --light-gray: #C9C9C9;
    }
    
    /* Main title styling */
    .main-title {
        background-color: var(--primary-color);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(28, 128, 116, 0.3);
    }
    
    /* Professional card styling */
    .professional-card {
        background: white;
        border: 2px solid var(--very-light-green);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(28, 128, 116, 0.1);
        transition: all 0.3s ease;
    }
    
    .professional-card:hover {
        box-shadow: 0 8px 30px rgba(28, 128, 116, 0.2);
        transform: translateY(-2px);
    }
    
    /* Status indicators */
    .status-success {
        background-color: var(--primary-color);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-info {
        background-color: var(--very-light-green);
        color: var(--dark-green);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: var(--very-light-green);
        border-radius: 8px 8px 0 0;
        color: var(--dark-green);
        font-weight: bold;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Button styling - Override Streamlit defaults */
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: var(--dark-green) !important;
        border-color: var(--dark-green) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(28, 128, 116, 0.3);
    }
    
    .stButton > button[kind="secondary"] {
        background-color: var(--very-light-green) !important;
        border-color: var(--light-green) !important;
        color: var(--dark-green) !important;
        border-radius: 10px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: var(--light-green) !important;
        border-color: var(--primary-color) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(28, 128, 116, 0.3);
    }
    
    /* Fallback for any other buttons */
    .stButton > button {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--dark-green) !important;
        border-color: var(--dark-green) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(28, 128, 116, 0.3);
    }
    
    /* Selectbox and other form elements */
    .stSelectbox > div > div > div > div {
        border-color: var(--light-green) !important;
    }
    
    .stSelectbox > div > div > div > div:hover {
        border-color: var(--primary-color) !important;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: var(--very-light-green);
        border: 2px solid var(--light-green);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Chat styling */
    .chat-message {
        background: white;
        border: 1px solid var(--very-light-green);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .chat-message.user {
        background-color: var(--primary-color);
        color: white;
    }
    
    .chat-message.assistant {
        background: var(--very-light-green);
        color: var(--dark-green);
    }
    </style>
    """, unsafe_allow_html=True)


def render_main_title():
    """Renderiza el título principal de la aplicación."""
    st.markdown("""
    <div class="main-title">
        <h1>🤖 OkuoAgent</h1>
        <p style="font-size: 1.2rem; margin: 0;">Análisis Inteligente de Datos de Producción</p>
    </div>
    """, unsafe_allow_html=True)


def render_professional_card(title, content):
    """Renderiza una tarjeta profesional con título y contenido."""
    st.markdown(f"""
    <div class="professional-card">
        <h3 style="color: var(--primary-color); margin-bottom: 1rem;">{title}</h3>
        <p style="color: var(--dark-green); font-size: 1.1rem;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_status_info(title, message):
    """Renderiza un mensaje de estado informativo."""
    st.markdown(f"""
    <div class="status-info">
        <h3>{title}</h3>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_status_success(title, message):
    """Renderiza un mensaje de estado exitoso."""
    st.markdown(f"""
    <div class="status-success">
        <h3>{title}</h3>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_data_status_indicator():
    """Renderiza el indicador de estado de datos compacto."""
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 0.5rem; background-color: #E6ECD8; border-radius: 6px; margin: 0.5rem 0; font-size: 0.9rem;">
        <span style="color: #1A494C;">✅</span>
        <span style="color: #1A494C; font-weight: 500;">Actualmente solo se tienen datos disponibles de la Fazenda</span>
        <span style="color: #666666;">•</span>
        <span style="color: #666666;">📅 En tiempo real</span>
    </div>
    """, unsafe_allow_html=True) 