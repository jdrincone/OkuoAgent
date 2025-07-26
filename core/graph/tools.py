from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from typing import Annotated, Tuple
from langgraph.prebuilt import InjectedState
import sys
from io import StringIO
import os
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import pandas as pd
import sklearn
import threading
import uuid
import time
from datetime import datetime, timedelta
from config import config
from utils.logger import logger


# Importaciones automáticas para el entorno de ejecución
try:
    from utils.production_metrics import (
        compute_metric_sackoff,
        compute_metric_pdi_mean_agroindustrial,
        compute_metric_dureza_mean_agroindustrial,
        compute_metric_fino_mean_agroindustrial,
        compute_metric_diferencia_toneladas,
        filter_con_adiflow,
        filter_sin_adiflow,
        calculate_kpis,
        analyze_trends,
        detect_anomalies
    )
    PRODUCTION_METRICS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import production metrics: {e}")
    PRODUCTION_METRICS_AVAILABLE = False


# Thread-local storage for session isolation
_thread_local = threading.local()

def get_session_id() -> str:
    """Get or create a unique session ID for the current thread."""
    if not hasattr(_thread_local, 'session_id'):
        _thread_local.session_id = str(uuid.uuid4())
        _thread_local.session_start_time = time.time()
        logger.info(f"Created new session: {_thread_local.session_id}")
    return _thread_local.session_id

def get_persistent_vars() -> dict:
    """Get thread-local persistent variables for the current session."""
    session_id = get_session_id()
    if not hasattr(_thread_local, 'persistent_vars'):
        _thread_local.persistent_vars = {}
        logger.info(f"Initialized persistent variables for session: {session_id}")
    return _thread_local.persistent_vars

def cleanup_old_sessions(max_age_hours: int = 24):
    """Clean up old session data to prevent memory leaks."""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # This would be implemented in a production environment
    # For now, we'll just log the cleanup attempt
    logger.info(f"Session cleanup check - max age: {max_age_hours} hours")

def get_session_info() -> dict:
    """Get information about the current session."""
    session_id = get_session_id()
    if hasattr(_thread_local, 'session_start_time'):
        session_age = time.time() - _thread_local.session_start_time
        return {
            'session_id': session_id,
            'session_age_seconds': session_age,
            'variables_count': len(get_persistent_vars())
        }
    return {'session_id': session_id}

def create_safe_execution_environment() -> dict:
    """Create a safe execution environment with all necessary imports and utilities."""
    env = {
        # Librerías estándar de análisis de datos
        'pd': pd,
        'np': __import__('numpy'),
        'plt': __import__('matplotlib.pyplot'),
        'px': px,
        'go': go,
        'sklearn': sklearn,
        'datetime': datetime,
        'timedelta': timedelta,
        'os': __import__('os'),
        'uuid': __import__('uuid'),
        
        # Funciones de utilidad para fechas
        'pd_to_datetime': pd.to_datetime,
        'pd_date_range': pd.date_range,
    }
    
    # Agregar funciones de métricas si están disponibles
    if PRODUCTION_METRICS_AVAILABLE:
        env.update({
            'compute_metric_sackoff': compute_metric_sackoff,
            'compute_metric_pdi_mean_agroindustrial': compute_metric_pdi_mean_agroindustrial,
            'compute_metric_dureza_mean_agroindustrial': compute_metric_dureza_mean_agroindustrial,
            'compute_metric_fino_mean_agroindustrial': compute_metric_fino_mean_agroindustrial,
            'compute_metric_diferencia_toneladas': compute_metric_diferencia_toneladas,
            'filter_con_adiflow': filter_con_adiflow,
            'filter_sin_adiflow': filter_sin_adiflow,
            'calculate_kpis': calculate_kpis,
            'analyze_trends': analyze_trends,
            'detect_anomalies': detect_anomalies,
        })
    
    # Funciones de utilidad para manejo de fechas
    def safe_date_conversion(series, **kwargs):
        """Safely convert series to datetime with error handling."""
        try:
            return pd.to_datetime(series, **kwargs)
        except Exception as e:
            logger.warning(f"Date conversion error: {e}")
            return series
    
    def safe_date_filter(df, date_column, start_date=None, end_date=None):
        """Safely filter DataFrame by date range."""
        try:
            if date_column not in df.columns:
                logger.warning(f"Date column '{date_column}' not found in DataFrame")
                return df
            
            # Ensure date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            
            # Apply filters
            if start_date:
                df = df[df[date_column] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df[date_column] <= pd.to_datetime(end_date)]
            
            return df
        except Exception as e:
            logger.error(f"Date filtering error: {e}")
            return df
    
    env.update({
        'safe_date_conversion': safe_date_conversion,
        'safe_date_filter': safe_date_filter,
    })
    
    return env

plotly_saving_code = f"""import pickle
import uuid
import plotly
import pandas as pd
import numpy as np

def clean_figure_for_pickle(fig):
    \"\"\"Clean figure data to ensure it's pickle-serializable\"\"\"
    if hasattr(fig, 'data'):
        for trace in fig.data:
            # Clean x-axis data
            if hasattr(trace, 'x') and trace.x is not None:
                if isinstance(trace.x, pd.Series):
                    # Convert pandas objects to strings
                    trace.x = trace.x.astype(str)
                elif isinstance(trace.x, (list, np.ndarray)):
                    trace.x = [str(x) if hasattr(x, 'strftime') or isinstance(x, pd.Period) else x for x in trace.x]
                elif hasattr(trace.x, 'strftime'):
                    trace.x = str(trace.x)
            
            # Clean y-axis data
            if hasattr(trace, 'y') and trace.y is not None:
                if isinstance(trace.y, pd.Series):
                    # Convert pandas objects to strings
                    trace.y = trace.y.astype(str)
                elif isinstance(trace.y, (list, np.ndarray)):
                    trace.y = [str(y) if hasattr(y, 'strftime') or isinstance(y, pd.Period) else y for y in trace.y]
                elif hasattr(trace.y, 'strftime'):
                    trace.y = str(trace.y)
            
            # Clean text data if present
            if hasattr(trace, 'text') and trace.text is not None:
                if isinstance(trace.text, pd.Series):
                    trace.text = trace.text.astype(str)
                elif isinstance(trace.text, (list, np.ndarray)):
                    trace.text = [str(t) if hasattr(t, 'strftime') or isinstance(t, pd.Period) else t for t in trace.text]
            
            # Clean customdata if present
            if hasattr(trace, 'customdata') and trace.customdata is not None:
                if isinstance(trace.customdata, pd.Series):
                    trace.customdata = trace.customdata.astype(str)
                elif isinstance(trace.customdata, (list, np.ndarray)):
                    trace.customdata = [str(cd) if hasattr(cd, 'strftime') or isinstance(cd, pd.Period) else cd for cd in trace.customdata]
    
    return fig

# Save each figure in plotly_figures list
for i, fig in enumerate(plotly_figures):
    try:
        # Clean the figure for pickle serialization
        clean_fig = clean_figure_for_pickle(fig)
        
        # Generate unique filename
        filename = f"figure_{{uuid.uuid4()}}.pkl"
        filepath = os.path.join("{config.IMAGES_DIR}", filename)
        
        # Save figure
        with open(filepath, 'wb') as f:
            pickle.dump(clean_fig, f)
        
        print(f"Figure {{i+1}} saved as {{filename}}")
        
    except Exception as e:
        print(f"Error saving figure: {{e}}")
        continue
"""

@tool(parse_docstring=True)
def complete_python_task(
        graph_state: Annotated[dict, InjectedState], thought: str, python_code: str
) -> Tuple[str, dict]:
    """Completes a python task for data analysis and visualization.

    Args:
        graph_state: The current state of the graph containing input data and variables.
        thought: Internal thought about the next action to be taken, and the reasoning behind it.
        python_code: Python code to be executed to perform analyses, create a new dataset or create a visualization.

    Returns:
        A tuple containing the output from executing the Python code and updated state.
    """
    # Get session-specific persistent variables
    persistent_vars = get_persistent_vars()
    session_info = get_session_info()
    
    logger.info(f"Executing Python task for session {session_info['session_id']} with {len(python_code)} characters")
    
    # Use the original code without preprocessing
    processed_code = python_code
    
    # Create safe execution environment
    exec_globals = create_safe_execution_environment()
    
    current_variables = graph_state["current_variables"] if "current_variables" in graph_state else {}
    for input_dataset in graph_state["input_data"]:
        if input_dataset.variable_name not in current_variables:
            try:
                if input_dataset.data_path.endswith('.csv'):
                    current_variables[input_dataset.variable_name] = pd.read_csv(input_dataset.data_path)
                    logger.info(f"Loaded dataset {input_dataset.variable_name} with {len(current_variables[input_dataset.variable_name])} rows")
                elif input_dataset.data_path.endswith('.json'):
                    current_variables[input_dataset.variable_name] = pd.read_json(input_dataset.data_path)
                    logger.info(f"Loaded dataset {input_dataset.variable_name} with {len(current_variables[input_dataset.variable_name])} rows")
                else:
                    raise ValueError(f"Unsupported file type: {input_dataset.data_path}")
            except Exception as e:
                logger.error(f"Error loading {input_dataset.data_path}: {str(e)}")
                raise ValueError(f"Error loading {input_dataset.data_path}: {str(e)}")
    
    if not os.path.exists(config.IMAGES_DIR):
        os.makedirs(config.IMAGES_DIR)

    try:
        current_image_pickle_files = os.listdir(config.IMAGES_DIR)
    except FileNotFoundError:
        current_image_pickle_files = []
    
    try:
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Update execution environment with session variables and data
        exec_globals.update(persistent_vars)  # Session-specific variables
        exec_globals.update(current_variables)
        exec_globals.update({"plotly_figures": []})

        # Execute the processed code
        exec(processed_code, exec_globals)
        
        # Update session-specific persistent variables
        new_vars = {k: v for k, v in exec_globals.items() 
                   if k not in globals() and not k.startswith('_')}
        persistent_vars.update(new_vars)
        
        # Log variable count for monitoring
        if new_vars:
            logger.info(f"Session {session_info['session_id']}: Added {len(new_vars)} new variables. Total: {len(persistent_vars)}")

        # Get the captured stdout
        output = sys.stdout.getvalue()

        # Restore stdout
        sys.stdout = old_stdout

        updated_state = {
            "intermediate_outputs": [{"thought": thought, "code": processed_code, "output": output}],
            "current_variables": persistent_vars  # Session-specific variables
        }

        if 'plotly_figures' in exec_globals:
            exec(plotly_saving_code, exec_globals)
            # Check if any images were created
            try:
                new_image_folder_contents = os.listdir(config.IMAGES_DIR)
            except FileNotFoundError:
                new_image_folder_contents = []
            new_image_files = [file for file in new_image_folder_contents if file not in current_image_pickle_files]
            if new_image_files:
                updated_state["output_image_paths"] = new_image_files
                logger.info(f"Session {session_info['session_id']}: Created {len(new_image_files)} new plotly figures")
            
            persistent_vars["plotly_figures"] = []

        logger.info(f"Python task completed successfully for session {session_info['session_id']}")
        return output, updated_state
        
    except Exception as e:
        # Simple error handling
        user_friendly_error = f"Error de ejecución: {str(e)}"
        
        logger.error(f"Code execution error for session {session_info['session_id']}: {str(e)}")
        return user_friendly_error, {"intermediate_outputs": [{"thought": thought, "code": processed_code, "output": user_friendly_error}]}