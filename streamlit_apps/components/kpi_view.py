"""
Componente para gestión de KPIs.
Maneja la visualización de KPIs y métricas de producción.
"""

import streamlit as st
import pandas as pd
from services.kpi_service import KPIService
from utils.kpi_components import (
    render_main_kpis_section, 
    render_product_analysis_section,
    render_period_info,
    render_debug_info,
    render_error_message
)


def render_kpis_section(df):
    """Renderiza la sección completa de KPIs."""
    if df is not None and len(df) > 0:
        try:
            # Instanciar el servicio de KPIs
            kpi_service = KPIService(df)
            kpis = kpi_service.calculate_kpis()
            period_info = kpi_service.get_period_info()
            product_kpis = kpi_service.calculate_product_kpis()
            
            # Display main KPIs
            render_main_kpis_section(kpis)
            
            # Display period information
            render_period_info(period_info)
            
            # Display product analysis
            render_product_analysis_section(product_kpis)
            
            st.divider()
            
        except ValueError as e:
            render_error_message(str(e))
            st.info("📋 Columnas disponibles: " + ", ".join(df.columns.tolist()))
        except Exception as e:
            render_error_message(f"Error al calcular KPIs: {str(e)}")
            st.exception(e)
    else:
        st.warning("No hay datos disponibles para mostrar KPIs")


def calculate_kpis(df):
    """Calcula los KPIs para un DataFrame dado."""
    if df is None or len(df) == 0:
        return None, None, None
    
    try:
        kpi_service = KPIService(df)
        kpis = kpi_service.calculate_kpis()
        period_info = kpi_service.get_period_info()
        product_kpis = kpi_service.calculate_product_kpis()
        return kpis, period_info, product_kpis
    except Exception as e:
        st.error(f"Error al calcular KPIs: {str(e)}")
        return None, None, None


def render_kpis_only(df):
    """Renderiza solo los KPIs principales sin análisis adicional."""
    if df is not None and len(df) > 0:
        try:
            kpi_service = KPIService(df)
            kpis = kpi_service.calculate_kpis()
            render_main_kpis_section(kpis)
        except Exception as e:
            render_error_message(f"Error al calcular KPIs: {str(e)}")


def render_period_analysis_only(df):
    """Renderiza solo el análisis de periodos."""
    if df is not None and len(df) > 0:
        try:
            kpi_service = KPIService(df)
            period_info = kpi_service.get_period_info()
            render_period_info(period_info)
        except Exception as e:
            render_error_message(f"Error al calcular análisis de periodos: {str(e)}")


def render_product_analysis_only(df):
    """Renderiza solo el análisis de productos."""
    if df is not None and len(df) > 0:
        try:
            kpi_service = KPIService(df)
            product_kpis = kpi_service.calculate_product_kpis()
            render_product_analysis_section(product_kpis)
        except Exception as e:
            render_error_message(f"Error al calcular análisis de productos: {str(e)}") 