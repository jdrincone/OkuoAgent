import streamlit as st
from streamlit_apps.components.detailed_report import render_detailed_report_page

# Configuración de la página
st.set_page_config(
    page_title="📊 Informe Detallado - OkuoAgent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos corporativos
from streamlit_apps.components.styles import apply_corporate_theme, load_corporate_styles
apply_corporate_theme()
load_corporate_styles()

# Renderizar la página del informe detallado
render_detailed_report_page() 