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
import pickle
import gc
import tempfile
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


# Configuración del gestor de sesiones (centralizada en config.py)
SESSION_TTL_HOURS = config.SESSION_TTL_HOURS
MAX_MEMORY_PER_SESSION_MB = config.MAX_MEMORY_PER_SESSION_MB
MAX_VARIABLES_PER_SESSION = config.MAX_VARIABLES_PER_SESSION
MAX_IMAGES_PER_SESSION = config.MAX_IMAGES_PER_SESSION
CLEANUP_INTERVAL_SECONDS = config.CLEANUP_INTERVAL_SECONDS

# Gestor de sesiones global
class SessionManager:
    """Gestor robusto de sesiones con TTL y límites de memoria."""
    
    def __init__(self):
        self.sessions = {}  # {session_id: SessionData}
        self.lock = threading.Lock()
        self.cleanup_timer = None
        self.start_cleanup_scheduler()
    
    def start_cleanup_scheduler(self):
        """Inicia el planificador de limpieza periódica."""
        def schedule_cleanup():
            self.cleanup_old_sessions()
            # Programar siguiente limpieza
            self.cleanup_timer = threading.Timer(CLEANUP_INTERVAL_SECONDS, schedule_cleanup)
            self.cleanup_timer.daemon = True
            self.cleanup_timer.start()
        
        self.cleanup_timer = threading.Timer(CLEANUP_INTERVAL_SECONDS, schedule_cleanup)
        self.cleanup_timer.daemon = True
        self.cleanup_timer.start()
        logger.info("Session cleanup scheduler started")
    
    def create_session(self, session_id: str) -> dict:
        """Crea una nueva sesión con metadatos."""
        with self.lock:
            session_data = {
                'session_id': session_id,
                'start_time': time.time(),
                'last_activity': time.time(),
                'variables': {},
                'variable_count': 0,
                'memory_usage_mb': 0,
                'image_files': [],
                'image_count': 0,
                'temp_dir': None
            }
            self.sessions[session_id] = session_data
            logger.info(f"Created session: {session_id}")
            return session_data
    
    def get_session(self, session_id: str) -> dict:
        """Obtiene una sesión existente o crea una nueva."""
        with self.lock:
            if session_id not in self.sessions:
                return self.create_session(session_id)
            
            # Actualizar última actividad
            self.sessions[session_id]['last_activity'] = time.time()
            return self.sessions[session_id]
    
    def update_session_memory(self, session_id: str, variables: dict):
        """Actualiza el uso de memoria de una sesión."""
        if session_id not in self.sessions:
            return
        
        total_memory = 0
        for var_name, var_value in variables.items():
            try:
                if isinstance(var_value, pd.DataFrame):
                    memory_usage = var_value.memory_usage(deep=True).sum()
                elif isinstance(var_value, pd.Series):
                    memory_usage = var_value.memory_usage(deep=True)
                else:
                    memory_usage = sys.getsizeof(var_value)
                total_memory += memory_usage
            except:
                total_memory += 1024  # Estimación por defecto
        
        with self.lock:
            self.sessions[session_id]['memory_usage_mb'] = total_memory / (1024 * 1024)
            self.sessions[session_id]['variable_count'] = len(variables)
    
    def add_image_file(self, session_id: str, image_filename: str):
        """Registra un archivo de imagen para una sesión."""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['image_files'].append(image_filename)
                self.sessions[session_id]['image_count'] = len(self.sessions[session_id]['image_files'])
    
    def cleanup_session(self, session_id: str):
        """Limpia completamente una sesión."""
        with self.lock:
            if session_id not in self.sessions:
                return
            
            session_data = self.sessions[session_id]
            
            # Limpiar variables
            session_data['variables'].clear()
            session_data['variable_count'] = 0
            session_data['memory_usage_mb'] = 0
            
            # Eliminar archivos de imagen
            for image_file in session_data['image_files']:
                try:
                    filepath = os.path.join(config.IMAGES_DIR, image_file)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"Removed image file: {image_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove image file {image_file}: {e}")
            
            session_data['image_files'].clear()
            session_data['image_count'] = 0
            
            # Limpiar directorio temporal
            if session_data['temp_dir'] and os.path.exists(session_data['temp_dir']):
                try:
                    import shutil
                    shutil.rmtree(session_data['temp_dir'])
                    logger.info(f"Removed temp directory for session: {session_id}")
                except Exception as e:
                    logger.warning(f"Failed to remove temp directory for session {session_id}: {e}")
            
            # Eliminar de la lista de sesiones
            del self.sessions[session_id]
            logger.info(f"Session cleanup completed: {session_id}")
    
    def cleanup_old_sessions(self):
        """Limpia sesiones que han expirado."""
        current_time = time.time()
        max_age_seconds = SESSION_TTL_HOURS * 3600
        
        sessions_to_cleanup = []
        
        with self.lock:
            for session_id, session_data in self.sessions.items():
                session_age = current_time - session_data['start_time']
                last_activity_age = current_time - session_data['last_activity']
                
                # Limpiar si la sesión es muy antigua o inactiva
                if session_age > max_age_seconds or last_activity_age > max_age_seconds:
                    sessions_to_cleanup.append(session_id)
                    logger.info(f"Marking session for cleanup: {session_id} (age: {session_age/3600:.1f}h)")
        
        # Limpiar sesiones marcadas
        for session_id in sessions_to_cleanup:
            self.cleanup_session(session_id)
        
        # Forzar garbage collection
        gc.collect()
        
        # Log del estado del sistema
        total_sessions = len(self.sessions)
        total_memory = sum(s['memory_usage_mb'] for s in self.sessions.values())
        logger.info(f"Session cleanup completed. Active sessions: {total_sessions}, Total memory: {total_memory:.2f}MB")
    
    def check_memory_limits(self, session_id: str, new_variables: dict) -> bool:
        """Verifica si agregar nuevas variables excedería los límites de memoria."""
        if session_id not in self.sessions:
            return True
        
        current_memory = self.sessions[session_id]['memory_usage_mb']
        
        # Estimar memoria de nuevas variables
        new_memory = 0
        for var_value in new_variables.values():
            try:
                if isinstance(var_value, pd.DataFrame):
                    memory_usage = var_value.memory_usage(deep=True).sum()
                elif isinstance(var_value, pd.Series):
                    memory_usage = var_value.memory_usage(deep=True)
                else:
                    memory_usage = sys.getsizeof(var_value)
                new_memory += memory_usage
            except:
                new_memory += 1024
        
        new_memory_mb = new_memory / (1024 * 1024)
        total_memory = current_memory + new_memory_mb
        
        if total_memory > MAX_MEMORY_PER_SESSION_MB:
            logger.warning(f"Session {session_id}: Memory limit exceeded ({total_memory:.2f}MB > {MAX_MEMORY_PER_SESSION_MB}MB)")
            return False
        
        return True
    
    def enforce_memory_limits(self, session_id: str):
        """Fuerza el cumplimiento de límites de memoria eliminando variables antiguas."""
        if session_id not in self.sessions:
            return
        
        session_data = self.sessions[session_id]
        
        if session_data['memory_usage_mb'] > MAX_MEMORY_PER_SESSION_MB:
            logger.warning(f"Session {session_id}: Enforcing memory limits")
            
            # Eliminar la mitad de las variables más antiguas
            variables = list(session_data['variables'].items())
            if len(variables) > 1:
                variables_to_remove = variables[:len(variables)//2]
                for var_name, _ in variables_to_remove:
                    if var_name in session_data['variables']:
                        del session_data['variables'][var_name]
                
                # Actualizar métricas
                self.update_session_memory(session_id, session_data['variables'])
                gc.collect()
    
    def get_session_info(self, session_id: str) -> dict:
        """Obtiene información detallada de una sesión."""
        if session_id not in self.sessions:
            return {'session_id': session_id, 'exists': False}
        
        session_data = self.sessions[session_id]
        current_time = time.time()
        
        return {
            'session_id': session_id,
            'exists': True,
            'start_time': session_data['start_time'],
            'last_activity': session_data['last_activity'],
            'age_hours': (current_time - session_data['start_time']) / 3600,
            'inactive_hours': (current_time - session_data['last_activity']) / 3600,
            'variable_count': session_data['variable_count'],
            'memory_usage_mb': session_data['memory_usage_mb'],
            'image_count': session_data['image_count']
        }
    
    def get_all_sessions_info(self) -> list:
        """Obtiene información de todas las sesiones activas."""
        with self.lock:
            return [self.get_session_info(session_id) for session_id in self.sessions.keys()]


# Instancia global del gestor de sesiones
session_manager = SessionManager()

# Thread-local storage para compatibilidad
_thread_local = threading.local()

def get_session_id() -> str:
    """Obtiene o crea un ID de sesión único para el hilo actual."""
    if not hasattr(_thread_local, 'session_id'):
        _thread_local.session_id = str(uuid.uuid4())
        session_manager.create_session(_thread_local.session_id)
        logger.info(f"Created new session: {_thread_local.session_id}")
    else:
        # Actualizar actividad
        session_manager.get_session(_thread_local.session_id)
    
    return _thread_local.session_id

def get_persistent_vars() -> dict:
    """Obtiene las variables persistentes de la sesión actual."""
    session_id = get_session_id()
    session_data = session_manager.get_session(session_id)
    return session_data['variables']

def get_session_info() -> dict:
    """Obtiene información de la sesión actual."""
    session_id = get_session_id()
    return session_manager.get_session_info(session_id)

def create_safe_execution_environment() -> dict:
    """Crea un entorno de ejecución seguro con todas las importaciones y utilidades necesarias."""
    # Configure Plotly to not open new tabs
    import plotly.io as pio
    pio.renderers.default = "notebook"  # This prevents opening new tabs
    
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
        'time': __import__('time'),
        
        # Funciones de utilidad para fechas
        'pd_to_datetime': pd.to_datetime,
        'pd_date_range': pd.date_range,
    }
    
    # Agregar métricas de producción si están disponibles
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
    
    # Agregar función de conversión de fechas segura
    def safe_date_conversion(series, **kwargs):
        """Convierte de forma segura una serie a datetime con manejo de errores."""
        try:
            return pd.to_datetime(series, **kwargs)
        except Exception as e:
            logger.warning(f"Date conversion error: {e}")
            return series
    
    def safe_date_filter(df, date_column, start_date=None, end_date=None):
        """Filtra de forma segura un dataframe por rango de fechas."""
        try:
            if date_column not in df.columns:
                return df
            
            # Asegurar que la columna de fecha sea datetime
            df[date_column] = pd.to_datetime(df[date_column])
            
            if start_date:
                df = df[df[date_column] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df[date_column] <= pd.to_datetime(end_date)]
            
            return df
        except Exception as e:
            logger.warning(f"Date filtering error: {e}")
            return df
    
    env.update({
        'safe_date_conversion': safe_date_conversion,
        'safe_date_filter': safe_date_filter,
    })
    
    return env

plotly_saving_code = f"""import pickle
import uuid
import plotly
import plotly.io as pio
import pandas as pd
import numpy as np

# Configure Plotly to not open new tabs
pio.renderers.default = "notebook"

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
        
        # Generate unique filename with timestamp
        timestamp = int(time.time())
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
    session_id = get_session_id()
    persistent_vars = get_persistent_vars()
    session_info = get_session_info()
    
    logger.info(f"Executing Python task for session {session_id} with {len(python_code)} characters")
    
    # Use the original code without preprocessing
    processed_code = python_code
    
    # Create safe execution environment
    exec_globals = create_safe_execution_environment()
    
    current_variables = graph_state["current_variables"] if "current_variables" in graph_state else {}
    # Load DataFrames directly from the state
    for table_name, df in graph_state["dataframes"].items():
        if table_name not in current_variables:
            current_variables[table_name] = df
            logger.info(f"Loaded dataset {table_name} with {len(df)} rows")
    
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
        
        # Update session-specific persistent variables with memory management
        new_vars = {k: v for k, v in exec_globals.items() 
                   if k not in globals() and not k.startswith('_')}
        
        # Check memory limits before adding new variables
        if not session_manager.check_memory_limits(session_id, new_vars):
            # If memory limit exceeded, enforce limits
            session_manager.enforce_memory_limits(session_id)
        
        # Add new variables
        persistent_vars.update(new_vars)
        
        # Update session memory usage
        session_manager.update_session_memory(session_id, persistent_vars)
        
        # Log variable count for monitoring
        if new_vars:
            session_data = session_manager.get_session(session_id)
            logger.info(f"Session {session_id}: Added {len(new_vars)} new variables. "
                       f"Total: {session_data['variable_count']}. "
                       f"Memory: {session_data['memory_usage_mb']:.2f}MB")

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
                logger.info(f"Session {session_id}: Created {len(new_image_files)} new plotly figures")
                
                # Register image files with session manager
                for image_file in new_image_files:
                    session_manager.add_image_file(session_id, image_file)
            
            persistent_vars["plotly_figures"] = []

        logger.info(f"Python task completed successfully for session {session_id}")
        return output, updated_state
        
    except Exception as e:
        # Simple error handling
        user_friendly_error = f"Error de ejecución: {str(e)}"
        
        logger.error(f"Code execution error for session {session_id}: {str(e)}")
        return user_friendly_error, {"intermediate_outputs": [{"thought": thought, "code": processed_code, "output": user_friendly_error}]}