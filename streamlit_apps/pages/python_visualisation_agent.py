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

    st.title(config.STREAMLIT_PAGE_TITLE)

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

    tab1, tab2, tab3, tab4 = st.tabs(["Data Management", "Database Connection", "Chat Interface", "Debug"])

    with tab1:
        st.header("📁 Data Management")
        
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
                            "Source": "File",
                            "Name": file,
                            "Rows": len(df),
                            "Columns": len(df.columns)
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
                            "Source": "Custom Query",
                            "Name": "Query Results",
                            "Rows": len(df),
                            "Columns": len(df.columns)
                        })
                else:
                    if 'database_data' in st.session_state and table in st.session_state['database_data']:
                        df = st.session_state['database_data'][table]
                        selected_data_info.append({
                            "Source": "Database",
                            "Name": table,
                            "Rows": len(df),
                            "Columns": len(df.columns)
                        })
        
        if has_selected_data:
            st.subheader("🎯 Currently Selected Data")
            
            if selected_data_info:
                selected_df = pd.DataFrame(selected_data_info)
                st.dataframe(selected_df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📈 Go to Analysis", type="primary"):
                        st.switch_page("streamlit_apps/pages/python_visualisation_agent.py")
                with col2:
                    if st.button("🗑️ Clear All Data"):
                        if 'selected_files' in st.session_state:
                            del st.session_state['selected_files']
                        if 'database_data' in st.session_state:
                            del st.session_state['database_data']
                        st.rerun()
            
            st.divider()
        
        # File upload section
        uploaded_files = st.file_uploader(
            f"Upload files ({', '.join(config.ALLOWED_FILE_TYPES)})", 
            type=config.ALLOWED_FILE_TYPES, 
            accept_multiple_files=True
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
        st.header("🗄️ Database Connection")
        
        # Import database service
        try:
            from services.database_service import db_service
            db_available = True
        except ImportError:
            logger.warning("Database service not available. Please install required dependencies.")
            st.warning("⚠️ Database functionality not available. Please install required dependencies.")
            db_available = False
            db_service = None
        
        if db_available:
            # Simplified interface for non-technical users
            st.markdown("### 📊 Selecciona una tabla para analizar")
            
            # Auto-load tables on page load
            if 'tables_loaded' not in st.session_state:
                st.session_state['tables_loaded'] = False
            
            if not st.session_state['tables_loaded'] or st.button("🔄 Actualizar tablas", type="secondary"):
                with st.spinner("Cargando tablas disponibles..."):
                    # Test connection first
                    if db_service.test_connection():
                        tables = db_service.get_tables()
                        st.session_state['available_tables'] = tables
                        st.session_state['tables_loaded'] = True
                        if tables:
                            st.success(f"✅ Se encontraron {len(tables)} tablas")
                        else:
                            st.warning("⚠️ No se encontraron tablas en la base de datos")
                    else:
                        st.error("❌ No se pudo conectar a la base de datos")
                        st.session_state['available_tables'] = []
                        st.session_state['tables_loaded'] = True
            
            # Table selection
            tables = st.session_state.get('available_tables', [])
            if tables:
                st.info(f"📋 **{len(tables)} tablas disponibles**")
                
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
                        
                        # Show table summary with status indicator
                        if is_table_loaded:
                            st.success(f"✅ **Tabla '{selected_table}' lista para análisis**")
                        else:
                            st.info(f"📋 **Tabla seleccionada: {selected_table}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📊 Filas", table_info.get("row_count", 0))
                        with col2:
                            st.metric("📝 Columnas", len(table_info.get("columns", [])))
                        
                        # Show different button based on status
                        if is_table_loaded:
                            st.success("🎯 **¡Esta tabla está lista para análisis!**")
                            if st.button("🔄 Recargar tabla", type="secondary", use_container_width=True):
                                with st.spinner(f"Recargando tabla '{selected_table}'..."):
                                    df = db_service.load_table_as_dataframe(selected_table)
                                    if df is not None:
                                        st.session_state['selected_database_tables'] = [selected_table]
                                        st.session_state['database_data'] = {selected_table: df}
                                        st.success(f"✅ ¡Tabla '{selected_table}' recargada exitosamente!")
                                        st.rerun()
                                    else:
                                        logger.warning(f"Failed to reload table: {selected_table}")
                                        st.error("❌ No se pudo recargar la tabla")
                        else:
                            # Load table for analysis button
                            if st.button("🎯 Analizar esta tabla", type="primary", use_container_width=True):
                                with st.spinner(f"Cargando tabla '{selected_table}' para análisis..."):
                                    df = db_service.load_table_as_dataframe(selected_table)
                                    if df is not None:
                                        st.session_state['selected_database_tables'] = [selected_table]
                                        st.session_state['database_data'] = {selected_table: df}
                                        st.success(f"✅ ¡Tabla '{selected_table}' cargada para análisis!")
                                        st.rerun()
                                    else:
                                        logger.warning(f"Failed to load table for analysis: {selected_table}")
                                        st.error("❌ No se pudo cargar la tabla para análisis")
            else:
                st.info("No hay tablas disponibles. Verifica la conexión a la base de datos.")

    with tab3:
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
            # Chat input
            st.chat_input(placeholder="Ask me anything about your data", on_submit=on_submit_user_query, key='user_input')
        else:
            st.info("Please select files to analyze in the Data Management tab first.")

    with tab4:
        if 'visualisation_chatbot' in st.session_state:
            st.subheader("Intermediate Outputs")
            for i, output in enumerate(st.session_state.visualisation_chatbot.intermediate_outputs):
                with st.expander(f"Step {i+1}"):
                    if 'thought' in output:
                        st.markdown("### Thought Process")
                        st.markdown(output['thought'])
                    if 'code' in output:
                        st.markdown("### Code")
                        st.code(output['code'], language="python")
                    if 'output' in output:
                        st.markdown("### Output")
                        st.text(output['output'])
                    else:
                        st.markdown("### Output")
                        st.text(output)
        else:
            st.info("No debug information available yet. Start a conversation to see intermediate outputs.")

if __name__ == "__main__":
    main()