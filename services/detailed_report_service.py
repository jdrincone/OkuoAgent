"""
Servicio para Informe Detallado de Producción
Utiliza la misma lógica de KPIs del dashboard principal pero con análisis temporal avanzado
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from services.kpi_service import KPIService
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from config import config
from utils.production_metrics import (
    compute_metric_sackoff,
    compute_metric_pdi_mean_agroindustrial,
    compute_metric_dureza_mean_agroindustrial,
    compute_metric_fino_mean_agroindustrial,
    filter_con_adiflow,
    filter_sin_adiflow,
    compute_metric_diferencia_toneladas,
)


class DetailedReportService:
    """Servicio para generar informes detallados con análisis temporal avanzado"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el servicio de informe detallado
        
        Args:
            df: DataFrame con datos de producción
        """
        self.df = df.copy()
        self.kpi_service = KPIService(df)
        
        # Preparar datos
        if 'fecha_produccion' in self.df.columns:
            self.df['fecha_produccion'] = pd.to_datetime(self.df['fecha_produccion'])
            self.df = self.df.sort_values('fecha_produccion')
    
    def _get_period_data(self) -> Dict:
        """Obtiene datos para diferentes períodos temporales"""
        
        # Usar exactamente el mismo método que kpi_service.py
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Mes anterior
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        
        # Mes actual - usar exactamente el mismo filtro que kpi_service
        current_month_data = self.df[
            (self.df['fecha_produccion'].dt.month == current_month) & 
            (self.df['fecha_produccion'].dt.year == current_year)
        ]
        
        # Mes anterior - usar exactamente el mismo filtro que kpi_service
        previous_month_data = self.df[
            (self.df['fecha_produccion'].dt.month == prev_month) & 
            (self.df['fecha_produccion'].dt.year == prev_year)
        ]
        
        # Para compatibilidad, mantener los nombres originales
        return {
            'current_month': current_month_data,
            'previous_month': previous_month_data,
            'current_week': current_month_data,  # Usar mes actual como semana para compatibilidad
            'previous_week': previous_month_data  # Usar mes anterior como semana para compatibilidad
        }
    
    def _calculate_period_kpis(self, df: pd.DataFrame) -> Dict:
        """Calcula KPIs para un período específico"""
        if df.empty:
            return {
                'diferencia_toneladas': 0,
                'sackoff_total': 0,
                'durabilidad_promedio': 0,
                'dureza_promedio': 0,
                'finos_promedio': 0,
                'total_ordenes': 0,
                'toneladas_producidas': 0,
                'toneladas_a_producir': 0
            }
        
        # Calcular diferencia de toneladas
        cond = df["order_produccion_despachada"] == 'Si'
        df = df[cond].copy()
        diferencia_toneladas = compute_metric_diferencia_toneladas(df)
        
        # Calcular sackoff
        sackoff = compute_metric_sackoff(df)
        
        # Calcular métricas de calidad usando funciones centralizadas
        durabilidad = compute_metric_pdi_mean_agroindustrial(df)
        dureza = compute_metric_dureza_mean_agroindustrial(df)
        finos = compute_metric_fino_mean_agroindustrial(df)
        
        return {
            'diferencia_toneladas': diferencia_toneladas,
            'sackoff_total': sackoff,
            'durabilidad_promedio': durabilidad,
            'dureza_promedio': dureza,
            'finos_promedio': finos,
            'total_ordenes': len(df),
            'toneladas_producidas': df['toneladas_producidas'].sum(),
            'toneladas_a_producir': df['toneladas_a_producir'].sum()
        }
    
    def _calculate_comparisons(self, current: Dict, previous: Dict) -> Dict:
        """Calcula comparaciones entre períodos"""
        comparisons = {}
        
        for metric in ['diferencia_toneladas', 'sackoff_total', 'durabilidad_promedio', 'dureza_promedio', 'finos_promedio']:
            current_val = current.get(metric, 0)
            previous_val = previous.get(metric, 0)
            
            if previous_val != 0:
                change = current_val - previous_val
                change_pct = (change / previous_val) * 100
                
                # Lógica especial para diferencia de toneladas (más negativo = peor)
                if metric == 'diferencia_toneladas':
                    trend = "bajando" if change > 0 else "subiendo" if change < 0 else "estable"
                else:
                    # Para otras métricas, lógica normal
                    trend = "subiendo" if change > 0 else "bajando" if change < 0 else "estable"
            else:
                change = 0
                change_pct = 0
                trend = "estable"
            
            comparisons[metric] = {
                'actual': round(current_val, 2),
                'anterior': round(previous_val, 2),
                'cambio': f"{change:+.2f}",
                'cambio_pct': f"{change_pct:+.1f}%",
                'tendencia': trend
            }
        
        return comparisons
    
    def _analyze_correlations(self) -> List[Dict]:
        """Analiza correlaciones entre diferentes métricas"""
        correlations = []
        
        # Correlación entre durabilidad y dureza
        if 'durabilidad_pct_qa_agroindustrial' in self.df.columns and 'dureza_qa_agroindustrial' in self.df.columns:
            corr = self.df['durabilidad_pct_qa_agroindustrial'].corr(self.df['dureza_qa_agroindustrial'])
            if not pd.isna(corr):
                correlations.append({
                    'factor': 'Durabilidad vs Dureza',
                    'correlacion': round(corr, 3),
                    'impacto': 'positivo' if corr > 0.3 else 'negativo' if corr < -0.3 else 'bajo',
                    'descripcion': f"Correlación de {corr:.3f} entre durabilidad y dureza"
                })
        
        # Impacto del uso de Adiflow
        if 'tiene_adiflow' in self.df.columns:
            con_adiflow = self.df[self.df['tiene_adiflow'] == True]
            sin_adiflow = self.df[self.df['tiene_adiflow'] == False]
            
            if not con_adiflow.empty and not sin_adiflow.empty:
                diferencia_con = compute_metric_diferencia_toneladas(con_adiflow)
                diferencia_sin = compute_metric_diferencia_toneladas(sin_adiflow)
                
                mejora = diferencia_sin - diferencia_con  # Menor diferencia es mejor
                correlations.append({
                    'factor': 'Uso de Adiflow',
                    'impacto': 'positivo' if mejora > 0 else 'negativo',
                    'descripcion': f"Las órdenes con Adiflow muestran {abs(mejora):.2f} toneladas {'menor' if mejora > 0 else 'mayor'} diferencia"
                })
        
        # Correlación entre diferencia de toneladas y sackoff
        if 'sackoff_por_orden_produccion' in self.df.columns:
            self.df['diferencia_por_orden'] = (self.df['toneladas_a_producir'] - self.df['toneladas_producidas'] - self.df['toneladas_anuladas']).fillna(0)
            corr = self.df['diferencia_por_orden'].corr(self.df['sackoff_por_orden_produccion'])
            if not pd.isna(corr):
                correlations.append({
                    'factor': 'Diferencia vs Sackoff',
                    'correlacion': round(corr, 3),
                    'impacto': 'positivo' if corr > 0.3 else 'negativo' if corr < -0.3 else 'bajo',
                    'descripcion': f"Correlación de {corr:.3f} entre diferencia de toneladas y sackoff"
                })
        
        return correlations
    
    def _generate_alertas(self, comparisons: Dict) -> List[Dict]:
        """Genera alertas basadas en las comparaciones"""
        alertas = []
        
        # Alertas de diferencia de toneladas
        if comparisons.get('diferencia_toneladas', {}).get('actual', 0) > 100:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f"Diferencia de toneladas alta: {comparisons['diferencia_toneladas']['actual']:.1f} toneladas - Requiere atención inmediata"
            })
        
        # Alertas de sackoff
        if comparisons.get('sackoff_total', {}).get('actual', 0) > 5:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f"Sackoff alto: {comparisons['sackoff_total']['actual']:.2f}% - Pérdidas significativas"
            })
        
        # Alertas de calidad
        if comparisons.get('durabilidad_promedio', {}).get('actual', 0) < 85:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f"Durabilidad baja: {comparisons['durabilidad_promedio']['actual']:.1f}% - Problemas de calidad"
            })
        
        # Alertas positivas
        if comparisons.get('diferencia_toneladas', {}).get('tendencia') == 'bajando':
            alertas.append({
                'tipo': 'info',
                'mensaje': f"Diferencia de toneladas mejorando: {comparisons['diferencia_toneladas']['cambio_pct']} vs mes anterior"
            })
        
        return alertas
    
    def generate_detailed_report(self, user_context: str = "") -> Dict:
        """
        Genera un informe detallado completo
        
        Args:
            user_context: Contexto adicional del usuario
            
        Returns:
            Dict con el informe estructurado
        """
        
        # Obtener datos por período
        period_data = self._get_period_data()
        
        # Calcular KPIs para cada período
        current_month_kpis = self._calculate_period_kpis(period_data['current_month'])
        previous_month_kpis = self._calculate_period_kpis(period_data['previous_month'])
        current_week_kpis = self._calculate_period_kpis(period_data['current_week'])
        previous_week_kpis = self._calculate_period_kpis(period_data['previous_week'])
        
        # Calcular comparaciones
        month_comparisons = self._calculate_comparisons(current_month_kpis, previous_month_kpis)
        week_comparisons = self._calculate_comparisons(current_week_kpis, previous_week_kpis)
        
        # Analizar correlaciones
        correlations = self._analyze_correlations()
        
        # Generar alertas
        alertas = self._generate_alertas(month_comparisons)
        
        # Generar recomendaciones
        recomendaciones = self._generate_recommendations(month_comparisons, correlations)
        
        # Generar gráficos con colores corporativos
        quality_chart = self._generate_quality_chart()
        efficiency_chart = self._generate_efficiency_chart()
        sackoff_adiflow_chart = self._generate_sackoff_adiflow_chart()
        toneladas_adiflow_chart = self._generate_toneladas_adiflow_chart()
        
        # Construir el informe
        report = {
            "resumen_ejecutivo": self._generate_executive_summary(current_month_kpis, month_comparisons),
            "analisis_produccion": self._generate_production_analysis(current_month_kpis, month_comparisons, sackoff_adiflow_chart, toneladas_adiflow_chart),
            "analisis_calidad": self._generate_quality_analysis(current_month_kpis, month_comparisons),
            "analisis_diferencia_toneladas": self._generate_efficiency_analysis(current_month_kpis, month_comparisons),
            "recomendaciones": recomendaciones,
            "metricas_clave": current_month_kpis,
            "comparaciones_temporales": {
                "mes_actual_vs_anterior": month_comparisons,
                "semana_actual": {
                    "diferencia_toneladas": current_week_kpis['diferencia_toneladas'],
                    "sackoff": current_week_kpis['sackoff_total'],
                    "durabilidad": current_week_kpis['durabilidad_promedio'],
                    "tendencia": week_comparisons['diferencia_toneladas']['tendencia']
                }
            },
            "correlaciones": correlations,
            "tendencias": {
                "diferencia_toneladas_tendencia": month_comparisons['diferencia_toneladas']['tendencia'],
                "calidad_tendencia": month_comparisons['durabilidad_promedio']['tendencia'],
                "sackoff_tendencia": month_comparisons['sackoff_total']['tendencia']
            },
            "alertas": alertas,
            "graficos": {
                "calidad": quality_chart,
                "diferencia_toneladas": efficiency_chart,
                "sackoff_adiflow": sackoff_adiflow_chart,
                "toneladas_adiflow": toneladas_adiflow_chart
            }
        }
        
        return report
    
    def _generate_executive_summary(self, current_kpis: Dict, comparisons: Dict) -> str:
        """Genera el resumen ejecutivo"""
        
        diferencia_toneladas = current_kpis['diferencia_toneladas']
        sackoff = current_kpis['sackoff_total']
        durabilidad = current_kpis['durabilidad_promedio']
        total_ordenes = current_kpis['total_ordenes']
        
        diferencia_trend = comparisons['diferencia_toneladas']['tendencia']
        diferencia_change = comparisons['diferencia_toneladas']['cambio_pct']
        
        return f"""
        
        El presente informe detalla el análisis integral de la producción de alimentos para animales durante el mes actual. 
        Se procesaron {total_ordenes} órdenes de producción con una diferencia de toneladas de {diferencia_toneladas:.1f} toneladas, 
        demostrando un rendimiento {'excelente' if abs(diferencia_toneladas) <= 20 else 'bueno' if abs(diferencia_toneladas) <= 50 else 'que requiere mejora'} en las operaciones de peletización.
        
        La diferencia de toneladas muestra una tendencia {diferencia_trend} ({diferencia_change}) comparada con el mes anterior, 
        indicando {'un incremento en las pérdidas que demuestra ineficiencia operativa' if diferencia_trend == 'subiendo' else 'mejoras significativas en la eficiencia operativa' if diferencia_trend == 'bajando' else 'estabilidad en los procesos operativos'} 
        en los procesos operativos. La calidad del producto se mantiene en niveles {'satisfactorios' if durabilidad >= 90 else 'aceptables' if durabilidad >= 85 else 'que requieren atención'}, 
        con una durabilidad promedio del {durabilidad:.1f}%.
        
        El sackoff total del {sackoff:.2f}% {'refleja una gestión eficiente de pérdidas' if sackoff >= -0.3 else 'indica la necesidad de optimizar los procesos de peletización para reducir las pérdidas de producción'}. 
        {'Los resultados actuales demuestran un control efectivo de las operaciones' if sackoff >= -0.3 else 'Se recomienda revisar los parámetros operativos y fortalecer los controles de calidad para alcanzar el nivel óptimo de -0.3%'}. 
        Se identificaron oportunidades de mejora en la optimización de procesos y la implementación de controles de calidad más rigurosos para optimizar los procesos operativos.
        """
    
    def _generate_production_analysis(self, current_kpis: Dict, comparisons: Dict, sackoff_adiflow_chart: go.Figure, toneladas_adiflow_chart: go.Figure) -> str:
        """Genera el análisis de producción"""
        
        return f"""
       
        ANÁLISIS DEL SACKOFF POR SEMANA:
        • Se analiza el comportamiento del sackoff comparando semanas con y sin uso de Adiflow
        • La gráfica muestra la evolución semanal del sackoff para identificar patrones y tendencias
        • Se incluye una línea de referencia del -0.3% como nivel óptimo de sackoff
        • Este análisis permite identificar la efectividad del uso de Adiflow en la reducción de pérdidas semanales
        
        ANÁLISIS DE TONELADAS POR SEMANA:
        • Se analiza la tendencia de toneladas producidas comparando semanas con y sin uso de Adiflow
        • La gráfica muestra la evolución semanal de la producción para identificar patrones de rendimiento
        • Se incluye una línea de promedio semanal total como referencia de rendimiento
        • Este análisis permite identificar el impacto del uso de Adiflow en el volumen de producción semanal
        """
    
    def _generate_quality_analysis(self, current_kpis: Dict, comparisons: Dict) -> str:
        """Genera el análisis de calidad"""
        
        return f"""
        ANÁLISIS DE CALIDAD:
        
        • Durabilidad Promedio: {current_kpis['durabilidad_promedio']:.1f}% ({comparisons['durabilidad_promedio']['cambio_pct']} vs mes anterior)
        • Dureza Promedio: {current_kpis['dureza_promedio']:.1f}% ({comparisons['dureza_promedio']['cambio_pct']} vs mes anterior)
        • Finos Promedio: {current_kpis['finos_promedio']:.1f}% ({comparisons['finos_promedio']['cambio_pct']} vs mes anterior)
        
        EVALUACIÓN DE CALIDAD:
        • La durabilidad se mantiene en niveles {'excelentes' if current_kpis['durabilidad_promedio'] >= 95 else 'aceptables' if current_kpis['durabilidad_promedio'] >= 90 else 'que requieren mejora'}
        • La dureza está {comparisons['dureza_promedio']['tendencia']} ({comparisons['dureza_promedio']['cambio_pct']})
        • Los finos están {'dentro de parámetros' if current_kpis['finos_promedio'] <= 5 else 'por encima del objetivo'} ({comparisons['finos_promedio']['cambio_pct']})
        • Se requiere mayor consistencia en las mediciones de calidad
        """
    
    def _generate_efficiency_analysis(self, current_kpis: Dict, comparisons: Dict) -> str:
        """Genera el análisis de diferencia de toneladas"""
        
        return f"""
        ANÁLISIS DE DIFERENCIA DE TONELADAS:
        
        • Diferencia de Toneladas: {current_kpis['diferencia_toneladas']:.1f} toneladas ({comparisons['diferencia_toneladas']['cambio_pct']} vs mes anterior)
        • Sackoff Total: {current_kpis['sackoff_total']:.2f}% ({comparisons['sackoff_total']['cambio_pct']} vs mes anterior)
        • Total Órdenes: {current_kpis['total_ordenes']}
        • Toneladas Producidas: {current_kpis['toneladas_producidas']:.1f}
        
        FACTORES DE DIFERENCIA:
        • La diferencia de toneladas está {comparisons['diferencia_toneladas']['tendencia']} de manera {'significativa' if abs(float(comparisons['diferencia_toneladas']['cambio_pct'].replace('%', '').replace('+', ''))) > 5 else 'moderada'}, 
          {'demostrando un incremento en las pérdidas que requiere atención inmediata' if comparisons['diferencia_toneladas']['tendencia'] == 'subiendo' else 'indicando mejoras en la eficiencia operativa' if comparisons['diferencia_toneladas']['tendencia'] == 'bajando' else 'mostrando estabilidad en los procesos'}
        • El sackoff está {comparisons['sackoff_total']['tendencia']} {'de manera preocupante' if comparisons['sackoff_total']['tendencia'] == 'subiendo' and current_kpis['sackoff_total'] < -0.3 else 'de manera positiva' if comparisons['sackoff_total']['tendencia'] == 'bajando' or current_kpis['sackoff_total'] >= -0.3 else 'requiriendo optimización'}
        • Se identifican oportunidades de optimización en {'todos los procesos' if current_kpis['diferencia_toneladas'] > 100 else 'procesos específicos'}
        """
    
    def _generate_recommendations(self, comparisons: Dict, correlations: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        
        recomendaciones = []
        
        # Recomendaciones basadas en diferencia de toneladas
        if comparisons['diferencia_toneladas']['tendencia'] == 'subiendo':
            recomendaciones.append("Implementar controles de calidad más frecuentes para mejorar la consistencia")
            recomendaciones.append("Revisar y optimizar parámetros de peletización para reducir el sackoff")
            recomendaciones.append("Desarrollar un plan de acción inmediato para reducir las pérdidas de producción")
            recomendaciones.append("Establecer métricas de seguimiento diario para identificar causas raíz de la ineficiencia")
        
        # Recomendaciones basadas en calidad
        if comparisons['durabilidad_promedio']['tendencia'] == 'bajando':
            recomendaciones.append("Desarrollar protocolos estandarizados para mediciones de calidad")
            recomendaciones.append("Capacitar al personal en técnicas de control de calidad")
        
        # Recomendaciones basadas en correlaciones
        for corr in correlations:
            if corr['factor'] == 'Uso de Adiflow' and corr['impacto'] == 'positivo':
                recomendaciones.append("Capacitar al personal en el uso de Adiflow para maximizar su efectividad")
            elif corr['factor'] == 'Diferencia vs Sackoff' and corr['impacto'] == 'negativo':
                recomendaciones.append("Establecer métricas de seguimiento diario para identificar tendencias tempranas")
        
        # Recomendaciones generales
        recomendaciones.append("Establecer métricas de seguimiento diario para identificar tendencias tempranas")
        recomendaciones.append("Implementar un sistema de alertas automáticas para desviaciones significativas")
        recomendaciones.append("Desarrollar un plan de mejora continua basado en los datos históricos")
        
        return recomendaciones
    
    def _generate_quality_chart(self) -> go.Figure:
        """Genera gráfico de métricas de calidad con colores corporativos"""
        if self.df.empty:
            return go.Figure()
        
        # Calcular métricas de calidad promedio por producto
        quality_metrics = self.df.groupby('nombre_producto').agg({
            'durabilidad_pct_qa_agroindustrial': 'mean',
            'dureza_qa_agroindustrial': 'mean',
            'finos_pct_qa_agroindustrial': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        
        # Durabilidad
        fig.add_trace(go.Bar(
            x=quality_metrics['nombre_producto'],
            y=quality_metrics['durabilidad_pct_qa_agroindustrial'],
            name='Durabilidad',
            marker_color='#1C8074',  # PANTONE 3295 U
            opacity=0.8
        ))
        
        # Dureza
        fig.add_trace(go.Bar(
            x=quality_metrics['nombre_producto'],
            y=quality_metrics['dureza_qa_agroindustrial'],
            name='Dureza',
            marker_color='#1A494C',  # PANTONE 175-16 U
            opacity=0.8
        ))
        
        # Finos
        fig.add_trace(go.Bar(
            x=quality_metrics['nombre_producto'],
            y=quality_metrics['finos_pct_qa_agroindustrial'],
            name='Finos',
            marker_color='#94AF92',  # PANTONE 7494 U
            opacity=0.8
        ))
        
        fig.update_layout(
            title={
                'text': 'Métricas de Calidad por Producto',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1A494C'}  # PANTONE 175-16 U
            },
            xaxis_title='Producto',
            yaxis_title='Porcentaje',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1A494C'),  # PANTONE 175-16 U
            xaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9'
            ),
            yaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9'
            ),
            barmode='group',
            height=400
        )
        
        return fig
    
    def _generate_efficiency_chart(self) -> go.Figure:
        """Genera gráfico de diferencia de toneladas vs sackoff con colores corporativos"""
        if self.df.empty:
            return go.Figure()
        
        # Calcular diferencia de toneladas por orden
        self.df['diferencia_por_orden'] = (self.df['toneladas_a_producir'] - self.df['toneladas_producidas'] - self.df['toneladas_anuladas']).fillna(0)
        
        fig = go.Figure()
        
        # Scatter plot de diferencia de toneladas vs sackoff
        fig.add_trace(go.Scatter(
            x=self.df['diferencia_por_orden'],
            y=self.df['sackoff_por_orden_produccion'] if 'sackoff_por_orden_produccion' in self.df.columns else [0] * len(self.df),
            mode='markers',
            name='Órdenes',
            marker=dict(
                color='#1C8074',  # PANTONE 3295 U
                size=8,
                opacity=0.7
            ),
            text=self.df['nombre_producto'],
            hovertemplate='<b>%{text}</b><br>Diferencia: %{x:.1f} ton<br>Sackoff: %{y:.2f}%<extra></extra>'
        ))
        
        # Línea de tendencia
        if len(self.df) > 1:
            z = np.polyfit(self.df['diferencia_por_orden'], 
                          self.df['sackoff_por_orden_produccion'] if 'sackoff_por_orden_produccion' in self.df.columns else [0] * len(self.df), 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=self.df['diferencia_por_orden'],
                y=p(self.df['diferencia_por_orden']),
                mode='lines',
                name='Tendencia',
                line=dict(
                    color='#1A494C',  # PANTONE 175-16 U
                    width=2,
                    dash='dash'
                )
            ))
        
        fig.update_layout(
            title={
                'text': 'Diferencia de Toneladas vs Sackoff por Orden',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1A494C'}  # PANTONE 175-16 U
            },
            xaxis_title='Diferencia de Toneladas',
            yaxis_title='Sackoff (%)',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1A494C'),  # PANTONE 175-16 U
            xaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9'
            ),
            yaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9'
            ),
            height=400
        )
        
        return fig 

    def _generate_sackoff_adiflow_chart(self) -> go.Figure:
        """Genera gráfico de sackoff por semana con y sin Adiflow con colores corporativos"""
        if self.df.empty:
            return go.Figure()
        
        # Filtrar datos con y sin Adiflow
        df_con_adiflow = filter_con_adiflow(self.df)
        df_sin_adiflow = filter_sin_adiflow(self.df)
        
        # Calcular sackoff semanal para cada grupo
        def calculate_weekly_sackoff(df_group):
            if df_group.empty:
                return pd.DataFrame()
            
            # Crear columna de semana
            df_group = df_group.copy()
            df_group['semana'] = df_group['fecha_produccion'].dt.to_period('W')
            
            # Agrupar por semana y calcular sackoff semanal
            weekly_sackoff = df_group.groupby('semana').apply(
                lambda x: compute_metric_sackoff(x)
            ).reset_index()
            weekly_sackoff.columns = ['semana', 'sackoff']
            
            # Convertir periodo a fecha de inicio de semana
            weekly_sackoff['fecha_inicio_semana'] = weekly_sackoff['semana'].dt.start_time
            weekly_sackoff['fecha_fin_semana'] = weekly_sackoff['semana'].dt.end_time
            
            # Crear etiqueta con rango de fechas
            weekly_sackoff['rango_fechas'] = weekly_sackoff.apply(
                lambda row: f"{row['fecha_inicio_semana'].strftime('%d/%m')} - {row['fecha_fin_semana'].strftime('%d/%m')}", 
                axis=1
            )
            
            return weekly_sackoff
        
        weekly_con_adiflow = calculate_weekly_sackoff(df_con_adiflow)
        weekly_sin_adiflow = calculate_weekly_sackoff(df_sin_adiflow)
        
        fig = go.Figure()
        
        # Línea para Con Adiflow
        if not weekly_con_adiflow.empty:
            fig.add_trace(go.Scatter(
                x=weekly_con_adiflow['rango_fechas'],
                y=weekly_con_adiflow['sackoff'],
                mode='lines+markers',
                name='Con Adiflow',
                line=dict(
                    color='#1C8074',  # PANTONE 3295 U
                    width=3
                ),
                marker=dict(
                    color='#1C8074',
                    size=8
                ),
                hovertemplate='<b>Con Adiflow</b><br>Semana: %{x}<br>Sackoff: %{y:.2f}%<extra></extra>'
            ))
        
        # Línea para Sin Adiflow
        if not weekly_sin_adiflow.empty:
            fig.add_trace(go.Scatter(
                x=weekly_sin_adiflow['rango_fechas'],
                y=weekly_sin_adiflow['sackoff'],
                mode='lines+markers',
                name='Sin Adiflow',
                line=dict(
                    color='#666666',  # PANTONE 426 U
                    width=3
                ),
                marker=dict(
                    color='#666666',
                    size=8
                ),
                hovertemplate='<b>Sin Adiflow</b><br>Semana: %{x}<br>Sackoff: %{y:.2f}%<extra></extra>'
            ))
        
        # Línea de referencia para sackoff óptimo (-0.3%)
        if not weekly_con_adiflow.empty or not weekly_sin_adiflow.empty:
            fig.add_hline(
                y=-0.3,
                line_dash="dash",
                line_color="#1A494C",  # PANTONE 175-16 U
                annotation_text="Sackoff Óptimo (-0.3%)",
                annotation_position="top right",
                line_width=2
            )
        
        fig.update_layout(
            title={
                'text': 'Comportamiento del Sackoff por Semana: Con vs Sin Adiflow',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1A494C'}  # PANTONE 175-16 U
            },
            xaxis_title='Rango de Fechas (Semana)',
            yaxis_title='Sackoff (%)',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1A494C'),  # PANTONE 175-16 U
            xaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9',
                tickangle=-45  # Rotar etiquetas para mejor legibilidad
            ),
            yaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9',
                range=[0, max(
                    weekly_con_adiflow['sackoff'].max() if not weekly_con_adiflow.empty else 0,
                    weekly_sin_adiflow['sackoff'].max() if not weekly_sin_adiflow.empty else 0,
                    5  # Mínimo 5% para mostrar la línea de referencia
                ) * 1.1]
            ),
            height=450,  # Aumentar altura para acomodar etiquetas rotadas
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig 

    def _generate_toneladas_adiflow_chart(self) -> go.Figure:
        """Genera gráfico de toneladas producidas por semana con y sin Adiflow con colores corporativos"""
        if self.df.empty:
            return go.Figure()
        
        # Filtrar datos con y sin Adiflow
        df_con_adiflow = filter_con_adiflow(self.df)
        df_sin_adiflow = filter_sin_adiflow(self.df)
        
        # Calcular toneladas semanales para cada grupo
        def calculate_weekly_toneladas(df_group):
            if df_group.empty:
                return pd.DataFrame()
            
            # Crear columna de semana
            df_group = df_group.copy()
            df_group['semana'] = df_group['fecha_produccion'].dt.to_period('W')
            
            # Agrupar por semana y calcular toneladas semanales
            weekly_toneladas = df_group.groupby('semana')['toneladas_producidas'].sum().reset_index()
            weekly_toneladas.columns = ['semana', 'toneladas_producidas']
            
            # Convertir periodo a fecha de inicio de semana
            weekly_toneladas['fecha_inicio_semana'] = weekly_toneladas['semana'].dt.start_time
            weekly_toneladas['fecha_fin_semana'] = weekly_toneladas['semana'].dt.end_time
            
            # Crear etiqueta con rango de fechas
            weekly_toneladas['rango_fechas'] = weekly_toneladas.apply(
                lambda row: f"{row['fecha_inicio_semana'].strftime('%d/%m')} - {row['fecha_fin_semana'].strftime('%d/%m')}", 
                axis=1
            )
            
            return weekly_toneladas
        
        weekly_con_adiflow = calculate_weekly_toneladas(df_con_adiflow)
        weekly_sin_adiflow = calculate_weekly_toneladas(df_sin_adiflow)
        
        fig = go.Figure()
        
        # Línea para Con Adiflow
        if not weekly_con_adiflow.empty:
            fig.add_trace(go.Scatter(
                x=weekly_con_adiflow['rango_fechas'],
                y=weekly_con_adiflow['toneladas_producidas'],
                mode='lines+markers',
                name='Con Adiflow',
                line=dict(
                    color='#1C8074',  # PANTONE 3295 U
                    width=3
                ),
                marker=dict(
                    color='#1C8074',
                    size=8
                ),
                hovertemplate='<b>Con Adiflow</b><br>Semana: %{x}<br>Toneladas: %{y:,.0f} ton<extra></extra>'
            ))
        
        # Línea para Sin Adiflow
        if not weekly_sin_adiflow.empty:
            fig.add_trace(go.Scatter(
                x=weekly_sin_adiflow['rango_fechas'],
                y=weekly_sin_adiflow['toneladas_producidas'],
                mode='lines+markers',
                name='Sin Adiflow',
                line=dict(
                    color='#666666',  # PANTONE 426 U
                    width=3
                ),
                marker=dict(
                    color='#666666',
                    size=8
                ),
                hovertemplate='<b>Sin Adiflow</b><br>Semana: %{x}<br>Toneladas: %{y:,.0f} ton<extra></extra>'
            ))
        
        # Línea de promedio semanal total (opcional)
        if not weekly_con_adiflow.empty or not weekly_sin_adiflow.empty:
            # Combinar todas las semanas para calcular promedio
            all_weeks = pd.concat([
                weekly_con_adiflow[['rango_fechas', 'toneladas_producidas']] if not weekly_con_adiflow.empty else pd.DataFrame(),
                weekly_sin_adiflow[['rango_fechas', 'toneladas_producidas']] if not weekly_sin_adiflow.empty else pd.DataFrame()
            ])
            
            if not all_weeks.empty:
                # Agrupar por rango de fechas y sumar toneladas
                total_weekly = all_weeks.groupby('rango_fechas')['toneladas_producidas'].sum().reset_index()
                promedio_total = total_weekly['toneladas_producidas'].mean()
                
                # Agregar línea horizontal del promedio
                fig.add_hline(
                    y=promedio_total,
                    line_dash="dot",
                    line_color="#94AF92",  # PANTONE 7494 U
                    annotation_text=f"Promedio Semanal: {promedio_total:,.0f} ton",
                    annotation_position="top right",
                    line_width=2
                )
        
        fig.update_layout(
            title={
                'text': 'Tendencia de Toneladas Producidas por Semana: Con vs Sin Adiflow',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1A494C'}  # PANTONE 175-16 U
            },
            xaxis_title='Rango de Fechas (Semana)',
            yaxis_title='Toneladas Producidas',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#1A494C'),  # PANTONE 175-16 U
            xaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9',
                tickangle=-45  # Rotar etiquetas para mejor legibilidad
            ),
            yaxis=dict(
                gridcolor='#C9C9C9',  # PANTONE COLOR GRAY 2 U
                linecolor='#C9C9C9',
                tickformat=',',  # Formato con comas para miles
                range=[0, max(
                    weekly_con_adiflow['toneladas_producidas'].max() if not weekly_con_adiflow.empty else 0,
                    weekly_sin_adiflow['toneladas_producidas'].max() if not weekly_sin_adiflow.empty else 0,
                    1000  # Mínimo 1000 ton para mostrar la gráfica
                ) * 1.1]
            ),
            height=450,  # Aumentar altura para acomodar etiquetas rotadas
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig 