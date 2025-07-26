"""
Página principal del agente de visualización Python - Versión Refactorizada.
Utiliza componentes modulares para separar la lógica de presentación.
"""

import streamlit as st
import sys
import os

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar componentes modulares
from streamlit_apps.components import (
    # Styles
    apply_corporate_theme,
    load_corporate_styles,
    render_main_title,
    render_professional_card,
    
    # Data Manager
    initialize_session_state,
    create_uploads_directory,
    check_database_service,
    load_produccion_aliar_data,
    has_data_for_analysis,
    get_produccion_aliar_data,
    render_data_status,
    render_reload_button,
    render_no_data_message,
    render_database_unavailable_message,
    render_database_error_message,
    
    # Chat Manager
    initialize_chatbot,
    render_chat_interface,
    
    # KPI Manager
    render_kpis_section,
    
    # Debug Manager
    render_debug_tab
)


def main():
    """Función principal de la aplicación - Versión refactorizada."""
    
    # Inicializar estado de sesión
    initialize_session_state()
    
    # Crear directorio de uploads
    create_uploads_directory()
    
    # Aplicar tema corporativo
    apply_corporate_theme()
    load_corporate_styles()
    
    # Renderizar título principal
    render_main_title()
    
    # Verificar servicio de base de datos
    db_available, db_service = check_database_service()
    
    # Crear pestañas
    tab1, tab2 = st.tabs(["💬 Dashboard Inteligente", "🔧 Depuración"])
    
    with tab1:
        # Renderizar tarjeta de introducción
        render_professional_card(
            "💬 Dashboard Inteligente",
            "Interactúa con tus datos de producción y calidad en tiempo real. Okuo-Agent convierte métricas en respuestas, tendencias en decisiones y gráficos en insights claros. No solo ves lo que pasó: entiendes lo que significa y lo que viene."
        )
        
        if db_available:
            # Cargar datos de produccion_aliar
            load_produccion_aliar_data(db_service)
            
            # Verificar si hay datos para análisis
            if has_data_for_analysis():
                # Renderizar estado de datos
                render_data_status()
                
                # Renderizar botón de recarga
                render_reload_button(db_service)
                
                st.divider()
                
                # Obtener datos y renderizar KPIs
                df = get_produccion_aliar_data()
                render_kpis_section(df)
                
                # Inicializar chatbot
                initialize_chatbot()
                
                # Renderizar interfaz de chat
                render_chat_interface()
            else:
                render_no_data_message()
        else:
            render_database_error_message()
    
    with tab2:
        # Renderizar pestaña de depuración
        render_debug_tab()


if __name__ == "__main__":
    main() 