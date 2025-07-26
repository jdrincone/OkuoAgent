# 🤖 OkuoAgent - Agente Inteligente de Análisis de Datos en plantas de producción de alimentos concentrados para animales

## 📋 Descripción General

**OkuoAgent** es un agente de inteligencia artificial especializado en análisis de datos industriales, diseñado específicamente para la empresa Aliar. Combina tecnologías avanzadas de IA (LangGraph, OpenAI) con capacidades de análisis de datos en tiempo real para proporcionar insights accionables sobre producción y calidad.

### 🎯 Propósito Principal

- **Análisis Inteligente**: Conversación natural con datos de producción
- **Visualización Automática**: Gráficos interactivos generados automáticamente
- **KPIs en Tiempo Real**: Métricas clave de producción actualizadas
- **Detección de Tendencias**: Identificación automática de patrones y anomalías

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   LangGraph     │    │   Base de Datos │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   OpenAI API    │◄─────────────┘
                        └─────────────────┘
```

### Flujo de Datos

1. **Usuario** → Interactúa con la interfaz Streamlit
2. **Streamlit** → Envía consulta al agente LangGraph
3. **LangGraph** → Procesa con OpenAI y ejecuta código Python
4. **Base de Datos** → Proporciona datos de producción en tiempo real
5. **Resultados** → Gráficos y análisis se muestran en la UI

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.12+
- PostgreSQL
- Cuenta de OpenAI API

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/OkuoAgent.git
cd OkuoAgent
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp env.example .env
```

Editar `.env` con tus credenciales:

```env
# OpenAI Configuration
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=aliar_production
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_password
DATABASE_URL=postgresql://usuario:password@localhost:5432/aliar_production

# Application Configuration
STREAMLIT_PAGE_TITLE=OkuoAgent - Análisis Inteligente
STREAMLIT_PAGE_ICON=🤖
IMAGES_DIR=images/plotly_figures/pickle
UPLOADS_DIR=uploads

# Session Management
SESSION_TTL_HOURS=24
MAX_MEMORY_PER_SESSION_MB=100
MAX_VARIABLES_PER_SESSION=50
MAX_IMAGES_PER_SESSION=20
CLEANUP_INTERVAL_SECONDS=691200
```

### 4. Configurar Base de Datos

Asegúrate de que PostgreSQL esté corriendo y que la tabla `produccion_aliar` exista con la estructura correcta.

### 5. Ejecutar la Aplicación

```bash
streamlit run run_app.py
```

La aplicación estará disponible en: `http://localhost:8502`

## 💬 Cómo Usar OkuoAgent

### 1. Acceso a la Interfaz

1. Abre tu navegador y ve a `http://localhost:8502`
2. Verás la interfaz principal con dos pestañas:
   - **💬 Dashboard Inteligente**: Chat con el agente
   - **🔧 Depuración**: Información técnica y debugging

### 2. Interacción con el Chat

#### Consultas Básicas
```
"Muéstrame las tendencias de producción del último mes"
"¿Cuál es el sackoff promedio por planta?"
"Compara la calidad con y sin Adiflow"
```

#### Análisis Específicos
```
"Genera un gráfico de eficiencia por producto"
"Analiza las anomalías en dureza"
"Calcula los KPIs principales"
```

#### Consultas Avanzadas
```
"Identifica correlaciones entre presión y calidad"
"Predice tendencias de producción para el próximo trimestre"
"Detecta patrones estacionales en los datos"
```

### 3. Interpretación de Resultados

#### Gráficos Interactivos
- **Zoom**: Haz clic y arrastra para hacer zoom
- **Hover**: Pasa el mouse para ver detalles
- **Pan**: Arrastra para mover la vista
- **Reset**: Doble clic para resetear la vista

#### KPIs en Tiempo Real
- **Sackoff**: Pérdida total por orden de producción
- **Eficiencia**: Porcentaje de producción vs. planificado
- **Calidad QA**: Métricas oficiales de calidad
- **Rendimiento**: Eficiencia en uso de materia prima

## 📊 Datos y Métricas Disponibles

### Tabla Principal: `produccion_aliar`

#### Columnas Clave
- **`fecha_produccion`**: Fecha exacta de producción
- **`planta`**: Ubicación de la producción
- **`nombre_producto`**: Producto fabricado
- **`toneladas_producidas`**: Producción real
- **`toneladas_a_producir`**: Producción planificada
- **`tiene_adiflow`**: Uso de aditivo (Si/No)
- **`durabilidad_pct_qa_agroindustrial`**: Calidad oficial
- **`dureza_qa_agroindustrial`**: Resistencia física
- **`finos_pct_qa_agroindustrial`**: Granulometría

#### Métricas Calculadas
- **Eficiencia de Producción**: `(toneladas_producidas / toneladas_a_producir) * 100`
- **Sackoff Total**: Pérdida total incluyendo anulaciones
- **Rendimiento de Materia Prima**: Eficiencia en uso de insumos

### Funciones Especializadas

#### Filtros por Adiflow
```python
# Datos con Adiflow
filter_con_adiflow(produccion_aliar)

# Datos sin Adiflow  
filter_sin_adiflow(produccion_aliar)
```

#### Cálculo de Métricas
```python
# Sackoff por orden
compute_metric_sackoff(produccion_aliar)

# KPIs principales
calculate_kpis(produccion_aliar)
```

## 🔧 Características Técnicas

### Gestión de Sesiones
- **TTL**: Sesiones expiran automáticamente (24h por defecto)
- **Memoria**: Límite de 100MB por sesión
- **Limpieza**: Limpieza automática cada 8 días
- **Variables**: Máximo 50 variables por sesión

### Manejo de Errores
- **Validación**: Verificación automática de datos
- **Fallbacks**: Respuestas de error útiles
- **Logging**: Registro detallado de operaciones
- **Recuperación**: Recuperación automática de errores

### Optimizaciones
- **Caché**: Metadata cacheada para mejor rendimiento
- **Lazy Loading**: Carga de datos bajo demanda
- **Memory Management**: Gestión automática de memoria
- **File Cleanup**: Limpieza automática de archivos temporales

## 📁 Estructura del Repositorio

```
OkuoAgent/
├── core/                          # Lógica principal del agente
│   ├── backend.py                 # Backend principal
│   ├── graph/                     # Componentes de LangGraph
│   │   ├── nodes.py              # Nodos del grafo
│   │   ├── state.py              # Estado del agente
│   │   └── tools.py              # Herramientas de ejecución
│   └── prompts/                   # Prompts del agente
│       └── main_prompt.md        # Prompt principal
├── streamlit_apps/                # Aplicación Streamlit
│   ├── components/               # Componentes modulares
│   │   ├── chat.py              # Interfaz de chat
│   │   ├── data_loader.py       # Cargador de datos
│   │   ├── kpi_view.py          # Vista de KPIs
│   │   ├── debug_view.py        # Vista de debugging
│   │   └── styles.py            # Estilos y tema
│   ├── pages/                    # Páginas de la aplicación
│   │   ├── login.py             # Sistema de autenticación
│   │   └── python_visualisation_agent.py
│   └── data_analysis_streamlit_app.py
├── services/                      # Servicios de datos
│   ├── database_service.py       # Conexión a BD
│   ├── metadata_service.py       # Gestión de metadata
│   └── kpi_service.py           # Servicio de KPIs
├── utils/                         # Utilidades
│   ├── logger.py                 # Sistema de logging
│   ├── config_validator.py       # Validación de configuración
│   ├── production_metrics.py     # Métricas de producción
│   ├── session_utils.py          # Gestión de sesiones
│   └── kpi_components.py         # Componentes de KPIs
├── data/                          # Datos y metadata
│   └── metadata/                 # Archivos YAML de metadata
│       └── produccion_aliar.yaml
├── docs/                          # Documentación
│   ├── DEVELOPER_GUIDE.md        # Guía para desarrolladores
│   ├── USER_GUIDE.md             # Guía para usuarios
│   └── TECHNICAL_SPECS.md        # Especificaciones técnicas
├── images/                        # Imágenes generadas
├── logs/                          # Archivos de log
├── uploads/                       # Archivos temporales
├── tests/                         # Tests del sistema
├── config.py                      # Configuración centralizada
├── requirements.txt               # Dependencias
├── run_app.py                     # Punto de entrada
├── env.example                    # Ejemplo de variables de entorno
├── .gitignore                     # Archivos ignorados por Git
├── .streamlitignore               # Archivos ignorados por Streamlit
└── README.md                      # Esta documentación
```

## 🛠️ Desarrollo y Mantenimiento

### Comandos Útiles

#### Verificar Estado
```bash
# Verificar configuración
python -c "from config import config; print('Config OK')"

# Verificar conexión a BD
python -c "from services.database_service import DatabaseService; print('DB OK')"

# Verificar OpenAI
python -c "from langchain_openai import ChatOpenAI; print('OpenAI OK')"
```

#### Logs y Debugging
```bash
# Ver logs en tiempo real
tail -f logs/okuoagent.log

# Limpiar archivos temporales
rm -rf images/* uploads/*

# Reiniciar aplicación
pkill -f streamlit && streamlit run run_app.py
```

### Personalización

#### Agregar Nuevas Métricas
1. Editar `utils/production_metrics.py`
2. Agregar función de cálculo
3. Actualizar `core/graph/tools.py`
4. Documentar en `data/metadata/`

#### Modificar Prompts
1. Editar `core/prompts/main_prompt.md`
2. Ajustar instrucciones específicas
3. Probar con consultas de ejemplo

#### Agregar Nuevas Tablas
1. Crear metadata YAML en `data/metadata/`
2. Actualizar `services/database_service.py`
3. Modificar `core/graph/nodes.py`

## 🔒 Seguridad y Privacidad

### Protecciones Implementadas
- **Validación de Entrada**: Sanitización de consultas
- **Límites de Memoria**: Prevención de ataques DoS
- **TTL de Sesiones**: Limpieza automática
- **Logging Seguro**: Sin datos sensibles en logs

### Mejores Prácticas
- **API Keys**: Nunca committear en el código
- **Variables de Entorno**: Usar `.env` para configuración
- **Backups**: Respaldar configuración y metadata
- **Updates**: Mantener dependencias actualizadas

## 📈 Monitoreo y Performance

### Métricas de Rendimiento
- **Tiempo de Respuesta**: < 5 segundos promedio
- **Uso de Memoria**: < 100MB por sesión
- **Disponibilidad**: 99.9% uptime
- **Precisión**: > 95% en análisis de datos

### Alertas y Notificaciones
- **Errores de BD**: Logging automático
- **Límites de Memoria**: Alertas cuando se exceden
- **Sesiones Expiradas**: Limpieza automática
- **Errores de OpenAI**: Fallbacks automáticos

## 🤝 Contribución

### Guías de Contribución
1. **Fork** el repositorio
2. **Crear** una rama para tu feature
3. **Desarrollar** siguiendo las convenciones
4. **Probar** exhaustivamente
5. **Commit** con mensajes descriptivos
6. **Pull Request** con documentación

### Convenciones de Código
- **Python**: PEP 8, type hints
- **Commits**: Conventional Commits
- **Documentación**: Markdown, docstrings
- **Testing**: Unit tests para nuevas features

## 📞 Soporte

### Canales de Ayuda
- **Issues**: GitHub Issues para bugs
- **Discussions**: GitHub Discussions para preguntas
- **Documentación**: Wiki del repositorio
- **Email**: soporte@aliar.com

### Troubleshooting Común

#### La aplicación no inicia
```bash
# Verificar dependencias
pip install -r requirements.txt

# Verificar configuración
python -c "from config import config; print(config.OPENAI_API_KEY[:10])"

# Verificar puerto
lsof -i :8502
```

#### Errores de conexión a BD
```bash
# Verificar PostgreSQL
pg_isready -h localhost -p 5432

# Verificar credenciales
psql -h localhost -U tu_usuario -d aliar_production
```

#### Problemas con OpenAI
```bash
# Verificar API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Verificar límites
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/usage
```

## 📄 Licencia

Este proyecto es propiedad de Aliar y está bajo licencia interna. Para uso comercial, contactar a la empresa.

---

**Desarrollado con ❤️ por el equipo de Aliar**

*Última actualización: Julio 2024*
