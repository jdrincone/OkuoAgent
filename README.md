# OkuoAgent

OkuoAgent es una aplicación de análisis de datos inteligente construida con Streamlit que permite a los usuarios interactuar con sus datos a través de un agente de IA conversacional.

## 🚀 Características

- **Análisis de Datos Conversacional**: Interactúa con tus datos usando lenguaje natural
- **Visualizaciones Automáticas**: Genera gráficos y visualizaciones automáticamente
- **Ejecución de Código Python**: Ejecuta código Python de forma segura para análisis avanzados
- **Interfaz Web Intuitiva**: Interfaz de usuario moderna y fácil de usar
- **Sistema de Autenticación**: Control de acceso y gestión de sesiones
- **Logging Completo**: Sistema de logs detallado para debugging

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Conexión a internet para descargar dependencias

## 🛠️ Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd OkuoAgent
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**:
   ```bash
   cp env.example .env
   # Edita el archivo .env con tus configuraciones
   ```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `env.example` con las siguientes variables:

```env
# Configuración de la API de OpenAI
OPENAI_API_KEY=tu_api_key_aqui

# Configuración de Streamlit
STREAMLIT_PAGE_TITLE=OkuoAgent
STREAMLIT_PAGE_ICON=🤖

# Configuración de la base de datos (opcional)
DATABASE_URL=sqlite:///okuoagent.db
```

### Validación de Configuración

El sistema incluye un validador de configuración que verifica que todas las variables necesarias estén configuradas correctamente antes de iniciar la aplicación.

## 🚀 Uso

### Iniciar la Aplicación

```bash
# Opción 1: Usar el script principal
python3 run_app.py

# Opción 2: Usar Streamlit directamente (recomendado)
streamlit run run_app.py
```

### Acceso a la Aplicación

Una vez iniciada, la aplicación estará disponible en:
- **URL Local**: http://localhost:8501
- **URL de Red**: http://[tu-ip]:8501

## 📁 Estructura del Proyecto

```
OkuoAgent/
├── config.py                          # Configuración principal
├── run_app.py                         # Punto de entrada de la aplicación
├── requirements.txt                   # Dependencias del proyecto
├── env.example                        # Ejemplo de variables de entorno
├── README.md                          # Documentación (este archivo)
├── core/                              # Lógica principal del agente
│   ├── backend.py                     # Backend del agente
│   ├── data_models.py                 # Modelos de datos
│   ├── graph/                         # Sistema de grafo de herramientas
│   │   ├── nodes.py                   # Nodos del grafo
│   │   ├── state.py                   # Estado del grafo
│   │   └── tools.py                   # Herramientas disponibles
│   └── prompts/                       # Prompts del sistema
│       └── main_prompt.md             # Prompt principal
├── streamlit_apps/                    # Aplicaciones Streamlit
│   ├── data_analysis_streamlit_app.py # App principal de análisis
│   └── pages/                         # Páginas de la aplicación
│       ├── login.py                   # Sistema de autenticación
│       └── python_visualisation_agent.py # Agente de visualización
├── services/                          # Servicios externos
│   └── database_service.py            # Servicio de base de datos
├── utils/                             # Utilidades
│   ├── config_validator.py            # Validador de configuración
│   └── logger.py                      # Sistema de logging
├── uploads/                           # Archivos subidos por usuarios
├── logs/                              # Archivos de log
└── images/                            # Imágenes de la aplicación
```

## 🔧 Funcionalidades Principales

### 1. Análisis Conversacional de Datos
- Sube archivos CSV, Excel, o JSON
- Haz preguntas en lenguaje natural sobre tus datos
- Obtén análisis automáticos y visualizaciones

### 2. Ejecución de Código Python
- Ejecuta código Python de forma segura
- Análisis estadísticos avanzados
- Manipulación de datos con pandas, numpy, etc.

### 3. Visualizaciones Automáticas
- Gráficos generados automáticamente
- Visualizaciones interactivas con Plotly
- Exportación de gráficos

### 4. Sistema de Sesiones
- Gestión de sesiones de usuario
- Persistencia de variables entre interacciones
- Historial de conversaciones

## 🛡️ Seguridad

- **Ejecución Segura de Código**: El código Python se ejecuta en un entorno controlado
- **Validación de Entrada**: Todas las entradas del usuario son validadas
- **Autenticación**: Sistema de login para control de acceso
- **Logging**: Registro detallado de todas las operaciones

## 📊 Logging

El sistema incluye un sistema de logging completo que registra:
- Inicio y cierre de sesiones
- Ejecución de código Python
- Errores y excepciones
- Interacciones del usuario
- Rendimiento del sistema

Los logs se almacenan en el directorio `logs/` y también se muestran en la consola.
