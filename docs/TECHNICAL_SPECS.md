# 🔧 Especificaciones Técnicas - OkuoAgent

## 📋 Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [APIs y Endpoints](#apis-y-endpoints)
3. [Modelos de Datos](#modelos-de-datos)
4. [Configuración del Sistema](#configuración-del-sistema)
5. [Seguridad](#seguridad)
6. [Performance](#performance)
7. [Monitoreo](#monitoreo)
8. [Integración](#integración)

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit UI (Port 8502)                                       │
│  ├── Dashboard Component                                        │
│  ├── Chat Interface                                            │
│  ├── KPI Display                                               │
│  └── Debug Panel                                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  LangGraph Agent                                               │
│  ├── State Management                                          │
│  ├── Tool Execution                                            │
│  ├── Session Management                                        │
│  └── Error Handling                                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      External Services                          │
├─────────────────────────────────────────────────────────────────┤
│  OpenAI API │ PostgreSQL DB │ Metadata Service │ File System   │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. Frontend (Streamlit)
- **Framework**: Streamlit 1.28+
- **Puerto**: 8502
- **Arquitectura**: Component-based
- **Estado**: Session-based

#### 2. Backend (LangGraph)
- **Framework**: LangGraph 0.2+
- **Patrón**: State Machine
- **Herramientas**: Python REPL
- **Memoria**: Thread-local storage

#### 3. Base de Datos
- **Sistema**: PostgreSQL 13+
- **Conexión**: SQLAlchemy
- **Pool**: Connection pooling
- **Backup**: Automático diario

#### 4. Servicios Externos
- **OpenAI**: GPT-4o-mini
- **Metadata**: YAML files (`data/metadata/`)
- **Storage**: Local file system (`images/`, `uploads/`, `logs/`)

## 🔌 APIs y Endpoints

### LangGraph State API

#### AgentState
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    dataframes: Dict[str, pd.DataFrame]
    intermediate_outputs: Annotated[List[dict], operator.add]
    current_variables: dict
    output_image_paths: Annotated[List[str], operator.add]
```

#### Endpoints Internos

##### 1. Model Invocation
```python
def call_model(state: AgentState) -> Dict:
    """
    Invoca el modelo LLM con el estado actual.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Dict con mensajes y outputs intermedios
    """
```

##### 2. Tool Execution
```python
def call_tools(state: AgentState) -> Dict:
    """
    Ejecuta herramientas basadas en el estado.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Dict con resultados de herramientas
    """
```

##### 3. Routing Logic
```python
def route_to_tools(state: AgentState) -> Literal["tools", "__end__"]:
    """
    Determina si continuar a herramientas o terminar.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        "tools" para continuar, "__end__" para terminar
    """
```

### Database Service API

#### DatabaseService
```python
class DatabaseService:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
    
    def get_produccion_aliar_data(self) -> pd.DataFrame:
        """Obtiene datos de la tabla produccion_aliar."""
        
    def get_tables(self) -> List[str]:
        """Obtiene lista de tablas disponibles."""
        
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos."""
```

### Metadata Service API

#### MetadataService
```python
class MetadataService:
    def __init__(self):
        self.metadata_dir = "data/metadata/"
        self._metadata_cache = {}
    
    def get_table_metadata(self, table_name: str) -> Optional[Dict]:
        """Obtiene metadata completa de una tabla."""
        
    def get_column_info(self, table_name: str) -> Dict[str, str]:
        """Obtiene información de columnas."""
        
    def get_business_context(self, table_name: str) -> str:
        """Obtiene contexto de negocio."""
```

### KPI Service API

#### KPIService
```python
class KPIService:
    def __init__(self):
        self.metrics = {}
    
    def calculate_kpis(self, df: pd.DataFrame) -> Dict:
        """Calcula KPIs principales."""
        
    def get_sackoff_metrics(self, df: pd.DataFrame) -> Dict:
        """Obtiene métricas de sackoff."""
        
    def get_efficiency_metrics(self, df: pd.DataFrame) -> Dict:
        """Obtiene métricas de eficiencia."""
```

## 📊 Modelos de Datos

### Tabla Principal: produccion_aliar

#### Esquema de Base de Datos
```sql
CREATE TABLE produccion_aliar (
    id_registro SERIAL PRIMARY KEY,
    orden_produccion VARCHAR(50) NOT NULL,
    fecha_produccion TIMESTAMP NOT NULL,
    mes_produccion VARCHAR(20),
    planta VARCHAR(50),
    referencia_producto VARCHAR(50),
    nombre_producto VARCHAR(100),
    toneladas_a_producir DECIMAL(10,2),
    toneladas_materia_prima_consumida DECIMAL(10,2),
    toneladas_anuladas DECIMAL(10,2),
    toneladas_producidas DECIMAL(10,2),
    tiene_adiflow BOOLEAN,
    peso_agua_kg DECIMAL(10,2),
    order_produccion_despachada BOOLEAN,
    control_aceite_postengrase_pct DECIMAL(5,2),
    control_presion_distribuidor_psi DECIMAL(8,2),
    control_carga_alimentador_pct DECIMAL(5,2),
    control_presion_acondicionador_psi DECIMAL(8,2),
    durabilidad_pct_qa_agroindustrial DECIMAL(5,2),
    dureza_qa_agroindustrial DECIMAL(6,2),
    finos_pct_qa_agroindustrial DECIMAL(5,2),
    durabilidad_pct_produccion DECIMAL(5,2),
    dureza_produccion DECIMAL(6,2),
    finos_pct_produccion DECIMAL(5,2),
    diferencia_toneladas_por_orden_produccion DECIMAL(10,2),
    sackoff_por_orden_produccion DECIMAL(10,2)
);
```

#### Índices Recomendados
```sql
-- Índices para optimización
CREATE INDEX idx_fecha_produccion ON produccion_aliar(fecha_produccion);
CREATE INDEX idx_planta ON produccion_aliar(planta);
CREATE INDEX idx_tiene_adiflow ON produccion_aliar(tiene_adiflow);
CREATE INDEX idx_orden_produccion ON produccion_aliar(orden_produccion);
```

### Metadata YAML Structure

#### produccion_aliar.yaml
```yaml
description: "Tabla que contiene registros de órdenes de producción..."
columns:
  - name: "id_registro"
    description: "Identificador único del registro"
    type: "integer"
    business_meaning: "Clave primaria de la tabla"
  
  - name: "fecha_produccion"
    description: "Fecha exacta de producción"
    type: "datetime"
    business_meaning: "Cuándo se realizó la producción"

calculated_metrics:
  - name: "eficiencia_produccion"
    formula: "(toneladas_producidas / toneladas_a_producir) * 100"
    description: "Porcentaje de eficiencia de producción"

business_rules:
  - "Las métricas de QA agroindustrial son las medidas oficiales"
  - "El aditivo Adiflow puede afectar significativamente la calidad"

key_metrics:
  - "Eficiencia de producción (meta: >90%)"
  - "Calidad QA (durabilidad >90%, dureza 8-12 kg/cm²)"

relationships:
  - "Adiflow → Mejora calidad → Menor sackoff"
  - "Presión acondicionador → Calidad del pellet"
```

## ⚙️ Configuración del Sistema

### Variables de Entorno

#### Configuración de OpenAI
```env
OPENAI_API_KEY=sk-...                    # API Key de OpenAI
OPENAI_MODEL=gpt-4o-mini                 # Modelo a usar
OPENAI_TEMPERATURE=0.1                   # Temperatura (0.0-1.0)
OPENAI_MAX_TOKENS=4000                   # Máximo de tokens
```

#### Configuración de Base de Datos
```env
DATABASE_HOST=localhost                   # Host de la BD
DATABASE_PORT=5432                        # Puerto de la BD
DATABASE_NAME=aliar_production            # Nombre de la BD
DATABASE_USER=okuoagent_user              # Usuario de la BD
DATABASE_PASSWORD=secure_password         # Contraseña de la BD
DATABASE_URL=postgresql://user:pass@host:port/db
```

#### Configuración de la Aplicación
```env
STREAMLIT_PAGE_TITLE=OkuoAgent - Análisis Inteligente
STREAMLIT_PAGE_ICON=🤖
IMAGES_DIR=images/plotly_figures/pickle
UPLOADS_DIR=uploads
LOG_LEVEL=INFO
ENVIRONMENT=production
```

#### Configuración de Sesiones
```env
SESSION_TTL_HOURS=24                      # TTL de sesiones
MAX_MEMORY_PER_SESSION_MB=100             # Memoria por sesión
MAX_VARIABLES_PER_SESSION=50              # Variables por sesión
MAX_IMAGES_PER_SESSION=20                 # Imágenes por sesión
CLEANUP_INTERVAL_SECONDS=691200           # Limpieza cada 8 días
```

### Configuración de Streamlit

#### .streamlit/config.toml
```toml
[server]
port = 8502
address = "localhost"
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1C8074"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 🔒 Seguridad

### Medidas de Seguridad Implementadas

#### 1. Validación de Entrada
```python
def validate_user_input(user_query: str) -> bool:
    """Valida la entrada del usuario."""
    # Sanitización básica
    if len(user_query) > 1000:
        return False
    
    # Verificar caracteres peligrosos
    dangerous_chars = ['<script>', 'javascript:', 'eval(']
    for char in dangerous_chars:
        if char in user_query.lower():
            return False
    
    return True
```

#### 2. Entorno de Ejecución Seguro
```python
def create_safe_execution_environment() -> dict:
    """Crea un entorno de ejecución seguro."""
    safe_globals = {
        'pd': pandas,
        'np': numpy,
        'plt': matplotlib.pyplot,
        # Solo librerías seguras
    }
    
    # Excluir funciones peligrosas
    forbidden = ['os.system', 'subprocess', 'eval', 'exec']
    
    return safe_globals
```

#### 3. Límites de Recursos
```python
# Límites por sesión
MAX_MEMORY_PER_SESSION_MB = 100
MAX_VARIABLES_PER_SESSION = 50
MAX_IMAGES_PER_SESSION = 20
SESSION_TTL_HOURS = 24
```

#### 4. Logging Seguro
```python
def sanitize_log_message(message: str) -> str:
    """Sanitiza mensajes de log para evitar información sensible."""
    # Remover API keys
    message = re.sub(r'sk-[a-zA-Z0-9]{48}', '[API_KEY]', message)
    
    # Remover contraseñas
    message = re.sub(r'password=[^&\s]+', 'password=[HIDDEN]', message)
    
    return message
```

### Autenticación y Autorización

#### Niveles de Acceso
1. **Usuario Básico**: Solo lectura de datos
2. **Analista**: Análisis y consultas
3. **Administrador**: Configuración del sistema

#### Control de Acceso
```python
def check_user_permissions(user_id: str, action: str) -> bool:
    """Verifica permisos del usuario."""
    permissions = get_user_permissions(user_id)
    
    if action == "read_data":
        return True  # Todos pueden leer
    elif action == "modify_config":
        return "admin" in permissions
    elif action == "delete_data":
        return "admin" in permissions
    
    return False
```

## ⚡ Performance

### Métricas de Rendimiento

#### Objetivos de Performance
- **Tiempo de Respuesta**: < 5 segundos promedio
- **Throughput**: 100+ consultas por minuto
- **Memoria**: < 100MB por sesión
- **Disponibilidad**: 99.9% uptime

#### Optimizaciones Implementadas

##### 1. Caché de Metadata
```python
class MetadataService:
    def __init__(self):
        self._metadata_cache = {}  # Cache en memoria
    
    def get_table_metadata(self, table_name: str) -> Optional[Dict]:
        if table_name in self._metadata_cache:
            return self._metadata_cache[table_name]  # Cache hit
        
        # Cache miss - cargar desde archivo
        metadata = self._load_from_file(table_name)
        self._metadata_cache[table_name] = metadata
        return metadata
```

##### 2. Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

##### 3. Lazy Loading
```python
def load_data_on_demand(table_name: str) -> pd.DataFrame:
    """Carga datos solo cuando se necesitan."""
    if table_name not in _data_cache:
        _data_cache[table_name] = db_service.get_table_data(table_name)
    return _data_cache[table_name]
```

##### 4. Compresión de Figuras
```python
def compress_plotly_figure(fig) -> bytes:
    """Comprime figuras para reducir uso de memoria."""
    return pickle.dumps(fig, protocol=4, compression='gzip')
```

### Monitoreo de Performance

#### Métricas Clave
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'error_rates': [],
            'throughput': []
        }
    
    def record_response_time(self, duration: float):
        self.metrics['response_times'].append(duration)
    
    def get_average_response_time(self) -> float:
        return sum(self.metrics['response_times']) / len(self.metrics['response_times'])
```

## 📊 Monitoreo

### Health Checks

#### Endpoint de Health Check
```python
def health_check() -> Dict[str, Any]:
    """Verifica el estado del sistema."""
    checks = {
        'database': check_database_connection(),
        'openai': check_openai_connection(),
        'memory': check_memory_usage(),
        'disk': check_disk_space(),
        'sessions': check_active_sessions()
    }
    
    overall_status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return {
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'checks': checks
    }
```

#### Métricas del Sistema
```python
def get_system_metrics() -> Dict[str, Any]:
    """Obtiene métricas del sistema."""
    return {
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'active_sessions': len(get_active_sessions()),
        'total_requests': get_total_requests(),
        'error_rate': get_error_rate()
    }
```

### Alertas

#### Configuración de Alertas
```python
ALERT_THRESHOLDS = {
    'cpu_usage': 80,      # % CPU
    'memory_usage': 85,   # % Memoria
    'disk_usage': 90,     # % Disco
    'error_rate': 5,      # % Errores
    'response_time': 10   # segundos
}

def check_alerts():
    """Verifica si se deben enviar alertas."""
    metrics = get_system_metrics()
    
    for metric, threshold in ALERT_THRESHOLDS.items():
        if metrics[metric] > threshold:
            send_alert(f"High {metric}: {metrics[metric]}%")
```

## 🔗 Integración

### APIs de Integración

#### REST API Endpoints
```python
# GET /api/health
def health_endpoint():
    return health_check()

# GET /api/metrics
def metrics_endpoint():
    return get_system_metrics()

# POST /api/query
def query_endpoint(request):
    user_query = request.json['query']
    return process_user_query(user_query)

# GET /api/data/{table_name}
def data_endpoint(table_name):
    return get_table_data(table_name)
```

#### Webhook Integration
```python
def webhook_handler(event_type: str, data: Dict):
    """Maneja webhooks de sistemas externos."""
    if event_type == "data_update":
        refresh_data_cache()
    elif event_type == "config_change":
        reload_configuration()
    elif event_type == "alert":
        process_alert(data)
```

### Integración con Sistemas Externos

#### PostgreSQL Triggers
```sql
-- Trigger para notificar cambios en datos
CREATE OR REPLACE FUNCTION notify_data_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('data_change', json_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'timestamp', NOW()
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER data_change_trigger
    AFTER INSERT OR UPDATE OR DELETE ON produccion_aliar
    FOR EACH ROW EXECUTE FUNCTION notify_data_change();
```

#### Exportación de Datos
```python
def export_data(format: str, filters: Dict) -> bytes:
    """Exporta datos en diferentes formatos."""
    data = get_filtered_data(filters)
    
    if format == 'csv':
        return data.to_csv(index=False).encode('utf-8')
    elif format == 'excel':
        return data.to_excel(index=False)
    elif format == 'json':
        return data.to_json(orient='records').encode('utf-8')
```

### Configuración de Integración

#### Configuración de Webhooks
```env
WEBHOOK_URL=https://api.external-system.com/webhook
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_EVENTS=data_update,config_change,alert
```

#### Configuración de Exportación
```env
EXPORT_ENABLED=true
EXPORT_FORMATS=csv,excel,json
EXPORT_MAX_ROWS=10000
EXPORT_RETENTION_DAYS=30
```

---

**Documentación Técnica Completa** - Para más detalles, consulta la documentación de la API o contacta al equipo de desarrollo. 