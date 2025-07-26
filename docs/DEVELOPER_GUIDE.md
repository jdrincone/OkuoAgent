# 🛠️ Guía del Desarrollador - OkuoAgent

## 📋 Índice

1. [Arquitectura Técnica](#arquitectura-técnica)
2. [Flujo de Datos](#flujo-de-datos)
3. [Componentes Principales](#componentes-principales)
4. [Configuración de Desarrollo](#configuración-de-desarrollo)
5. [Patrones de Diseño](#patrones-de-diseño)
6. [Extensibilidad](#extensibilidad)
7. [Testing](#testing)
8. [Debugging](#debugging)
9. [Deployment](#deployment)

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

```
Frontend (Streamlit)
├── streamlit_apps/
│   ├── components/          # Componentes modulares
│   ├── pages/              # Páginas de la aplicación
│   └── data_analysis_streamlit_app.py
│
Backend (LangGraph + OpenAI)
├── core/
│   ├── backend.py          # Orquestador principal
│   ├── graph/              # Sistema de grafo
│   └── prompts/            # Prompts del agente
│
Data Layer
├── services/               # Servicios de datos
├── utils/                  # Utilidades
└── data/                   # Metadata y configuración
```

### Principios de Diseño

1. **Separación de Responsabilidades**: Cada componente tiene una responsabilidad específica
2. **Modularidad**: Componentes reutilizables y desacoplados
3. **Configuración Centralizada**: Todas las configuraciones en `config.py`
4. **Logging Estratégico**: Logging detallado para debugging
5. **Manejo de Errores**: Fallbacks y recuperación automática

## 🔄 Flujo de Datos

### 1. Inicialización
```python
# 1. Carga de configuración
config = Config()

# 2. Inicialización de servicios
db_service = DatabaseService()
metadata_service = MetadataService()

# 3. Creación del agente
chatbot = PythonChatbot()
```

### 2. Procesamiento de Consulta
```python
# 1. Usuario envía consulta
user_query = "Muéstrame las tendencias de producción"

# 2. Carga de datos
dataframes = {"produccion_aliar": df}

# 3. Procesamiento con LangGraph
result = chatbot.user_sent_message(user_query, dataframes)

# 4. Ejecución de código Python
exec_result = complete_python_task(graph_state, thought, python_code)

# 5. Generación de visualizaciones
figures = exec_result["plotly_figures"]
```

### 3. Renderizado
```python
# 1. Carga de figuras desde pickle
figures = load_plotly_figures()

# 2. Renderizado en Streamlit
for fig in figures:
    st.plotly_chart(fig, use_container_width=True)
```

## 🔧 Componentes Principales

### Core Backend (`core/`)

#### `backend.py`
- **Responsabilidad**: Orquestación del flujo principal
- **Patrón**: Singleton para gestión de sesiones
- **Clave**: `PythonChatbot` - Clase principal del agente

```python
class PythonChatbot:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chat_history = []
        self.output_image_paths = {}
    
    def user_sent_message(self, user_query: str, dataframes: Dict[str, pd.DataFrame]):
        # Procesamiento principal
```

#### `graph/nodes.py`
- **Responsabilidad**: Nodos del grafo de LangGraph
- **Funciones clave**:
  - `call_model()`: Invocación del modelo LLM
  - `call_tools()`: Ejecución de herramientas
  - `route_to_tools()`: Enrutamiento inteligente

#### `graph/tools.py`
- **Responsabilidad**: Herramientas de ejecución
- **Función principal**: `complete_python_task()`
- **Características**:
  - Entorno de ejecución seguro
  - Gestión de memoria
  - Guardado de figuras

### Frontend (`streamlit_apps/`)

#### Componentes Modulares
```python
# styles.py - Tema y estilos
apply_corporate_theme()
load_corporate_styles()

# data_loader.py - Carga de datos
load_produccion_aliar_data()
has_data_for_analysis()

# chat.py - Interfaz de chat
render_chat_interface()
on_submit_user_query()

# kpi_view.py - Visualización de KPIs
render_kpis_section()

# debug_view.py - Panel de debugging
render_debug_panel()
```

### Servicios (`services/`)

#### `database_service.py`
```python
class DatabaseService:
    def get_produccion_aliar_data(self) -> pd.DataFrame:
        # Carga datos de PostgreSQL
    
    def get_tables(self) -> List[str]:
        # Lista tablas disponibles
```

#### `metadata_service.py`
```python
class MetadataService:
    def get_table_metadata(self, table_name: str) -> Dict:
        # Carga metadata desde YAML
    
    def get_column_info(self, table_name: str) -> Dict[str, str]:
        # Información de columnas
```

#### `kpi_service.py`
```python
class KPIService:
    def calculate_kpis(self, df: pd.DataFrame) -> Dict:
        # Calcula KPIs principales
    
    def get_sackoff_metrics(self, df: pd.DataFrame) -> Dict:
        # Métricas de sackoff
```

## ⚙️ Configuración de Desarrollo

### Entorno de Desarrollo

1. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

2. **Instalar dependencias de desarrollo**:
```bash
pip install -r requirements.txt
pip install pytest black flake8 mypy
```

3. **Configurar pre-commit hooks**:
```bash
pre-commit install
```

### Comandos de Desarrollo

```bash
# Formatear código
black core/ streamlit_apps/ services/ utils/

# Verificar estilo
flake8 core/ streamlit_apps/ services/ utils/

# Verificar tipos
mypy core/ streamlit_apps/ services/ utils/

# Ejecutar tests
pytest tests/

# Ejecutar aplicación en modo desarrollo
streamlit run run_app.py --server.port 8502 --server.address localhost
```

## 🎨 Patrones de Diseño

### 1. Singleton Pattern
```python
# config.py
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Factory Pattern
```python
# services/database_service.py
class DatabaseServiceFactory:
    @staticmethod
    def create_service(db_type: str) -> DatabaseService:
        if db_type == "postgresql":
            return PostgreSQLService()
        elif db_type == "sqlite":
            return SQLiteService()
```

### 3. Observer Pattern
```python
# utils/logger.py
class LogObserver:
    def update(self, message: str, level: str):
        # Notificar cambios de log
```

### 4. Strategy Pattern
```python
# core/graph/tools.py
class ExecutionStrategy:
    def execute(self, code: str, context: dict):
        pass

class SafeExecutionStrategy(ExecutionStrategy):
    def execute(self, code: str, context: dict):
        # Ejecución segura
```

## 🔌 Extensibilidad

### Agregar Nuevas Métricas

1. **Crear función en `utils/production_metrics.py`**:
```python
def compute_new_metric(df: pd.DataFrame) -> float:
    """Calcula nueva métrica de producción."""
    # Implementación
    return result
```

2. **Agregar al entorno de ejecución en `core/graph/tools.py`**:
```python
def create_safe_execution_environment() -> dict:
    env = {
        # ... otras funciones
        'compute_new_metric': compute_new_metric,
    }
    return env
```

3. **Documentar en metadata**:
```yaml
# data/metadata/produccion_aliar.yaml
calculated_metrics:
  - name: "nueva_metrica"
    formula: "compute_new_metric(produccion_aliar)"
    description: "Descripción de la nueva métrica"
```

4. **Integrar en el servicio de KPIs**:
```python
# services/kpi_service.py
def calculate_kpis(self, df: pd.DataFrame) -> Dict:
    return {
        # ... otros KPIs
        'nueva_metrica': compute_new_metric(df),
    }
```

### Agregar Nuevas Tablas

1. **Crear metadata YAML**:
```yaml
# data/metadata/nueva_tabla.yaml
description: "Descripción de la nueva tabla"
columns:
  - name: "columna1"
    description: "Descripción de columna1"
    type: "string"
```

2. **Actualizar servicio de base de datos**:
```python
# services/database_service.py
def get_nueva_tabla_data(self) -> pd.DataFrame:
    query = "SELECT * FROM nueva_tabla"
    return pd.read_sql(query, self.engine)
```

3. **Integrar en el flujo**:
```python
# streamlit_apps/components/data_loader.py
def load_all_data():
    return {
        "produccion_aliar": db_service.get_produccion_aliar_data(),
        "nueva_tabla": db_service.get_nueva_tabla_data(),
    }
```

### Agregar Nuevas Herramientas

1. **Crear herramienta en `core/graph/tools.py`**:
```python
@tool(parse_docstring=True)
def nueva_herramienta(param1: str, param2: int) -> str:
    """Descripción de la nueva herramienta.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
    
    Returns:
        Resultado de la herramienta
    """
    # Implementación
    return result
```

2. **Agregar al prompt**:
```markdown
# core/prompts/main_prompt.md
## 🛠️ Herramientas Disponibles

- `nueva_herramienta`: Descripción de cuándo usar esta herramienta
```

## 🧪 Testing

### Estructura de Tests

```
tests/                      # Tests del sistema
├── test_kpi_calculations.py # Tests de cálculos de KPIs
├── debug_database.py        # Scripts de debugging
└── fixtures/               # Datos de prueba (futuro)
```

### Ejemplos de Tests

#### Test Unitario
```python
# tests/unit/test_production_metrics.py
import pytest
from utils.production_metrics import compute_metric_sackoff

def test_compute_metric_sackoff():
    # Arrange
    df = create_test_dataframe()
    
    # Act
    result = compute_metric_sackoff(df)
    
    # Assert
    assert isinstance(result, float)
    assert result >= 0
```

#### Test de Integración
```python
# tests/integration/test_chatbot.py
def test_chatbot_workflow():
    # Arrange
    chatbot = PythonChatbot("test_session")
    query = "Calcula el sackoff promedio"
    data = {"produccion_aliar": test_df}
    
    # Act
    result = chatbot.user_sent_message(query, data)
    
    # Assert
    assert result is not None
    assert len(result.messages) > 0
```

### Comandos de Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con coverage
pytest --cov=core --cov=services --cov=utils

# Ejecutar tests específicos
pytest tests/unit/test_production_metrics.py

# Ejecutar tests en paralelo
pytest -n auto
```



### Debugging de Sesiones

```python
# Debug de variables de sesión
def debug_session(session_id: str):
    session_info = get_session_info(session_id)
    logger.info(f"Session {session_id}: {session_info}")
    
    # Ver variables
    variables = get_persistent_vars()
    logger.info(f"Variables: {list(variables.keys())}")
```

### Debugging de LangGraph

```python
# Habilitar debug de LangGraph
import os
os.environ["LANGGRAPH_TRACE"] = "true"

# Ver trazas en tiempo real
from langgraph.graph import StateGraph
graph = StateGraph(AgentState)
graph.set_debug(True)
```

### Herramientas de Debugging

1. **Streamlit Debug Mode**:
```bash
streamlit run run_app.py --logger.level debug
```

2. **Python Debugger**:
```python
import pdb; pdb.set_trace()
```

3. **Logs en Tiempo Real**:
```bash
tail -f logs/okuoagent.log | grep "ERROR\|WARNING"
```