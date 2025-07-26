"""
Componente para gestión del chat.
Maneja la interfaz de chat, el chatbot y la visualización de mensajes.
"""

import streamlit as st
import os
import pickle
import uuid
import time
from langchain_core.messages import HumanMessage, AIMessage
from core.backend import PythonChatbot, InputData
from config import config
from utils.logger import logger


def initialize_chatbot():
    """Inicializa el chatbot con gestión de sesión."""
    if 'visualisation_chatbot' not in st.session_state:
        # Create new session if needed
        if st.session_state.user_session_id is None:
            st.session_state.user_session_id = str(uuid.uuid4())
            st.session_state.session_start_time = time.time()
            logger.info(f"Created new user session: {st.session_state.user_session_id}")
        
        st.session_state.visualisation_chatbot = PythonChatbot(session_id=st.session_state.user_session_id)


def on_submit_user_query():
    """Función de envío de consulta del usuario."""
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


def render_chat_interface():
    """Renderiza la interfaz de chat completa."""
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
    
    # Chat input
    st.chat_input(
        placeholder="Pregúntame cualquier cosa sobre los datos de producción...", 
        on_submit=on_submit_user_query, 
        key='user_input'
    )


def get_chatbot():
    """Obtiene la instancia del chatbot."""
    return st.session_state.get('visualisation_chatbot', None)


def has_chatbot():
    """Verifica si existe una instancia del chatbot."""
    return 'visualisation_chatbot' in st.session_state 