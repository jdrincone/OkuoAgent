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
    
    /* File upload button styling */
    .stFileUploader > div > div > div > button {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader > div > div > div > button:hover {
        background-color: var(--dark-green) !important;
        border-color: var(--dark-green) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(28, 128, 116, 0.3) !important;
    }
    
    /* File uploader container styling */
    .stFileUploader > div {
        border: 2px dashed var(--primary-color) !important;
        border-radius: 12px !important;
        background-color: var(--very-light-green) !important;
    }
    
    /* Selectbox and other form elements */
    .stSelectbox > div > div > div > div {
        border-color: var(--light-green) !important;
    }
    
    .stSelectbox > div > div > div > div:hover {
        border-color: var(--primary-color) !important;
    }
    
    /* Remove any red backgrounds from file items */
    .stFileUploader > div > div > div > div > div[data-testid="stFileUploaderFile"] {
        background-color: var(--very-light-green) !important;
        border-color: var(--light-green) !important;
    }
    
    /* Override any red elements */
    [style*="background-color: rgb(220, 53, 69)"], 
    [style*="background-color: #dc3545"],
    [style*="background-color: red"] {
        background-color: var(--primary-color) !important;
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
    
    /* File upload styling */
    .stFileUploader {
        border: 2px dashed var(--primary-color);
        border-radius: 12px;
        padding: 2rem;
        background: var(--very-light-green);
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
        <p style="font-size: 1.2rem; margin: 0;">Análisis Inteligente de Datos</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state for session management
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = None
        st.session_state.session_start_time = None

    # Load data dictionary
    try:
        with open(config.DATA_DICTIONARY_PATH, 'r') as f:
            data_dictionary = json.load(f)
    except FileNotFoundError:
        st.warning(f"Data dictionary file not found at {config.DATA_DICTIONARY_PATH}. Creating empty dictionary.")
        data_dictionary = {}

    tab1, tab2, tab3, tab4 = st.tabs(["📁 Gestión de Datos", "🗄️ Conexión a Base de Datos", "💬 Chat Inteligente", "🔧 Depuración"])

    with tab1:
        st.markdown("""
        <div class="professional-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">📁 Gestión de Datos</h2>
            <p style="color: var(--dark-green); font-size: 1.1rem;">Sube tus archivos de datos o selecciona tablas de la base de datos para comenzar el análisis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current selected data
        has_selected_data = False
        selected_data_info = []
        
        # Check for file-based data
        if 'selected_files' in st.session_state and st.session_state['selected_files']:
            has_selected_data = True
            for file in st.session_state['selected_files']:
                # File-based data
                file_path = os.path.join(config.UPLOADS_DIR, file)
                if os.path.exists(file_path):
                    try:
                        if file.endswith('.csv'):
                            df = pd.read_csv(file_path)
                        elif file.endswith('.json'):
                            df = pd.read_json(file_path)
                        else:
                            continue
                        
                        selected_data_info.append({
                            "Fuente": "Archivo",
                            "Nombre": file,
                            "Filas": len(df),
                            "Columnas": len(df.columns)
                        })
                    except:
                        continue
        
        # Check for database data
        if 'selected_database_tables' in st.session_state and st.session_state['selected_database_tables']:
            has_selected_data = True
            for table in st.session_state['selected_database_tables']:
                if table == "custom_query_results":
                    if 'database_data' in st.session_state and "custom_query" in st.session_state['database_data']:
                        df = st.session_state['database_data']['custom_query']
                        selected_data_info.append({
                            "Fuente": "Consulta SQL",
                            "Nombre": "Resultados de Consulta",
                            "Filas": len(df),
                            "Columnas": len(df.columns)
                        })
                else:
                    if 'database_data' in st.session_state and table in st.session_state['database_data']:
                        df = st.session_state['database_data'][table]
                        selected_data_info.append({
                            "Fuente": "Base de Datos",
                            "Nombre": table,
                            "Filas": len(df),
                            "Columnas": len(df.columns)
                        })
        
        if has_selected_data:
            st.markdown("""
            <div class="status-success">
                <h3>🎯 Datos Seleccionados para Análisis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if selected_data_info:
                selected_df = pd.DataFrame(selected_data_info)
                st.dataframe(selected_df, use_container_width=True)
                
                if st.button("🗑️ Limpiar Todos los Datos", type="secondary", use_container_width=True):
                    if 'selected_files' in st.session_state:
                        del st.session_state['selected_files']
                    if 'database_data' in st.session_state:
                        del st.session_state['database_data']
                    st.rerun()
            
            st.divider()
        
        # File upload section
        st.markdown("""
        <div class="professional-card">
            <h3 style="color: var(--primary-color);">📤 Subir Archivos</h3>
            <p style="color: var(--dark-green);">Selecciona archivos CSV o JSON para analizar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            f"Subir archivos ({', '.join(config.ALLOWED_FILE_TYPES)})", 
            type=config.ALLOWED_FILE_TYPES, 
            accept_multiple_files=True,
            help="Arrastra y suelta tus archivos aquí o haz clic para seleccionar"
        )

        if uploaded_files:
            # Validate and save uploaded files
            for file in uploaded_files:
                # Check file type
                file_extension = file.name.split('.')[-1].lower()
                if file_extension not in config.ALLOWED_FILE_TYPES:
                    st.error(f"File type '{file_extension}' not allowed. Allowed types: {', '.join(config.ALLOWED_FILE_TYPES)}")
                    continue
                
                # Check file size
                file_size_mb = len(file.getbuffer()) / (1024 * 1024)
                if file_size_mb > config.MAX_FILE_SIZE_MB:
                    st.error(f"File {file.name} is too large ({file_size_mb:.2f}MB). Maximum size: {config.MAX_FILE_SIZE_MB}MB")
                    continue
                
                # Save file
                with open(os.path.join(config.UPLOADS_DIR, file.name), "wb") as f:
                    f.write(file.getbuffer())
            st.success("Files uploaded successfully!")

        # Get list of available files
        available_files = [f for f in os.listdir(config.UPLOADS_DIR) if any(f.endswith(f'.{ext}') for ext in config.ALLOWED_FILE_TYPES)]

        if available_files:
            # File selection
            selected_files = st.multiselect(
                "Select files to analyze",
                available_files,
                key="selected_files"
            )
            
            # Initialize database data in session state if not exists
            if 'database_data' not in st.session_state:
                st.session_state['database_data'] = {}
            if 'selected_database_tables' not in st.session_state:
                st.session_state['selected_database_tables'] = []
            
            # Dictionary to store new descriptions
            new_descriptions = {}
            
            if selected_files:
                # Create tabs for each selected file
                file_tabs = st.tabs(selected_files)
                
                # Display dataframe previews and data dictionary info in tabs
                for tab, filename in zip(file_tabs, selected_files):
                    with tab:
                        try:
                            file_path = os.path.join(config.UPLOADS_DIR, filename)
                            if filename.endswith('.csv'):
                                df = pd.read_csv(file_path)
                            elif filename.endswith('.json'):
                                df = pd.read_json(file_path)
                            else:
                                logger.warning(f"Unsupported file type for {filename}")
                                continue
                            st.write(f"Preview of {filename}:")
                            st.dataframe(df.head())
                            
                            # Display/edit data dictionary information
                            st.subheader("Dataset Information")
                            
                            if filename in data_dictionary:
                                info = data_dictionary[filename]
                                current_description = info.get('description', '')
                            else:
                                current_description = ''
                                
                            new_descriptions[filename] = st.text_area(
                                "Dataset Description",
                                value=current_description,
                                key=f"description_{filename}",
                                help="Provide a description of this dataset"
                            )
                            
                            if filename in data_dictionary:
                                info = data_dictionary[filename]
                                
                                if 'coverage' in info:
                                    st.write(f"**Coverage:** {info['coverage']}")
                                    
                                if 'features' in info:
                                    st.write("**Features:**")
                                    for feature in info['features']:
                                        st.write(f"- {feature}")
                                        
                                if 'usage' in info:
                                    st.write("**Usage:**")
                                    if isinstance(info['usage'], list):
                                        for use in info['usage']:
                                            st.write(f"- {use}")
                                    else:
                                        st.write(f"- {info['usage']}")
                                        
                                if 'linkage' in info:
                                    st.write(f"**Linkage:** {info['linkage']}")
                                    
                        except Exception as e:
                            logger.warning(f"Error loading {filename}: {str(e)}")
                            st.warning(f"⚠️ Could not load preview for {filename}")
                
                # Save button for descriptions
                if st.button("Save Descriptions"):
                    for filename, description in new_descriptions.items():
                        if description:  # Only update if description is not empty
                            if filename not in data_dictionary:
                                data_dictionary[filename] = {}
                            data_dictionary[filename]['description'] = description
                    
                    # Save updated data dictionary
                    with open(config.DATA_DICTIONARY_PATH, 'w') as f:
                        json.dump(data_dictionary, f, indent=4)
                    st.success("Descriptions saved successfully!")
                    
        else:
            st.info("No CSV files available. Please upload some files first.")

    with tab2:
        st.markdown("""
        <div class="professional-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">🗄️ Conexión a Base de Datos</h2>
            <p style="color: var(--dark-green); font-size: 1.1rem;">Conecta con tu base de datos y selecciona las tablas que deseas analizar.</p>
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
            # Simplified interface for non-technical users
            st.markdown("""
            <div class="professional-card">
                <h3 style="color: var(--primary-color);">📊 Selecciona una Tabla para Analizar</h3>
                <p style="color: var(--dark-green);">Elige una tabla de tu base de datos para comenzar el análisis inteligente.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-load tables on page load
            if 'tables_loaded' not in st.session_state:
                st.session_state['tables_loaded'] = False
            
            if not st.session_state['tables_loaded'] or st.button("🔄 Actualizar Tablas", type="secondary", use_container_width=True):
                with st.spinner("🔄 Conectando y cargando tablas disponibles..."):
                    # Test connection first
                    if db_service.test_connection():
                        tables = db_service.get_tables()
                        st.session_state['available_tables'] = tables
                        st.session_state['tables_loaded'] = True
                        if tables:
                            st.success(f"✅ Conexión exitosa - {len(tables)} tablas encontradas")
                        else:
                            st.warning("⚠️ No se encontraron tablas en la base de datos")
                    else:
                        st.error("❌ No se pudo conectar a la base de datos")
                        st.session_state['available_tables'] = []
                        st.session_state['tables_loaded'] = True
            
            # Table selection
            tables = st.session_state.get('available_tables', [])
            if tables:
                st.info(f"📋 {len(tables)} tablas disponibles")
                
                selected_table = st.selectbox(
                    "🗂️ Selecciona una tabla:", 
                    tables,
                    help="Elige una tabla de tu base de datos para analizar"
                )
                
                if selected_table:
                    # Get basic table info
                    table_info = db_service.get_table_info(selected_table)
                    
                    if table_info:
                        # Check if this table is already loaded for analysis
                        is_table_loaded = (
                            'selected_database_tables' in st.session_state and 
                            selected_table in st.session_state['selected_database_tables']
                        )
                        
                        # Show simple status indicator
                        if is_table_loaded:
                            st.success(f"✅ Tabla '{selected_table}' lista para análisis")
                        else:
                            st.info(f"📋 Tabla seleccionada: {selected_table}")
                        
                        # Simple metrics
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📊 Filas", f"{table_info.get("row_count", 0):,}")
                        with col2:
                            st.metric("📝 Columnas", len(table_info.get("columns", [])))
                        
                        # Show different button based on status
                        if is_table_loaded:
                            if st.button("🔄 Recargar Tabla", type="secondary", use_container_width=True):
                                with st.spinner(f"🔄 Recargando tabla '{selected_table}'..."):
                                    df = db_service.load_table_as_dataframe(selected_table)
                                    if df is not None:
                                        st.session_state['selected_database_tables'] = [selected_table]
                                        st.session_state['database_data'] = {selected_table: df}
                                        st.success(f"✅ Tabla '{selected_table}' recargada")
                                        st.rerun()
                                    else:
                                        logger.warning(f"Failed to reload table: {selected_table}")
                                        st.error("❌ No se pudo recargar la tabla")
                        else:
                            # Load table for analysis button
                            if st.button("🎯 Analizar esta Tabla", type="primary", use_container_width=True):
                                with st.spinner(f"🔄 Cargando tabla '{selected_table}' para análisis..."):
                                    df = db_service.load_table_as_dataframe(selected_table)
                                    if df is not None:
                                        st.session_state['selected_database_tables'] = [selected_table]
                                        st.session_state['database_data'] = {selected_table: df}
                                        st.success(f"✅ Tabla '{selected_table}' cargada para análisis")
                                        st.rerun()
                                    else:
                                        logger.warning(f"Failed to load table for analysis: {selected_table}")
                                        st.error("❌ No se pudo cargar la tabla para análisis")
            else:
                st.info("📋 No hay tablas disponibles. Verifica la conexión a la base de datos.")

    with tab3:
        st.markdown("""
        <div class="professional-card">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem;">💬 Chat Inteligente</h2>
            <p style="color: var(--dark-green); font-size: 1.1rem;">Interactúa con tu agente de IA para analizar datos, crear visualizaciones y obtener insights.</p>
        </div>
        """, unsafe_allow_html=True)
        
        def on_submit_user_query():
            try:
                user_query = st.session_state['user_input']
                input_data_list = []
                
                # Handle file-based data
                if 'selected_files' in st.session_state:
                    for file in st.session_state['selected_files']:
                        try:
                            input_data_list.append(InputData(
                                variable_name=f"{file.split('.')[0]}", 
                                data_path=os.path.abspath(os.path.join(config.UPLOADS_DIR, file)), 
                                data_description=data_dictionary.get(file, {}).get('description', '')
                            ))
                        except Exception as e:
                            logger.warning(f"Error processing file {file}: {str(e)}")
                            continue
                
                # Handle database data
                if 'selected_database_tables' in st.session_state:
                    for table in st.session_state['selected_database_tables']:
                        try:
                            if table == "custom_query_results":
                                if 'database_data' in st.session_state and "custom_query" in st.session_state['database_data']:
                                    df = st.session_state['database_data']['custom_query']
                                    temp_path = os.path.join(config.UPLOADS_DIR, "custom_query_temp.csv")
                                    df.to_csv(temp_path, index=False)
                                    input_data_list.append(InputData(
                                        variable_name="custom_query_results",
                                        data_path=os.path.abspath(temp_path),
                                        data_description="Custom SQL query results"
                                    ))
                            else:
                                if 'database_data' in st.session_state and table in st.session_state['database_data']:
                                    df = st.session_state['database_data'][table]
                                    temp_path = os.path.join(config.UPLOADS_DIR, f"{table}_temp.csv")
                                    df.to_csv(temp_path, index=False)
                                    input_data_list.append(InputData(
                                        variable_name=table,
                                        data_path=os.path.abspath(temp_path),
                                        data_description=f"Database table: {table}"
                                    ))
                        except Exception as e:
                            logger.warning(f"Error processing database table {table}: {str(e)}")
                            continue
                
                # Only proceed if we have data to analyze
                if input_data_list:
                    st.session_state.visualisation_chatbot.user_sent_message(user_query, input_data=input_data_list)
                else:
                    logger.warning("No valid data found for analysis")
                    
            except Exception as e:
                logger.error(f"Error in on_submit_user_query: {str(e)}")
                # Don't show error to user, just log it

        has_data_for_analysis = (
            ('selected_files' in st.session_state and st.session_state['selected_files']) or
            ('selected_database_tables' in st.session_state and st.session_state['selected_database_tables'])
        )
        
        if has_data_for_analysis:
            # Initialize chatbot with session management
            if 'visualisation_chatbot' not in st.session_state:
                # Create new session if needed
                if st.session_state.user_session_id is None:
                    st.session_state.user_session_id = str(uuid.uuid4())
                    st.session_state.session_start_time = time.time()
                    logger.info(f"Created new user session: {st.session_state.user_session_id}")
                
                st.session_state.visualisation_chatbot = PythonChatbot(session_id=st.session_state.user_session_id)
            
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
                                    with open(os.path.join(config.IMAGES_DIR, image_path), "rb") as f:
                                        fig = pickle.load(f)
                                    # Use unique key to avoid duplicate ID errors
                                    unique_key = f"plot_{msg_index}_{img_idx}_{image_path.replace('.pickle', '')}"
                                    st.plotly_chart(fig, use_container_width=True, key=unique_key)
                                except FileNotFoundError:
                                    # Silently handle missing files - don't show error to user
                                    continue
                                except Exception as e:
                                    # Log error but don't show to user
                                    logger.warning(f"Error loading image {image_path}: {str(e)}")
                                    continue
            st.chat_input(
                placeholder="Pregúntame cualquier cosa sobre tus datos...", 
                on_submit=on_submit_user_query, 
                key='user_input'
            )
        else:
            st.markdown("""
            <div class="status-info">
                <h3>📋 Sin Datos Seleccionados</h3>
                <p>Por favor, selecciona archivos o tablas de base de datos en la pestaña "Gestión de Datos" para comenzar el análisis.</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
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