"""
Módulo de componentes para la aplicación Streamlit.
Contiene componentes modulares para separar la lógica de presentación.
"""

# Imports de estilos
from .styles import (
    apply_corporate_theme,
    load_corporate_styles,
    render_main_title,
    render_professional_card,
    render_status_info,
    render_status_success,
    render_data_status_indicator
)

# Imports de gestión de datos
from .data_loader import (
    initialize_session_state,
    create_uploads_directory,
    check_database_service,
    load_produccion_aliar_data,
    reload_produccion_aliar_data,
    has_data_for_analysis,
    get_produccion_aliar_data,
    render_data_status,
    render_reload_button,
    render_no_data_message,
    render_database_unavailable_message,
    render_database_error_message
)

# Imports de gestión del chat
from .chat import (
    initialize_chatbot,
    on_submit_user_query,
    render_chat_interface,
    get_chatbot,
    has_chatbot
)

# Imports de gestión de KPIs
from .kpi_view import (
    render_kpis_section,
    calculate_kpis,
    render_kpis_only,
    render_period_analysis_only,
    render_product_analysis_only
)

# Imports de gestión de depuración
from .debug_view import (
    render_debug_tab,
    render_debug_info,
    render_no_debug_info,
    render_session_info,
    render_data_info
)

__all__ = [
    # Styles
    'apply_corporate_theme',
    'load_corporate_styles',
    'render_main_title',
    'render_professional_card',
    'render_status_info',
    'render_status_success',
    'render_data_status_indicator',
    
    # Data Loader
    'initialize_session_state',
    'create_uploads_directory',
    'check_database_service',
    'load_produccion_aliar_data',
    'reload_produccion_aliar_data',
    'has_data_for_analysis',
    'get_produccion_aliar_data',
    'render_data_status',
    'render_reload_button',
    'render_no_data_message',
    'render_database_unavailable_message',
    'render_database_error_message',
    
    # Chat
    'initialize_chatbot',
    'on_submit_user_query',
    'render_chat_interface',
    'get_chatbot',
    'has_chatbot',
    
    # KPI View
    'render_kpis_section',
    'calculate_kpis',
    'render_kpis_only',
    'render_period_analysis_only',
    'render_product_analysis_only',
    
    # Debug View
    'render_debug_tab',
    'render_debug_info',
    'render_no_debug_info',
    'render_session_info',
    'render_data_info'
] 