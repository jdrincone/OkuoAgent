"""
Componente para gestión de depuración.
Maneja la información de debugging y salidas intermedias.
"""

import streamlit as st
from .styles import render_professional_card, render_status_info


def render_debug_tab():
    """Renderiza la pestaña completa de depuración."""
    render_professional_card(
        "🔧 Depuración",
        "Información técnica para desarrolladores y debugging."
    )
    
    if has_chatbot():
        render_debug_info()
    else:
        render_no_debug_info()


def render_debug_info():
    """Renderiza la información de debugging cuando hay chatbot disponible."""
    render_professional_card(
        "📊 Salidas Intermedias",
        "Información detallada del procesamiento del chatbot."
    )
    
    chatbot = get_chatbot()
    if chatbot and hasattr(chatbot, 'intermediate_outputs'):
        for i, output in enumerate(chatbot.intermediate_outputs):
            with st.expander(f"Paso {i+1}", expanded=False):
                if 'thought' in output:
                    st.markdown("### 💭 Proceso de Pensamiento")
                    st.markdown(output['thought'])
                if 'code' in output:
                    st.markdown("### 💻 Código")
                    st.code(output['code'], language="python")
                if 'output' in output:
                    st.markdown("### 📤 Salida")
                    st.text(output['output'])
                else:
                    st.markdown("### 📤 Salida")
                    st.text(output)


def render_no_debug_info():
    """Renderiza mensaje cuando no hay información de debugging."""
    render_status_info(
        "📋 Sin Información de Depuración",
        "Inicia una conversación para ver las salidas intermedias del sistema."
    )


def get_chatbot():
    """Obtiene la instancia del chatbot desde el estado de la sesión."""
    return st.session_state.get('visualisation_chatbot', None)


def has_chatbot():
    """Verifica si existe una instancia del chatbot."""
    return 'visualisation_chatbot' in st.session_state


def render_session_info():
    """Renderiza información de la sesión actual."""
    if 'user_session_id' in st.session_state and st.session_state.user_session_id:
        render_professional_card(
            "🔑 Información de Sesión",
            f"ID de Sesión: {st.session_state.user_session_id}"
        )
        
        if 'session_start_time' in st.session_state and st.session_state.session_start_time:
            import time
            elapsed_time = time.time() - st.session_state.session_start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            
            st.info(f"⏱️ Tiempo de sesión: {hours:02d}:{minutes:02d}:{seconds:02d}")


def render_data_info():
    """Renderiza información sobre los datos cargados."""
    if 'database_data' in st.session_state and st.session_state['database_data']:
        render_professional_card(
            "📊 Información de Datos",
            f"Tablas cargadas: {', '.join(st.session_state['database_data'].keys())}"
        )
        
        for table_name, df in st.session_state['database_data'].items():
            if df is not None:
                st.info(f"📋 {table_name}: {len(df)} filas, {len(df.columns)} columnas") 