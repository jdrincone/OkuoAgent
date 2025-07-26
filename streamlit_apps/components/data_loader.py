"""
Componente para gestión de datos.
Maneja la carga, validación y gestión de datos de la base de datos.
"""

import streamlit as st
import os
import pandas as pd
from config import config
from utils.logger import logger
from .styles import render_status_info, render_data_status_indicator


def initialize_session_state():
    """Inicializa el estado de la sesión para gestión de datos."""
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = None
        st.session_state.session_start_time = None

    if 'database_data' not in st.session_state:
        st.session_state['database_data'] = {}
    if 'selected_database_tables' not in st.session_state:
        st.session_state['selected_database_tables'] = []
    if 'produccion_aliar_loaded' not in st.session_state:
        st.session_state['produccion_aliar_loaded'] = False


def create_uploads_directory():
    """Crea el directorio de uploads si no existe."""
    if not os.path.exists(config.UPLOADS_DIR):
        os.makedirs(config.UPLOADS_DIR)


def check_database_service():
    """Verifica si el servicio de base de datos está disponible."""
    try:
        from services.database_service import db_service
        return True, db_service
    except ImportError:
        logger.warning("Database service not available. Please install required dependencies.")
        return False, None


def load_produccion_aliar_data(db_service):
    """Carga los datos de produccion_aliar desde la base de datos."""
    if st.session_state['produccion_aliar_loaded']:
        return True
    
    with st.spinner("🔄 Cargando datos de producción..."):
        # Test connection first
        if db_service.test_connection():
            # Try to load produccion_aliar table
            df = db_service.load_table_as_dataframe("produccion_aliar")
            if df is not None:
                st.session_state['selected_database_tables'] = ["produccion_aliar"]
                st.session_state['database_data'] = {"produccion_aliar": df}
                st.session_state['produccion_aliar_loaded'] = True
                st.success(f"✅ Datos correctamente cargados")
                return True
            else:
                st.error("❌ No se pudo cargar la tabla 'produccion_aliar'")
                st.session_state['produccion_aliar_loaded'] = True
                return False
        else:
            st.error("❌ No se pudo conectar a la base de datos")
            st.session_state['produccion_aliar_loaded'] = True
            return False


def reload_produccion_aliar_data(db_service):
    """Recarga los datos de produccion_aliar."""
    with st.spinner("🔄 Recargando datos de producción..."):
        df = db_service.load_table_as_dataframe("produccion_aliar")
        if df is not None:
            st.session_state['database_data'] = {"produccion_aliar": df}
            st.success("✅ Datos recargados exitosamente")
            st.rerun()
            return True
        else:
            st.error("❌ No se pudo recargar los datos")
            return False


def has_data_for_analysis():
    """Verifica si hay datos disponibles para análisis."""
    return (
        'selected_database_tables' in st.session_state and 
        'produccion_aliar' in st.session_state['selected_database_tables']
    )


def get_produccion_aliar_data():
    """Obtiene los datos de produccion_aliar."""
    if has_data_for_analysis():
        return st.session_state['database_data']['produccion_aliar']
    return None


def render_data_status():
    """Renderiza el estado de los datos."""
    if has_data_for_analysis():
        render_data_status_indicator()
    else:
        render_status_info(
            "📋 Sin Datos de Producción",
            "No se pudieron cargar los datos de producción. Verifica la conexión a la base de datos."
        )


def render_reload_button(db_service):
    """Renderiza el botón de recarga de datos."""
    if st.button("🔄 Recargar Datos", type="secondary", use_container_width=True):
        reload_produccion_aliar_data(db_service)


def render_no_data_message():
    """Renderiza mensaje cuando no hay datos."""
    render_status_info(
        "📋 Sin Datos de Producción",
        "No se pudieron cargar los datos de producción. Verifica la conexión a la base de datos."
    )


def render_database_unavailable_message():
    """Renderiza mensaje cuando la base de datos no está disponible."""
    render_status_info(
        "⚠️ Base de Datos No Disponible",
        "La funcionalidad de base de datos no está disponible. Verifica la configuración."
    )


def render_database_error_message():
    """Renderiza mensaje de error de base de datos."""
    render_status_info(
        "⚠️ Funcionalidad de Base de Datos No Disponible",
        "Por favor, instala las dependencias requeridas para acceder a la base de datos."
    ) 