# Especificaciones Técnicas - Sistema de Informes Detallados

## 📋 Resumen Ejecutivo

El **Sistema de Informes Detallados** es una nueva funcionalidad de OkuoAgent v1.3.0 que proporciona análisis avanzado de datos de producción con generación automática de informes en PDF, incluyendo gráficos con colores corporativos y análisis temporal.

## 🏗️ Arquitectura del Sistema

### **Diagrama de Componentes**

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Dashboard     │  │  Informe        │  │   Debug      │ │
│  │   Inteligente   │  │  Detallado      │  │   View       │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 DetailedReportAgent                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   OpenAI API    │  │  Prompt Engine  │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              DetailedReportService                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   KPI Service   │  │  Data Analysis  │  │  Chart Gen.  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  PostgreSQL     │  │  Metadata       │                  │
│  │  Connection     │  │  Service        │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### **Flujo de Datos**

1. **Usuario** → Accede a pestaña "📊 Informe Detallado"
2. **Streamlit** → Carga datos y llama a `DetailedReportAgent`
3. **Agent** → Procesa con OpenAI usando `detailed_report_prompt.md`
4. **Service** → Calcula KPIs y genera gráficos con colores corporativos
5. **PDF Generator** → Crea documento con imágenes integradas
6. **UI** → Muestra informe y permite descarga

## 🔧 Componentes Técnicos

### **1. DetailedReportService**

#### **Ubicación:** `services/detailed_report_service.py`

#### **Responsabilidades:**
- Cálculo de KPIs usando lógica existente
- Análisis temporal (mes actual vs anterior)
- Generación de gráficos con colores corporativos
- Análisis de correlaciones entre métricas

#### **Métodos Principales:**

```python
class DetailedReportService:
    def generate_detailed_report(self, df: pd.DataFrame) -> Dict:
        """Genera informe completo con análisis temporal y gráficos"""
    
    def _calculate_period_kpis(self, df: pd.DataFrame) -> Dict:
        """Calcula KPIs para un período específico"""
    
    def _calculate_comparisons(self, current_kpis: Dict, previous_kpis: Dict) -> Dict:
        """Calcula comparaciones temporales"""
    
    def _analyze_correlations(self, df: pd.DataFrame) -> List[Dict]:
        """Analiza correlaciones entre métricas"""
    
    def _generate_production_chart(self, df: pd.DataFrame) -> go.Figure:
        """Genera gráfico de producción con colores corporativos"""
```

#### **Colores Corporativos Implementados:**
```python
CORPORATE_COLORS = {
    'primary': '#1C8074',      # PANTONE 3295 U
    'secondary': '#666666',    # PANTONE 426 U
    'accent': '#1A494C',       # PANTONE 175-16 U
    'accent2': '#94AF92',      # PANTONE 7494 U
    'light': '#E6ECD8',        # PANTONE 152-2 U
    'gray': '#C9C9C9'          # PANTONE COLOR GRAY 2 U
}
```

### **2. DetailedReportAgent**

#### **Ubicación:** `streamlit_apps/components/detailed_report.py`

#### **Responsabilidades:**
- Integración con OpenAI API
- Procesamiento del prompt especializado
- Coordinación entre UI y servicios

#### **Configuración:**
```python
class DetailedReportAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=config.OPENAI_API_KEY
        )
        self.system_prompt = self._load_system_prompt()
```

### **3. Prompt Especializado**

#### **Ubicación:** `core/prompts/detailed_report_prompt.md`

#### **Características:**
- **Instrucciones estructuradas** para análisis temporal
- **Formato JSON** para respuestas consistentes
- **Análisis de correlaciones** específico
- **Recomendaciones estratégicas** basadas en datos

#### **Estructura del Prompt:**
```markdown
# Prompt para Informe Detallado de Producción

## INSTRUCCIONES PARA EL INFORME:
### 1. ESTRUCTURA DEL INFORME:
- Resumen Ejecutivo (máximo 3 párrafos)
- Análisis de Producción (métricas clave, tendencias)
- Análisis de Calidad (durabilidad, dureza, finos)
- Recomendaciones Estratégicas

### 2. TIPO DE ANÁLISIS:
- Comparaciones temporales: Mes actual vs mes anterior
- Análisis semanal: Semana actual vs semana anterior
- Análisis por producto y planta
- Identificación de anomalías y oportunidades
- Tendencias y proyecciones
- Correlaciones entre métricas
```

## 📊 Análisis de Datos

### **KPIs Calculados**

#### **Métricas Principales:**
- **Sackoff Total:** Pérdida total incluyendo anulaciones
- **Durabilidad Promedio:** Promedio de durabilidad por orden
- **Dureza Promedio:** Promedio de dureza por orden
- **Finos Promedio:** Promedio de finos por orden

#### **Análisis Temporal:**
```python
def _calculate_comparisons(self, current_kpis: Dict, previous_kpis: Dict) -> Dict:
    """Calcula comparaciones entre períodos"""
    return {
        'sackoff': {
            'actual': current_kpis['sackoff'],
            'anterior': previous_kpis['sackoff'],
            'cambio': f"{((current_kpis['sackoff'] - previous_kpis['sackoff']) / previous_kpis['sackoff'] * 100):+.1f}%",
            'tendencia': 'subiendo' if current_kpis['sackoff'] > previous_kpis['sackoff'] else 'bajando'
        }
        # ... más métricas
    }
```

### **Correlaciones Analizadas**

#### **1. Durabilidad vs Dureza**
```python
def _analyze_durabilidad_dureza_correlation(self, df: pd.DataFrame) -> Dict:
    """Analiza correlación entre durabilidad y dureza"""
    correlation = df['durabilidad_pct_qa_agroindustrial'].corr(
        df['dureza_qa_agroindustrial']
    )
    return {
        'factor': 'Durabilidad vs Dureza',
        'correlacion': correlation,
        'interpretacion': 'Correlación positiva fuerte' if correlation > 0.7 else 'Correlación moderada'
    }
```

#### **2. Uso de Adiflow**
```python
def _analyze_adiflow_impact(self, df: pd.DataFrame) -> Dict:
    """Analiza impacto del uso de Adiflow"""
    con_adiflow = df[df['tiene_adiflow'] == 'Si']
    sin_adiflow = df[df['tiene_adiflow'] == 'No']
    
    sackoff_con = con_adiflow['sackoff'].mean()
    esackoff_sin = sin_adiflow['sackoff'].mean()
    
    return {
        'factor': 'Uso de Adiflow',
        'impacto': 'positivo' if sackoff_con > esackoff_sin else 'negativo',
        'diferencia': f"{sackoff_con - esackoff_sin:.1f}%"
    }
```

## 📄 Generación de PDF

### **Tecnologías Utilizadas**
- **ReportLab:** Generación de PDF
- **Kaleido:** Conversión de gráficos Plotly a imágenes
- **PIL:** Procesamiento de imágenes

### **Proceso de Generación**

#### **1. Conversión de Gráficos**
```python
def plotly_to_image(fig, filename: str) -> str:
    """Convierte gráfico Plotly a imagen PNG"""
    img_path = f"temp_images/{filename}"
    fig.write_image(img_path, width=800, height=400)
    return img_path
```

#### **2. Integración en PDF**
```python
def generate_pdf_report(report: Dict) -> bytes:
    """Genera PDF con imágenes integradas"""
    story = []
    
    # Título
    story.append(Paragraph("Informe Detallado de Producción", title_style))
    
    # Resumen ejecutivo
    story.append(Paragraph(report['resumen_ejecutivo'], normal_style))
    
    # Análisis con gráfico
    story.append(Paragraph("Análisis de Producción", subtitle_style))
    story.append(Paragraph(report['analisis_produccion'], normal_style))
    
    # Incluir gráfico
    if 'graficos' in report and 'produccion' in report['graficos']:
        img_path = plotly_to_image(report['graficos']['produccion'], 'produccion.png')
        img = Image(img_path, width=6*inch, height=3*inch)
        story.append(img)
    
    # ... más contenido
    
    return build_pdf(story)
```

### **Estilos Corporativos en PDF**
```python
# Definir estilos con colores corporativos
title_style = ParagraphStyle(
    'CustomTitle',
    parent=getSampleStyleSheet()['Title'],
    fontSize=24,
    textColor=HexColor('#1C8074'),  # PANTONE 3295 U
    spaceAfter=20
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=getSampleStyleSheet()['Heading2'],
    fontSize=16,
    textColor=HexColor('#1A494C'),  # PANTONE 175-16 U
    spaceAfter=12
)
```

## 🎨 Implementación de Colores Corporativos

### **Paleta PANTONE Completa**

#### **Colores Principales:**
- **Verde Principal:** `#1C8074` (PANTONE 3295 U)
  - Uso: Títulos, elementos principales, gráficos
- **Verde Oscuro:** `#1A494C` (PANTONE 175-16 U)
  - Uso: Subtítulos, texto secundario
- **Verde Grisáceo:** `#94AF92` (PANTONE 7494 U)
  - Uso: Elementos de acento, líneas secundarias

#### **Colores de Soporte:**
- **Verde Claro:** `#E6ECD8` (PANTONE 152-2 U)
  - Uso: Fondos, áreas de relleno
- **Gris:** `#C9C9C9` (PANTONE COLOR GRAY 2 U)
  - Uso: Texto secundario, líneas de separación

### **Aplicación en Gráficos Plotly**

#### **Configuración de Colores:**
```python
def _apply_corporate_colors(fig: go.Figure) -> go.Figure:
    """Aplica colores corporativos a gráfico Plotly"""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#1A494C'),  # PANTONE 175-16 U
        title=dict(
            font=dict(color='#1C8074', size=18)  # PANTONE 3295 U
        )
    )
    
    # Aplicar colores a trazas
    for trace in fig.data:
        if trace.type == 'scatter':
            trace.line.color = '#1C8074'  # PANTONE 3295 U
            trace.marker.color = '#1C8074'
        elif trace.type == 'bar':
            trace.marker.color = '#94AF92'  # PANTONE 7494 U
    
    return fig
```

## 🔍 Casos de Uso y Escenarios

### **1. Análisis Ejecutivo**
**Usuario:** Director de Producción
**Necesidad:** Resumen ejecutivo con tendencias y recomendaciones
**Resultado:** PDF con KPIs principales, análisis temporal y recomendaciones estratégicas

### **2. Análisis Operacional**
**Usuario:** Supervisor de Planta
**Resultado:** Gráficos interactivos con correlaciones y métricas por producto

### **3. Análisis de Calidad**
**Usuario:** Responsable de QA
**Necesidad:** Análisis de métricas de calidad y su evolución
**Resultado:** Análisis de durabilidad, dureza y finos con tendencias temporales

## 🚀 Performance y Optimización

### **Métricas de Rendimiento**
- **Tiempo de generación de informe:** < 30 segundos
- **Tamaño de PDF:** < 5MB
- **Resolución de imágenes:** 800×400 píxeles
- **Memoria utilizada:** < 100MB por sesión

### **Optimizaciones Implementadas**
- **Caché de cálculos** de KPIs
- **Gestión eficiente** de archivos temporales
- **Limpieza automática** después de generación
- **Lazy loading** de datos

### **Gestión de Errores**
```python
def generate_report(self, df: pd.DataFrame) -> Optional[Dict]:
    """Genera informe con manejo de errores robusto"""
    try:
        if df.empty:
            return self._generate_fallback_report()
        
        # Generar informe completo
        report = self._generate_complete_report(df)
        return report
        
    except Exception as e:
        logger.error(f"Error generando informe: {e}")
        return self._generate_fallback_report()
```

## 📈 Métricas y KPIs del Sistema

### **KPIs del Informe**
- **Sackoff Total:** Pérdida total por orden de producción
- **Durabilidad Promedio:** Calidad promedio del producto
- **Dureza Promedio:** Resistencia física promedio
- **Finos Promedio:** Granulometría promedio

### **Métricas de Análisis**
- **Cambios porcentuales** mes actual vs anterior
- **Tendencias semanales** con interpretación
- **Correlaciones** entre métricas clave
- **Anomalías** detectadas automáticamente

## 🔧 Configuración y Personalización

### **Variables de Configuración**
```python
# Configuración de colores corporativos
CORPORATE_COLORS = {
    'primary': '#1C8074',
    'secondary': '#666666',
    'accent': '#1A494C',
    'accent2': '#94AF92',
    'light': '#E6ECD8',
    'gray': '#C9C9C9'
}

# Configuración de PDF
PDF_CONFIG = {
    'image_width': 800,
    'image_height': 400,
    'page_size': 'A4',
    'margins': (1*inch, 1*inch, 1*inch, 1*inch)
}
```

### **Personalización de Prompts**
- **Editar:** `core/prompts/detailed_report_prompt.md`
- **Agregar análisis:** Nuevas secciones en el prompt
- **Modificar estructura:** Cambiar formato JSON de respuesta

## 🔮 Roadmap y Mejoras Futuras

### **Próximas Funcionalidades**
- [ ] **Exportación a Excel** con múltiples hojas
- [ ] **Alertas automáticas** basadas en umbrales
- [ ] **Dashboard ejecutivo** con KPIs en tiempo real
- [ ] **Análisis predictivo** con machine learning

### **Mejoras Técnicas**
- [ ] **Caché distribuido** para mejor performance
- [ ] **Generación asíncrona** de informes
- [ ] **Templates personalizables** para PDF
- [ ] **API REST** para integración externa

---

**Documento Técnico - Sistema de Informes Detallados v1.3.0**
*OkuoAgent - Transformando datos en insights inteligentes* 🚀 