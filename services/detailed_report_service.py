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
        
        # Fechas de referencia
        today = datetime.now()
        start_of_month = today.replace(day=1)
        start_of_previous_month = (start_of_month - timedelta(days=1)).replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())
        
        # Mes actual
        current_month = self.df[
            (self.df['fecha_produccion'] >= start_of_month) & 
            (self.df['fecha_produccion'] <= today)
        ]
        
        # Mes anterior
        previous_month = self.df[
            (self.df['fecha_produccion'] >= start_of_previous_month) & 
            (self.df['fecha_produccion'] < start_of_month)
        ]
        
        # Semana actual
        current_week = self.df[
            (self.df['fecha_produccion'] >= start_of_week) & 
            (self.df['fecha_produccion'] <= today)
        ]
        
        # Semana anterior
        start_of_previous_week = start_of_week - timedelta(days=7)
        previous_week = self.df[
            (self.df['fecha_produccion'] >= start_of_previous_week) & 
            (self.df['fecha_produccion'] < start_of_week)
        ]
        
        return {
            'current_month': current_month,
            'previous_month': previous_month,
            'current_week': current_week,
            'previous_week': previous_week
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
        diferencia_toneladas = compute_metric_diferencia_toneladas(df)
        
        # Calcular sackoff
        sackoff = compute_metric_sackoff(df)
        
        # Calcular métricas de calidad
        durabilidad = df['durabilidad_pct_qa_agroindustrial'].mean()
        dureza = df['dureza_qa_agroindustrial'].mean()
        finos = df['finos_pct_qa_agroindustrial'].mean()
        
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
        production_chart = self._generate_production_chart()
        quality_chart = self._generate_quality_chart()
        efficiency_chart = self._generate_efficiency_chart()
        
        # Construir el informe
        report = {
            "resumen_ejecutivo": self._generate_executive_summary(current_month_kpis, month_comparisons),
            "analisis_produccion": self._generate_production_analysis(current_month_kpis, month_comparisons),
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
                "produccion": production_chart,
                "calidad": quality_chart,
                "diferencia_toneladas": efficiency_chart
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
        demostrando un rendimiento {'sólido' if diferencia_toneladas <= 50 else 'que requiere mejora'} en las operaciones de peletización.
        
        La diferencia de toneladas muestra una tendencia {diferencia_trend} ({diferencia_change}) comparada con el mes anterior, 
        indicando {'mejoras significativas' if diferencia_trend == 'bajando' else 'áreas de oportunidad' if diferencia_trend == 'subiendo' else 'estabilidad'} 
        en los procesos operativos. La calidad del producto se mantiene en niveles {'satisfactorios' if durabilidad >= 90 else 'aceptables' if durabilidad >= 85 else 'que requieren atención'}, 
        con una durabilidad promedio del {durabilidad:.1f}%.
        
        El sackoff total del {sackoff:.2f}% {'indica una gestión eficiente' if sackoff <= 3 else 'requiere optimización'} 
        de las pérdidas de producción. Se identificaron oportunidades de mejora en la optimización de procesos 
        y la implementación de controles de calidad más rigurosos para optimizar los procesos operativos.
        """
    
    def _generate_production_analysis(self, current_kpis: Dict, comparisons: Dict) -> str:
        """Genera el análisis de producción"""
        
        return f"""
        ANÁLISIS DE PRODUCCIÓN:
        
        • Volumen de Producción: Se procesaron {current_kpis['total_ordenes']} órdenes durante el mes actual
        • Diferencia de Toneladas: {current_kpis['diferencia_toneladas']:.1f} toneladas ({comparisons['diferencia_toneladas']['cambio_pct']} vs mes anterior)
        • Gestión de Pérdidas: Sackoff total del {current_kpis['sackoff_total']:.2f}% ({comparisons['sackoff_total']['cambio_pct']} vs mes anterior)
        • Toneladas Producidas: {current_kpis['toneladas_producidas']:.1f} toneladas
        
        TENDENCIAS IDENTIFICADAS:
        • La diferencia de toneladas está {comparisons['diferencia_toneladas']['tendencia']} ({comparisons['diferencia_toneladas']['cambio_pct']})
        • El sackoff está {comparisons['sackoff_total']['tendencia']} ({comparisons['sackoff_total']['cambio_pct']})
        • La producción muestra {'estabilidad' if abs(float(comparisons['diferencia_toneladas']['cambio_pct'].replace('%', '').replace('+', ''))) < 5 else 'variaciones significativas'} en términos de volumen
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
        • La diferencia de toneladas está {comparisons['diferencia_toneladas']['tendencia']} de manera {'significativa' if abs(float(comparisons['diferencia_toneladas']['cambio_pct'].replace('%', '').replace('+', ''))) > 5 else 'moderada'}
        • El sackoff está {comparisons['sackoff_total']['tendencia']} {'de manera preocupante' if comparisons['sackoff_total']['tendencia'] == 'subiendo' else 'de manera positiva'}
        • Se identifican oportunidades de optimización en {'todos los procesos' if current_kpis['diferencia_toneladas'] > 100 else 'procesos específicos'}
        """
    
    def _generate_recommendations(self, comparisons: Dict, correlations: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        
        recomendaciones = []
        
        # Recomendaciones basadas en diferencia de toneladas
        if comparisons['diferencia_toneladas']['tendencia'] == 'subiendo':
            recomendaciones.append("Implementar controles de calidad más frecuentes para mejorar la consistencia")
            recomendaciones.append("Revisar y optimizar parámetros de peletización para reducir el sackoff")
        
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
    
    def _generate_production_chart(self) -> go.Figure:
        """Genera gráfico de tendencia de producción con colores corporativos"""
        if self.df.empty:
            return go.Figure()
        
        # Agrupar por fecha y calcular producción diaria
        daily_production = self.df.groupby('fecha_produccion')['toneladas_producidas'].sum().reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_production['fecha_produccion'],
            y=daily_production['toneladas_producidas'],
            mode='lines+markers',
            name='Producción Diaria',
            line=dict(
                color='#1C8074',  # PANTONE 3295 U
                width=3
            ),
            marker=dict(
                color='#1C8074',
                size=6
            ),
            fill='tonexty',
            fillcolor='rgba(230, 236, 216, 0.5)'  # PANTONE 152-2 U con transparencia
        ))
        
        fig.update_layout(
            title={
                'text': 'Tendencia de Producción Diaria',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1A494C'}  # PANTONE 175-16 U
            },
            xaxis_title='Fecha de Producción',
            yaxis_title='Toneladas Producidas',
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