import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import json
import os

class DetailedReportAgent:
    """
    Agente especializado para generar informes detallados de producción.
    """
    
    def __init__(self):
        # Cargar prompt desde el archivo en core/prompts
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                  'core', 'prompts', 'detailed_report_prompt.md')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            st.error(f"No se encontró el archivo de prompt: {prompt_path}")
            self.system_prompt = "Error: No se pudo cargar el prompt del informe detallado."
    
    def generate_report(self, df: pd.DataFrame) -> Dict:
        """
        Genera un informe detallado usando el servicio especializado.
        
        Args:
            df: DataFrame con datos de producción
            
        Returns:
            Dict con el informe estructurado
        """
        
        # Usar el servicio especializado para generar el informe
        from services.detailed_report_service import DetailedReportService
        
        try:
            report_service = DetailedReportService(df)
            report = report_service.generate_detailed_report()
            return report
        except Exception as e:
            st.error(f"Error generando informe: {str(e)}")
            # Fallback a informe básico
            return self._generate_fallback_report(df)
    
    def _generate_fallback_report(self, df: pd.DataFrame) -> Dict:
        """Genera un informe básico como fallback en caso de error."""
        
        # Calcular métricas básicas
        from utils.production_metrics import compute_metric_diferencia_toneladas
        diferencia_toneladas = compute_metric_diferencia_toneladas(df)
        sackoff_total = df['sackoff_por_orden_produccion'].sum() if 'sackoff_por_orden_produccion' in df.columns else 0
        durabilidad_promedio = df['durabilidad_pct_qa_agroindustrial'].mean() if 'durabilidad_pct_qa_agroindustrial' in df.columns else 0
        dureza_promedio = df['dureza_qa_agroindustrial'].mean() if 'dureza_qa_agroindustrial' in df.columns else 0
        finos_promedio = df['finos_pct_qa_agroindustrial'].mean() if 'finos_pct_qa_agroindustrial' in df.columns else 0
        
        return {
            "resumen_ejecutivo": f"Informe básico generado para {len(df)} órdenes de producción.",
            "analisis_produccion": f"Diferencia de toneladas: {diferencia_toneladas:.1f} toneladas",
            "analisis_calidad": f"Durabilidad promedio: {durabilidad_promedio:.1f}%",
            "analisis_diferencia_toneladas": f"Sackoff total: {sackoff_total:.2f}%",
            "recomendaciones": ["Revisar datos para análisis más detallado"],
            "metricas_clave": {
                "diferencia_toneladas": diferencia_toneladas,
                "sackoff_total": sackoff_total,
                "durabilidad_promedio": durabilidad_promedio,
                "dureza_promedio": dureza_promedio,
                "finos_promedio": finos_promedio,
                "total_ordenes": len(df)
            },
            "comparaciones_temporales": {
                "mes_actual_vs_anterior": {},
                "semana_actual": {}
            },
            "correlaciones": [],
            "tendencias": {},

        }

def create_metric_with_tooltip(title: str, value: str, tooltip_text: str, icon: str = "ℹ️"):
    """
    Crea una métrica con tooltip profesional que se muestra al hacer hover
    
    Args:
        title: Título de la métrica
        value: Valor de la métrica
        tooltip_text: Texto del tooltip
        icon: Icono para el tooltip (por defecto ℹ️)
    """
    # Crear el HTML para la métrica con tooltip
    html_content = f"""
    <div style="position: relative; display: inline-block; width: 100%;">
        <div style="
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
            border-left: 5px solid #1C8074;
            transition: all 0.3s ease;
            position: relative;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            ">
                <h4 style="
                    color: #1A494C;
                    margin: 0;
                    font-size: 1rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.3px;
                ">
                    {title}
                </h4>
                <div style="
                    position: relative;
                    display: inline-block;
                    cursor: help;
                ">
                    <span style="
                        font-size: 1.2rem;
                        color: #666666;
                        opacity: 0.7;
                        transition: opacity 0.3s ease;
                    " 
                    onmouseover="this.style.opacity='1'; this.nextElementSibling.style.display='block';"
                    onmouseout="this.style.opacity='0.7'; this.nextElementSibling.style.display='none';"
                    >
                        {icon}
                    </span>
                    <div style="
                        display: none;
                        position: absolute;
                        bottom: 125%;
                        right: 0;
                        background: #1A494C;
                        color: white;
                        padding: 0.75rem;
                        border-radius: 8px;
                        font-size: 0.85rem;
                        line-height: 1.4;
                        width: 280px;
                        z-index: 1000;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                        border: 1px solid #1C8074;
                    ">
                        {tooltip_text}
                        <div style="
                            position: absolute;
                            top: 100%;
                            right: 10px;
                            border: 8px solid transparent;
                            border-top-color: #1A494C;
                        "></div>
                    </div>
                </div>
            </div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: #1C8074;
                text-align: center;
                margin-top: 0.5rem;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            ">
                {value}
            </div>
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)

def render_detailed_report_page():
    """Renderiza la página del informe detallado simplificada."""
    
    st.title("📊 Informe Detallado de Producción")
    st.markdown("---")
    
    # Cargar datos
    from streamlit_apps.components.data_loader import get_produccion_aliar_data, check_database_service
    
    # Verificar servicio de base de datos
    db_available, db_service = check_database_service()
    
    if not db_available:
        st.error("❌ Servicio de base de datos no disponible")
        return
    
    # Obtener datos
    df = get_produccion_aliar_data()
    
    if df is None or df.empty:
        st.error("No se pudieron cargar los datos de producción. Verifica la conexión a la base de datos.")
        return
    
    # Inicializar agente
    agent = DetailedReportAgent()
    
    # Botón de descarga PDF al inicio
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Descargar Informe PDF", type="primary", use_container_width=True):
            # Generar informe para PDF
            with st.spinner("🔄 Generando PDF..."):
                report = agent.generate_report(df)
                if report:
                    pdf_bytes = generate_pdf_report(report)
                    if pdf_bytes:
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_bytes,
                            file_name=f"informe_detallado_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("Error generando PDF")
    
    st.markdown("---")
    
    # Generar informe automáticamente (sin configuración visible)
    with st.spinner("🔄 Generando informe detallado..."):
        report = agent.generate_report(df)
    
    if report:
        # Mostrar informe en una sola hoja
        st.success("✅ Informe generado exitosamente!")
        
        # Resumen Ejecutivo
        st.subheader("💡 Insights")
        st.write(report['resumen_ejecutivo'])
        
        # Métricas clave con tooltips profesionales
        st.subheader("📊 KPIs Principales")
        
        col1, col2, col3 = st.columns(3)
        metricas = report['metricas_clave']
        
        with col1:
            st.markdown(f"""
            **DIFERENCIA DE TONELADAS**  
            **{metricas['diferencia_toneladas']:.1f} ton**  
            <span style='color: #1C8074;'>⚖️</span>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **SACKOFF**  
            **{metricas['sackoff_total']:.2f}%**  
            <span style='color: #1C8074;'>📉</span>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            **DURABILIDAD**  
            **{metricas['durabilidad_promedio']:.1f}%**  
            <span style='color: #1C8074;'>📊</span>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Comportamiento semanal
        st.subheader("Comportamiento semanal")
        
        # Análisis de Producción
        with st.expander("📈 Análisis de Producción", expanded=True):
            st.write(report['analisis_produccion'])
            
            # Mostrar gráfico de sackoff por semana con y sin Adiflow si está disponible
            if 'graficos' in report and 'sackoff_adiflow' in report['graficos']:
                st.subheader("Tendencia del Sackoff por Semana: Con vs Sin Adiflow")
                st.plotly_chart(report['graficos']['sackoff_adiflow'], use_container_width=True)
                
                # Agregar explicación de la gráfica
                st.info("""
                **Interpretación de la gráfica:**
                - **Línea verde**: Sackoff semanal cuando se usa Adiflow
                - **Línea gris**: Sackoff semanal cuando NO se usa Adiflow  
                - **Línea punteada**: Nivel óptimo de sackoff (-0.3%)
                - **Eje X**: Rango de fechas de cada semana (dd/mm - dd/mm)
                - **Objetivo**: Mantener el sackoff semanal en -0.3% o superior para optimizar la producción
                """)
            
            # Mostrar gráfico de toneladas por semana con y sin Adiflow si está disponible
            if 'graficos' in report and 'toneladas_adiflow' in report['graficos']:
                st.subheader("Tendencia de Toneladas Producidas por Semana: Con vs Sin Adiflow")
                st.plotly_chart(report['graficos']['toneladas_adiflow'], use_container_width=True)
                
                # Agregar explicación de la gráfica
                st.info("""
                **Interpretación de la gráfica:**
                - **Línea verde**: Toneladas semanales cuando se usa Adiflow
                - **Línea gris**: Toneladas semanales cuando NO se usa Adiflow  
                - **Línea punteada**: Promedio semanal total como referencia
                - **Eje X**: Rango de fechas de cada semana (dd/mm - dd/mm)
                - **Objetivo**: Identificar el impacto del Adiflow en el volumen de producción semanal
                """)
            

        
        # Análisis de Calidad
        with st.expander("🔍 Análisis de Calidad", expanded=True):
            st.write(report['analisis_calidad'])
            
            # Mostrar gráfico de calidad si está disponible
            if 'graficos' in report and 'calidad' in report['graficos']:
                st.plotly_chart(report['graficos']['calidad'], use_container_width=True)
        
        # Análisis de Sackoff vs Dosis de Agua
        with st.expander("💧 Sackoff vs Dosis de Agua: Con vs Sin Adiflow", expanded=True):
            # Mostrar gráfico de sackoff vs dosis de agua si está disponible
            if 'graficos' in report and 'sackoff_agua' in report['graficos']:
                st.plotly_chart(report['graficos']['sackoff_agua'], use_container_width=True)
                
                # Agregar explicación de la gráfica
                st.info("""
                **Interpretación de la gráfica:**
                - **Puntos verdes**: Órdenes con Adiflow (sackoff vs peso de agua)
                - **Puntos grises**: Órdenes sin Adiflow (sackoff vs peso de agua)
                - **Línea punteada**: Nivel óptimo de sackoff (-0.3%)
                - **Eje X**: Peso de agua utilizado (kg)
                - **Eje Y**: Sackoff por orden de producción (%)
                - **Objetivo**: Identificar la relación entre dosis de agua y pérdidas de producción
                """)
            
            # Mostrar análisis de relación entre sackoff y dosis de agua
            if 'sackoff_agua_analysis' in report and report['sackoff_agua_analysis']['has_analysis']:
                analysis = report['sackoff_agua_analysis']
                
                st.subheader("📊 Análisis de Relación: Sackoff vs Dosis de Agua")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="Sackoff Promedio (>500kg agua)",
                        value=f"{analysis['sackoff_alto_agua']:.2f}%",
                        delta=f"{analysis['sackoff_alto_agua'] - analysis['sackoff_bajo_agua']:.2f}% vs ≤500kg"
                    )
                    
                    st.metric(
                        label="Órdenes con >500kg agua",
                        value=f"{analysis['total_alto_agua']}",
                        delta=f"{analysis['sackoff_cerca_cero_alto']} cerca de cero"
                    )
                
                with col2:
                    st.metric(
                        label="Sackoff Promedio (≤500kg agua)",
                        value=f"{analysis['sackoff_bajo_agua']:.2f}%"
                    )
                    
                    st.metric(
                        label="% Órdenes cerca de cero (>500kg)",
                        value=f"{analysis['porcentaje_cerca_cero']:.1f}%"
                    )
                
                # Mostrar conclusión del análisis
                if analysis['tiene_tendencia_cerca_cero']:
                    st.success(f"""
                    **🎯 Hallazgo Clave:** 
                    Las órdenes de producción con más de 500kg de agua tienden a tener un sackoff cercano a cero 
                    ({analysis['porcentaje_cerca_cero']:.1f}% de las órdenes con >500kg tienen sackoff entre -0.5% y +0.5%).
                    
                    **📈 Implicación:** Esta tendencia sugiere que dosis de agua superiores a 500kg pueden optimizar 
                    el proceso de peletización, reduciendo las pérdidas de producción.
                    """)
                else:
                    st.info(f"""
                    **📊 Análisis de Dosis de Agua:**
                    Se analizaron {analysis['total_alto_agua']} órdenes con más de 500kg de agua.
                    El {analysis['porcentaje_cerca_cero']:.1f}% de estas órdenes tienen sackoff cercano a cero.
                    
                    **💡 Observación:** Aunque no se detecta una tendencia clara, se recomienda monitorear 
                    continuamente la relación entre dosis de agua y sackoff para optimizar los procesos.
                    """)
                
                # Mostrar estadísticas detalladas por rango
                if 'stats_por_rango' in analysis:
                    st.subheader("📋 Estadísticas por Rango de Peso de Agua")
                    
                    # Crear tabla de estadísticas
                    stats_data = []
                    for rango, stats in analysis['stats_por_rango'].items():
                        if 'sackoff_por_orden_produccion' in stats:
                            stats_data.append({
                                'Rango': rango,
                                'Sackoff Promedio (%)': f"{stats['sackoff_por_orden_produccion']['mean']:.2f}",
                                'Desv. Estándar': f"{stats['sackoff_por_orden_produccion']['std']:.2f}",
                                'Número de Órdenes': stats['sackoff_por_orden_produccion']['count']
                            })
                    
                    if stats_data:
                        st.dataframe(
                            pd.DataFrame(stats_data),
                            use_container_width=True,
                            hide_index=True
                        )
            else:
                st.warning("No hay suficientes datos para realizar el análisis de relación entre sackoff y dosis de agua.")
        
        
        # Correlaciones
        if 'correlaciones' in report and report['correlaciones']:
            st.subheader("🔗 Análisis de Correlaciones")
            
            for corr in report['correlaciones']:
                with st.expander(f"🔍 {corr['factor']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Factor:** {corr['factor']}")
                        if 'correlacion' in corr:
                            st.write(f"**Correlación:** {corr['correlacion']}")
                        st.write(f"**Impacto:** {corr['impacto']}")
                    
                    with col2:
                        st.write(f"**Descripción:** {corr['descripcion']}")
                    
                    # Indicador visual del impacto
                    if corr['impacto'] == 'positivo':
                        st.success("✅ Impacto Positivo")
                    elif corr['impacto'] == 'negativo':
                        st.error("❌ Impacto Negativo")
                    else:
                        st.info("ℹ️ Impacto Bajo")
        
        # Recomendaciones
        st.subheader("💡 Recomendaciones")
        
        for i, rec in enumerate(report['recomendaciones'], 1):
            st.write(f"**{i}.** {rec}")

def generate_pdf_report(report: Dict) -> bytes:
    """Genera un PDF del informe con colores corporativos e imágenes de gráficos"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import io
    import tempfile
    import os
    from config import config
    
    # Crear buffer para el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Definir colores corporativos exactos del prompt
    corporate_colors = {
        'primary': '#1C8074',      # PANTONE 3295 U
        'secondary': '#666666',    # PANTONE 426 U
        'accent': '#1A494C',       # PANTONE 175-16 U
        'accent2': '#94AF92',      # PANTONE 7494 U
        'light': '#E6ECD8',        # PANTONE 152-2 U
        'gray': '#C9C9C9'          # PANTONE COLOR GRAY 2 U
    }
    
    # Convertir colores hex a RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Función para convertir gráfico de Plotly a imagen
    def plotly_to_image(fig, filename):
        """Convierte un gráfico de Plotly a imagen PNG"""
        try:
            # Crear directorio temporal si no existe
            temp_dir = "temp_images"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Guardar gráfico como imagen
            img_path = os.path.join(temp_dir, filename)
            fig.write_image(img_path, width=800, height=400, scale=1)
            return img_path
        except Exception as e:
            print(f"Error guardando gráfico: {e}")
            return None
    
    # Estilos personalizados con colores corporativos
    styles = getSampleStyleSheet()
    
    # Título principal
    title_style = ParagraphStyle(
        'CorporateTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(corporate_colors['primary']),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    # Subtítulos
    subtitle_style = ParagraphStyle(
        'CorporateSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(corporate_colors['accent']),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Texto normal
    normal_style = ParagraphStyle(
        'CorporateNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor(corporate_colors['accent']),
        spaceAfter=6
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("📊 Informe Detallado de Producción", title_style))
    story.append(Spacer(1, 20))
    
    # Fecha de generación
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Resumen Ejecutivo
    story.append(Paragraph("📋 Resumen Ejecutivo", subtitle_style))
    story.append(Paragraph(report['resumen_ejecutivo'], normal_style))
    story.append(Spacer(1, 15))
    
    # Métricas Clave
    story.append(Paragraph("📊 KPIs Principales", subtitle_style))
    
    metricas = report['metricas_clave']
    kpi_data = [
        ['Métrica', 'Valor'],
        ['Diferencia de Toneladas', f"{metricas['diferencia_toneladas']:.1f} ton"],
        ['Sackoff Total', f"{metricas['sackoff_total']:.2f}%"],
        ['Durabilidad Promedio', f"{metricas['durabilidad_promedio']:.1f}%"],
        ['Dureza Promedio', f"{metricas['dureza_promedio']:.1f}%"],
        ['Finos Promedio', f"{metricas['finos_promedio']:.1f}%"],
        ['Total Órdenes', str(metricas.get('total_ordenes', 'N/A'))],
        ['Productos Únicos', str(metricas.get('productos_unicos', 'N/A'))],
        ['Plantas Activas', str(metricas.get('plantas_activas', 'N/A'))]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[2*inch, 1.5*inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(corporate_colors['primary'])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(corporate_colors['light'])),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(corporate_colors['gray'])),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # Análisis de Producción con gráfico
    story.append(Paragraph("📈 Análisis de Producción", subtitle_style))
    story.append(Paragraph(report['analisis_produccion'], normal_style))
    story.append(Spacer(1, 10))
    
    # Incluir gráfico de producción si está disponible
    if 'graficos' in report and 'produccion' in report['graficos']:
        try:
            fig = report['graficos']['produccion']
            img_path = plotly_to_image(fig, 'produccion_chart.png')
            if img_path and os.path.exists(img_path):
                img = Image(img_path, width=6*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 10))
        except Exception as e:
            print(f"Error incluyendo gráfico de producción: {e}")
    
    # Análisis de Calidad con gráfico
    story.append(Paragraph("🔍 Análisis de Calidad", subtitle_style))
    story.append(Paragraph(report['analisis_calidad'], normal_style))
    story.append(Spacer(1, 10))
    
    # Incluir gráfico de calidad si está disponible
    if 'graficos' in report and 'calidad' in report['graficos']:
        try:
            fig = report['graficos']['calidad']
            img_path = plotly_to_image(fig, 'calidad_chart.png')
            if img_path and os.path.exists(img_path):
                img = Image(img_path, width=6*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 10))
        except Exception as e:
            print(f"Error incluyendo gráfico de calidad: {e}")
    
    # Análisis de Diferencia de Toneladas con gráfico
    story.append(Paragraph("⚡ Análisis de Diferencia de Toneladas", subtitle_style))
    story.append(Paragraph(report['analisis_diferencia_toneladas'], normal_style))
    story.append(Spacer(1, 10))
    
    # Incluir gráfico de diferencia de toneladas si está disponible
    if 'graficos' in report and 'diferencia_toneladas' in report['graficos']:
        try:
            fig = report['graficos']['diferencia_toneladas']
            img_path = plotly_to_image(fig, 'diferencia_toneladas_chart.png')
            if img_path and os.path.exists(img_path):
                img = Image(img_path, width=6*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 10))
        except Exception as e:
            print(f"Error incluyendo gráfico de diferencia de toneladas: {e}")
    
    # Comparaciones Temporales
    if 'comparaciones_temporales' in report and report['comparaciones_temporales']['mes_actual_vs_anterior']:
        story.append(Paragraph("📅 Comparaciones Temporales", subtitle_style))
        
        comparisons = report['comparaciones_temporales']['mes_actual_vs_anterior']
        comp_data = [['Métrica', 'Mes Actual', 'Mes Anterior', 'Cambio', 'Tendencia']]
        
        for metric, data in comparisons.items():
            comp_data.append([
                metric.replace('_', ' ').title(),
                f"{data['actual']:.2f}",
                f"{data['anterior']:.2f}",
                data['cambio_pct'],
                data['tendencia']
            ])
        
        comp_table = Table(comp_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(corporate_colors['accent'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(corporate_colors['light'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(corporate_colors['gray'])),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(comp_table)
        story.append(Spacer(1, 20))
    
    # Correlaciones
    if 'correlaciones' in report and report['correlaciones']:
        story.append(Paragraph("🔗 Análisis de Correlaciones", subtitle_style))
        
        for corr in report['correlaciones']:
            story.append(Paragraph(f"• {corr['factor']}: {corr['descripcion']}", normal_style))
        
        story.append(Spacer(1, 15))
    
    # Recomendaciones
    story.append(Paragraph("💡 Recomendaciones", subtitle_style))
    for i, rec in enumerate(report['recomendaciones'], 1):
        story.append(Paragraph(f"{i}. {rec}", normal_style))
    
    story.append(Spacer(1, 15))
    

    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    
    # Limpiar archivos temporales
    try:
        temp_dir = "temp_images"
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(temp_dir, file))
    except Exception as e:
        print(f"Error limpiando archivos temporales: {e}")
    
    return buffer.getvalue() 