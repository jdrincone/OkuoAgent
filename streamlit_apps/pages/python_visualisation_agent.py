import streamlit as st
import pandas as pd
import os
import json
import sys

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_core.messages import HumanMessage, AIMessage
from core.backend import PythonChatbot, InputData
import pickle
from config import config
from utils.logger import logger
import uuid
import time

def main():
    """Main function for the visualization agent"""
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists(config.UPLOADS_DIR):
        os.makedirs(config.UPLOADS_DIR)

    # Apply corporate theme
    st.set_page_config(
        page_title=config.STREAMLIT_PAGE_TITLE,
        page_icon=config.STREAMLIT_PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for professional styling
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

    # Professional header
    st.markdown("""
    <div class="main-title">
        <h1>🤖 OkuoAgent</h1>
        <p style="font-size: 1.2rem; margin: 0;">Análisis Inteligente de Datos de Producción</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for session management
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = None
        st.session_state.session_start_time = None

    # Initialize database data in session state
    if 'database_data' not in st.session_state:
        st.session_state['database_data'] = {}
    if 'selected_database_tables' not in st.session_state:
        st.session_state['selected_database_tables'] = []

    tab1, tab2 = st.tabs(["💬 Dashboard Inteligente", "🔧 Depuración"])

    with tab1:
        st.markdown("""
        <div class="professional-card">
            <h3 style="color: var(--primary-color); margin-bottom: 1rem;">💬 Dashboard Inteligente</h3>
            <p style="color: var(--dark-green); font-size: 1.1rem;">Interactúa con tu agente de IA para analizar datos de producción, crear visualizaciones y obtener insights.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Import database service
        try:
            from services.database_service import db_service
            db_available = True
        except ImportError:
            logger.warning("Database service not available. Please install required dependencies.")
            st.markdown("""
            <div class="status-info">
                <h3>⚠️ Funcionalidad de Base de Datos No Disponible</h3>
                <p>Por favor, instala las dependencias requeridas para acceder a la base de datos.</p>
            </div>
            """, unsafe_allow_html=True)
            db_available = False
            db_service = None
        
        if db_available:
            # Auto-load produccion_aliar table
            if 'produccion_aliar_loaded' not in st.session_state:
                st.session_state['produccion_aliar_loaded'] = False
            
            if not st.session_state['produccion_aliar_loaded']:
                with st.spinner("🔄 Cargando datos de producción..."):
                    # Test connection first
                    if db_service.test_connection():
                        # Try to load produccion_aliar table
                        df = db_service.load_table_as_dataframe("produccion_aliar")
                        if df is not None:
                            st.session_state['selected_database_tables'] = ["produccion_aliar"]
                            st.session_state['database_data'] = {"produccion_aliar": df}
                            st.session_state['produccion_aliar_loaded'] = True
                            st.success(f"✅ Datos correctamente cargados ")
                        else:
                            st.error("❌ No se pudo cargar la tabla 'produccion_aliar'")
                            st.session_state['produccion_aliar_loaded'] = True
                    else:
                        st.error("❌ No se pudo conectar a la base de datos")
                        st.session_state['produccion_aliar_loaded'] = True
            
            # Show data status
            has_data_for_analysis = (
                'selected_database_tables' in st.session_state and 
                'produccion_aliar' in st.session_state['selected_database_tables']
            )
            
            if has_data_for_analysis:
                # Show simplified data status
                df = st.session_state['database_data']['produccion_aliar']
                
                # Compact status indicator in one line
                st.markdown("""
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px; padding: 0.5rem; background-color: #E6ECD8; border-radius: 6px; margin: 0.5rem 0; font-size: 0.9rem;">
                    <span style="color: #1A494C;">✅</span>
                    <span style="color: #1A494C; font-weight: 500;">Actualmente solo se tienen datos disponibles de la Fazenda</span>
                    <span style="color: #666666;">•</span>
                    <span style="color: #666666;">📅 En tiempo real</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Reload button
                if st.button("🔄 Recargar Datos", type="secondary", use_container_width=True):
                    with st.spinner("🔄 Recargando datos de producción..."):
                        df = db_service.load_table_as_dataframe("produccion_aliar")
                        if df is not None:
                            st.session_state['database_data'] = {"produccion_aliar": df}
                            st.success("✅ Datos recargados exitosamente")
                            st.rerun()
                        else:
                            st.error("❌ No se pudo recargar los datos")
                
                st.divider()
                
                # Display KPIs using the new service architecture
                if df is not None and len(df) > 0:
                    try:
                        # Import the new KPI service and components
                        from services.kpi_service import create_kpi_service
                        from utils.kpi_components import (
                            render_main_kpis_section, 
                            render_product_analysis_section,
                            render_period_info,
                            render_debug_info,
                            render_error_message
                        )
                        
                        # Create KPI service
                        kpi_service = create_kpi_service(df)
                        
                        # Calculate all KPIs
                        main_kpis = kpi_service.calculate_main_kpis()
                        product_kpis = kpi_service.calculate_product_kpis()
                        debug_info = kpi_service.get_debug_info()
                        period_info = kpi_service.get_period_info()
                        
                                # Debug information removed as requested
                        
                        # Display main KPIs
                        render_main_kpis_section(main_kpis)
                        
                        # Display period information
                        render_period_info(period_info)
                        
                        # Display product analysis
                        render_product_analysis_section(product_kpis)
                        
                        st.divider()
                        
                    except ValueError as e:
                        render_error_message(str(e))
                        st.info("📋 Columnas disponibles: " + ", ".join(df.columns.tolist()))
                    except Exception as e:
                        render_error_message(f"Error al calcular KPIs: {str(e)}")
                        st.exception(e)
                
                # Initialize chatbot with session management
                if 'visualisation_chatbot' not in st.session_state:
                    # Create new session if needed
                    if st.session_state.user_session_id is None:
                        st.session_state.user_session_id = str(uuid.uuid4())
                        st.session_state.session_start_time = time.time()
                        logger.info(f"Created new user session: {st.session_state.user_session_id}")
                    
                    st.session_state.visualisation_chatbot = PythonChatbot(session_id=st.session_state.user_session_id)
                
                def on_submit_user_query():
                    try:
                        user_query = st.session_state['user_input']
                        input_data_list = []
                        
                        # Always use produccion_aliar table
                        if 'produccion_aliar' in st.session_state['database_data']:
                            df = st.session_state['database_data']['produccion_aliar']
                            temp_path = os.path.join(config.UPLOADS_DIR, "produccion_aliar_temp.csv")
                            df.to_csv(temp_path, index=False)
                            input_data_list.append(InputData(
                                variable_name="produccion_aliar",
                                data_path=os.path.abspath(temp_path),
                                data_description="Datos de producción de Aliar - Información en tiempo real de la producción"
                            ))
                        
                        # Only proceed if we have data to analyze
                        if input_data_list:
                            st.session_state.visualisation_chatbot.user_sent_message(user_query, input_data=input_data_list)
                        else:
                            logger.warning("No valid data found for analysis")
                            
                    except Exception as e:
                        logger.error(f"Error in on_submit_user_query: {str(e)}")
                        # Don't show error to user, just log it
                
                chat_container = st.container(height=500)
                with chat_container:
                    # Display chat history with associated images
                    for msg_index, msg in enumerate(st.session_state.visualisation_chatbot.chat_history):
                        msg_col, img_col = st.columns([2, 1])
                        
                        with msg_col:
                            if isinstance(msg, HumanMessage):
                                st.chat_message("You").markdown(msg.content)
                            elif isinstance(msg, AIMessage):
                                with st.chat_message("AI"):
                                    st.markdown(msg.content)

                            if isinstance(msg, AIMessage) and msg_index in st.session_state.visualisation_chatbot.output_image_paths:
                                image_paths = st.session_state.visualisation_chatbot.output_image_paths[msg_index]
                                for img_idx, image_path in enumerate(image_paths):
                                    try:
                                        # Check if file exists
                                        full_path = os.path.join(config.IMAGES_DIR, image_path)
                                        if not os.path.exists(full_path):
                                            logger.warning(f"Image file not found: {full_path}")
                                            continue
                                        
                                        # Load and validate the figure
                                        with open(full_path, "rb") as f:
                                            fig = pickle.load(f)
                                        
                                        # Validate that it's a plotly figure
                                        if not hasattr(fig, 'to_dict'):
                                            logger.warning(f"Loaded object is not a plotly figure: {type(fig)}")
                                            continue
                                        
                                        # Use unique key to avoid duplicate ID errors
                                        unique_key = f"plot_{msg_index}_{img_idx}_{image_path.replace('.pickle', '')}"
                                        st.plotly_chart(fig, use_container_width=True, key=unique_key)
                                        
                                    except (FileNotFoundError, OSError) as e:
                                        # Handle file system errors
                                        logger.warning(f"File system error loading image {image_path}: {str(e)}")
                                        continue
                                    except (pickle.PickleError, EOFError) as e:
                                        # Handle pickle errors
                                        logger.warning(f"Pickle error loading image {image_path}: {str(e)}")
                                        continue
                                    except Exception as e:
                                        # Handle any other errors
                                        logger.warning(f"Unexpected error loading image {image_path}: {str(e)}")
                                        continue
                st.chat_input(
                    placeholder="Pregúntame cualquier cosa sobre los datos de producción...", 
                    on_submit=on_submit_user_query, 
                    key='user_input'
                )
            else:
                st.markdown("""
                <div class="status-info">
                    <h3>📋 Sin Datos de Producción</h3>
                    <p>No se pudieron cargar los datos de producción. Verifica la conexión a la base de datos.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-info">
                <h3>⚠️ Base de Datos No Disponible</h3>
                <p>La funcionalidad de base de datos no está disponible. Verifica la configuración.</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="professional-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">🔧 Depuración</h2>
            <p style="color: var(--dark-green); font-size: 1.1rem;">Información técnica para desarrolladores y debugging.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'visualisation_chatbot' in st.session_state:
            st.markdown("""
            <div class="professional-card">
                <h3 style="color: var(--primary-color);">📊 Salidas Intermedias</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for i, output in enumerate(st.session_state.visualisation_chatbot.intermediate_outputs):
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
        else:
            st.markdown("""
            <div class="status-info">
                <h3>📋 Sin Información de Depuración</h3>
                <p>Inicia una conversación para ver las salidas intermedias del sistema.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()