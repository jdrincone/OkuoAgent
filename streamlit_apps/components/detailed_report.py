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
        eficiencia_general = (df['toneladas_producidas'].sum() / df['toneladas_a_producir'].sum() * 100) if df['toneladas_a_producir'].sum() > 0 else 0
        sackoff_total = df['sackoff_por_orden_produccion'].sum() if 'sackoff_por_orden_produccion' in df.columns else 0
        durabilidad_promedio = df['durabilidad_pct_qa_agroindustrial'].mean() if 'durabilidad_pct_qa_agroindustrial' in df.columns else 0
        dureza_promedio = df['dureza_qa_agroindustrial'].mean() if 'dureza_qa_agroindustrial' in df.columns else 0
        finos_promedio = df['finos_pct_qa_agroindustrial'].mean() if 'finos_pct_qa_agroindustrial' in df.columns else 0
        
        return {
            "resumen_ejecutivo": f"Informe básico generado para {len(df)} órdenes de producción.",
            "analisis_produccion": f"Eficiencia general: {eficiencia_general:.1f}%",
            "analisis_calidad": f"Durabilidad promedio: {durabilidad_promedio:.1f}%",
            "analisis_eficiencia": f"Sackoff total: {sackoff_total:.2f}%",
            "recomendaciones": ["Revisar datos para análisis más detallado"],
            "metricas_clave": {
                "eficiencia": eficiencia_general,
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
            "alertas": [{"tipo": "warning", "mensaje": "Informe generado en modo fallback"}]
        }

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
        st.subheader("📋 Resumen Ejecutivo")
        st.write(report['resumen_ejecutivo'])
        
        # Métricas clave con explicación
        st.subheader("📊 KPIs Principales - Explicación")
        
        col1, col2, col3 = st.columns(3)
        metricas = report['metricas_clave']
        
        with col1:
            st.metric("Eficiencia", f"{metricas['eficiencia']:.1f}%")
            st.info("**¿Qué significa?** Porcentaje de toneladas producidas vs planificadas. >95% es excelente.")
        
        with col2:
            st.metric("Sackoff", f"{metricas['sackoff_total']:.2f}%")
            st.info("**¿Qué significa?** Pérdidas de producción. <3% es óptimo, >5% requiere atención.")
        
        with col3:
            st.metric("Durabilidad", f"{metricas['durabilidad_promedio']:.1f}%")
            st.info("**¿Qué significa?** Resistencia del pellet. >90% es bueno, <85% requiere mejora.")
        
        st.markdown("---")
        
        # Análisis detallado
        st.subheader("🔍 Análisis Detallado")
        
        # Análisis de Producción
        with st.expander("📈 Análisis de Producción", expanded=True):
            st.write(report['analisis_produccion'])
            
            # Gráfico de tendencias si hay datos
            if 'fecha_produccion' in df.columns:
                df['fecha_produccion'] = pd.to_datetime(df['fecha_produccion'])
                daily_production = df.groupby(df['fecha_produccion'].dt.date)['toneladas_producidas'].sum().reset_index()
                
                fig = px.line(daily_production, x='fecha_produccion', y='toneladas_producidas',
                             title='Tendencia de Producción Diaria')
                st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de Calidad
        with st.expander("🔍 Análisis de Calidad", expanded=True):
            st.write(report['analisis_calidad'])
            
            # Gráfico de calidad por producto
            quality_by_product = df.groupby('nombre_producto').agg({
                'durabilidad_pct_qa_agroindustrial': 'mean',
                'dureza_qa_agroindustrial': 'mean',
                'finos_pct_qa_agroindustrial': 'mean'
            }).reset_index()
            
            if not quality_by_product.empty:
                fig = px.bar(quality_by_product, x='nombre_producto', y='durabilidad_pct_qa_agroindustrial',
                            title='Durabilidad Promedio por Producto')
                st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de Eficiencia
        with st.expander("⚡ Análisis de Eficiencia", expanded=True):
            st.write(report['analisis_eficiencia'])
            
            # Gráfico de eficiencia por planta
            efficiency_by_plant = df.groupby('planta').agg({
                'toneladas_producidas': 'sum',
                'toneladas_a_producir': 'sum'
            }).reset_index()
            efficiency_by_plant['eficiencia'] = (
                efficiency_by_plant['toneladas_producidas'] / 
                efficiency_by_plant['toneladas_a_producir'] * 100
            )
            
            fig = px.bar(efficiency_by_plant, x='planta', y='eficiencia',
                        title='Eficiencia por Planta')
            st.plotly_chart(fig, use_container_width=True)
        
        # Comparaciones temporales
        if 'comparaciones_temporales' in report and report['comparaciones_temporales']['mes_actual_vs_anterior']:
            st.subheader("📅 Comparaciones Temporales")
            
            comparisons = report['comparaciones_temporales']['mes_actual_vs_anterior']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'eficiencia' in comparisons:
                    st.metric(
                        "Eficiencia", 
                        f"{comparisons['eficiencia']['actual']:.1f}%",
                        f"{comparisons['eficiencia']['cambio_pct']}"
                    )
            
            with col2:
                if 'sackoff_total' in comparisons:
                    st.metric(
                        "Sackoff", 
                        f"{comparisons['sackoff_total']['actual']:.2f}%",
                        f"{comparisons['sackoff_total']['cambio_pct']}"
                    )
            
            with col3:
                if 'durabilidad_promedio' in comparisons:
                    st.metric(
                        "Durabilidad", 
                        f"{comparisons['durabilidad_promedio']['actual']:.1f}%",
                        f"{comparisons['durabilidad_promedio']['cambio_pct']}"
                    )
        
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
        
        # Recomendaciones y Alertas
        st.subheader("💡 Recomendaciones y Alertas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Recomendaciones")
            for i, rec in enumerate(report['recomendaciones'], 1):
                st.write(f"**{i}.** {rec}")
        
        with col2:
            if report['alertas']:
                st.subheader("⚠️ Alertas")
                for alerta in report['alertas']:
                    if alerta['tipo'] == 'warning':
                        st.warning(alerta['mensaje'])
                    elif alerta['tipo'] == 'info':
                        st.info(alerta['mensaje'])

def generate_pdf_report(report: Dict) -> bytes:
    """Genera un PDF del informe detallado."""
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            textColor=colors.HexColor('#1C8074')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#1C8074')
        )
        
        normal_style = styles['Normal']
        
        # Título
        story.append(Paragraph("📊 Informe Detallado de Producción", title_style))
        story.append(Paragraph(f"Aliar - {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Resumen Ejecutivo
        story.append(Paragraph("📋 Resumen Ejecutivo", heading_style))
        story.append(Paragraph(report['resumen_ejecutivo'], normal_style))
        story.append(Spacer(1, 20))
        
        # Métricas Clave
        story.append(Paragraph("📊 Métricas Clave", heading_style))
        metricas = report['metricas_clave']
        metricas_data = [
            ['Métrica', 'Valor'],
            ['Eficiencia General', f"{metricas['eficiencia']:.1f}%"],
            ['Sackoff Total', f"{metricas['sackoff_total']:.2f}%"],
            ['Durabilidad Promedio', f"{metricas['durabilidad_promedio']:.1f}%"],
            ['Dureza Promedio', f"{metricas['dureza_promedio']:.1f}%"],
            ['Total Órdenes', f"{metricas['total_ordenes']:,}"],
            ['Productos Únicos', str(metricas.get('productos_unicos', 'N/A'))],
            ['Plantas Activas', str(metricas.get('plantas_activas', 'N/A'))]
        ]
        
        metricas_table = Table(metricas_data, colWidths=[2*inch, 3*inch])
        metricas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1C8074')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metricas_table)
        story.append(Spacer(1, 20))
        
        # Análisis de Producción
        story.append(Paragraph("📈 Análisis de Producción", heading_style))
        story.append(Paragraph(report['analisis_produccion'], normal_style))
        story.append(Spacer(1, 20))
        
        # Análisis de Calidad
        story.append(Paragraph("🔍 Análisis de Calidad", heading_style))
        story.append(Paragraph(report['analisis_calidad'], normal_style))
        story.append(Spacer(1, 20))
        
        # Análisis de Eficiencia
        story.append(Paragraph("⚡ Análisis de Eficiencia", heading_style))
        story.append(Paragraph(report['analisis_eficiencia'], normal_style))
        story.append(Spacer(1, 20))
        
        # Recomendaciones
        story.append(Paragraph("💡 Recomendaciones", heading_style))
        for i, rec in enumerate(report['recomendaciones'], 1):
            story.append(Paragraph(f"{i}. {rec}", normal_style))
            story.append(Spacer(1, 6))
        
        # Alertas
        if report['alertas']:
            story.append(Spacer(1, 20))
            story.append(Paragraph("⚠️ Alertas y Notificaciones", heading_style))
            for alerta in report['alertas']:
                story.append(Paragraph(f"• {alerta['mensaje']}", normal_style))
                story.append(Spacer(1, 6))
        
        # Construir PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        st.error(f"Error generando PDF: {str(e)}")
        return None 