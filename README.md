# OkuoAgent - Análisis Inteligente de Datos de Producción

## 📋 Descripción General

OkuoAgent es una aplicación web inteligente que utiliza **LangGraph** y **Streamlit** para proporcionar análisis avanzado de datos de producción de alimentos para animales. La aplicación incluye un agente conversacional especializado que puede generar visualizaciones, calcular KPIs y crear informes detallados con colores corporativos.

### 🆕 **Nueva Funcionalidad: Informe Detallado (v1.3.0)**

La versión 1.3.0 introduce un **sistema completo de informes detallados** con las siguientes características:

#### 📊 **Informe Detallado de Producción**
- **Análisis temporal avanzado** (mes actual vs anterior, semana actual)
- **Gráficos con colores corporativos** PANTONE
- **PDF profesional** con imágenes integradas
- **Análisis de correlaciones** entre métricas
- **Recomendaciones estratégicas** basadas en datos

#### 🎨 **Identidad Visual Corporativa**
- **Paleta de colores PANTONE** implementada en toda la aplicación
- **Gráficos consistentes** con la marca
- **PDF con diseño profesional** y colores corporativos

#### 📄 **Generación de PDF**
- **Imágenes de gráficos** integradas automáticamente
- **Alta resolución** (800×400 píxeles)
- **Layout optimizado** para lectura profesional
- **Gestión automática** de archivos temporales

## 🏗️ Arquitectura del Sistema

### **Componentes Principales:**

1. **Frontend (Streamlit)**
   - Interfaz web responsiva
   - Dashboard inteligente con chat
   - **Nueva pestaña de informe detallado**
   - Sistema de autenticación

2. **Backend (LangGraph)**
   - Agente conversacional especializado
   - **Nuevo agente para informes detallados**
   - Procesamiento de datos en tiempo real
   - Generación de visualizaciones

3. **Servicios de Datos**
   - Conexión a base de datos PostgreSQL
   - **Servicio de informes detallados** (`DetailedReportService`)
   - Cálculo de KPIs y métricas
   - Filtros de datos (Adiflow)

4. **Sistema de Reportes**
   - **Generación automática** de informes
   - **PDF con imágenes** y colores corporativos
   - **Análisis temporal** y comparativo
   - **Recomendaciones** basadas en datos

## 🚀 Instalación y Configuración

### **Requisitos del Sistema:**
- Python 3.8+
- PostgreSQL
- **Kaleido** (para generación de imágenes en PDF)

### **Instalación:**
```bash
# Clonar el repositorio
git clone https://github.com/jdrincone/OkuoAgent.git
cd OkuoAgent

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus credenciales

# Ejecutar la aplicación
streamlit run run_app.py
```

## 📖 Cómo Usar OkuoAgent

### **Dashboard Inteligente:**
1. Accede a la pestaña "💬 Dashboard Inteligente"
2. Haz preguntas en lenguaje natural sobre los datos
3. El agente generará visualizaciones y análisis automáticamente

### **📊 Informe Detallado (NUEVO):**
1. Accede a la pestaña "📊 Informe Detallado"
2. **Haz clic en "📄 Descargar Informe PDF"** al inicio de la página
3. El sistema generará automáticamente:
   - **Análisis temporal** (mes actual vs anterior)
   - **Gráficos con colores corporativos**
   - **PDF profesional** con imágenes integradas
   - **Recomendaciones estratégicas**

### **Características del Informe:**
- ✅ **Resumen ejecutivo** con KPIs principales
- ✅ **Análisis de producción** con gráfico de tendencias
- ✅ **Análisis de calidad** con métricas por producto
- ✅ **Comparaciones temporales** detalladas
- ✅ **Recomendaciones** accionables

## 📊 Datos y Métricas Disponibles

### **KPIs Principales:**
- **Sackoff Total** (%)
- **Durabilidad Promedio** (%)
- **Dureza Promedio** (%)
- **Finos Promedio** (%)

### **Análisis Temporal:**
- **Mes actual vs anterior** con cambios porcentuales
- **Semana actual** con tendencias
- **Análisis de correlaciones** entre métricas

### **Filtros Disponibles:**
- **Por planta** de producción
- **Por producto** específico
- **Con/sin Adiflow**
- **Por rango de fechas**

## 🎨 Características Técnicas

### **Colores Corporativos Implementados:**
- **Verde Principal:** `#1C8074` (PANTONE 3295 U)
- **Verde Oscuro:** `#1A494C` (PANTONE 175-16 U)
- **Verde Grisáceo:** `#94AF92` (PANTONE 7494 U)
- **Verde Claro:** `#E6ECD8` (PANTONE 152-2 U)
- **Gris:** `#C9C9C9` (PANTONE COLOR GRAY 2 U)

### **Tecnologías Utilizadas:**
- **Streamlit** - Interfaz web
- **LangGraph** - Agente conversacional
- **Plotly** - Visualizaciones interactivas
- **Pandas/NumPy** - Procesamiento de datos
- **ReportLab** - Generación de PDF
- **Kaleido** - Conversión de gráficos a imágenes
- **PostgreSQL** - Base de datos

## 📁 Estructura del Repositorio

```
OkuoAgent/
├── core/                          # Lógica principal del agente
│   ├── prompts/
│   │   ├── main_prompt.md        # Prompt principal del agente
│   │   └── detailed_report_prompt.md  # Prompt para informes detallados
│   └── graph/                    # Nodos de LangGraph
├── services/                     # Servicios de negocio
│   ├── database_service.py      # Conexión a base de datos
│   ├── kpi_service.py          # Cálculo de KPIs
│   └── detailed_report_service.py  # Servicio de informes detallados
├── streamlit_apps/              # Aplicaciones Streamlit
│   ├── components/              # Componentes reutilizables
│   │   ├── chat.py             # Componente de chat
│   │   ├── data_loader.py      # Cargador de datos
│   │   ├── kpi_view.py         # Vista de KPIs
│   │   ├── debug_view.py       # Vista de depuración
│   │   └── detailed_report.py  # Componente de informe detallado
│   └── pages/                  # Páginas de la aplicación
│       ├── login.py            # Página de login
│       └── detailed_report.py  # Página de informe detallado
├── utils/                       # Utilidades
│   ├── production_metrics.py   # Métricas de producción
│   └── logger.py               # Sistema de logging
├── config.py                   # Configuración centralizada
├── requirements.txt            # Dependencias
└── run_app.py                 # Punto de entrada
```

## 🔄 Desarrollo y Mantenimiento

### **Versiones Disponibles:**
- **v1.1.0** - Versión inicial con dashboard básico
- **v1.2.0** - Estabilización y documentación
- **v1.3.0** - **Informe detallado con colores corporativos e imágenes en PDF**

### **Ramas Activas:**
- `main` - Rama principal estable
- `feature/gerencial-reports` - **Nueva funcionalidad de informes detallados**

### **Próximas Mejoras:**
- [ ] Exportación a Excel
- [ ] Más tipos de gráficos
- [ ] Alertas automáticas
- [ ] Dashboard ejecutivo

## 🔒 Seguridad y Privacidad

- **Autenticación** de usuarios
- **Validación** de datos de entrada
- **Logging** de actividades
- **Gestión segura** de credenciales

## 📈 Monitoreo y Performance

- **Logging centralizado** con niveles configurables
- **Gestión de sesiones** con TTL
- **Límites de memoria** por sesión
- **Limpieza automática** de archivos temporales

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto:
- **Email:** [tu-email@ejemplo.com]
- **Issues:** [GitHub Issues](https://github.com/jdrincone/OkuoAgent/issues)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**OkuoAgent v1.3.0** - Transformando datos en insights inteligentes 🚀

