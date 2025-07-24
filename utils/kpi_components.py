"""
KPI UI Components for OkuoAgent
Provides reusable components for displaying KPIs in Streamlit
"""

import streamlit as st
from typing import Dict, Any


def render_kpi_card(kpi_data: Dict[str, Any]) -> None:
    """
    Render a single KPI card with professional styling (premium version)
    
    Args:
        kpi_data: Dictionary containing KPI information
    """
    name = kpi_data['name']
    icon = kpi_data['icon']
    unit = kpi_data['unit']
    inverted = kpi_data['inverted']
    current_val = kpi_data['current']
    previous_val = kpi_data['previous']
    change_pct = kpi_data['change_pct']
    
    # Determine change icon and color based on whether lower is better
    if inverted:
        change_icon = "📉" if change_pct < 0 else "📈" if change_pct > 0 else "➡️"
        change_color = "#28a745" if change_pct < 0 else "#dc3545" if change_pct > 0 else "#ffc107"
        change_bg = "rgba(40, 167, 69, 0.1)" if change_pct < 0 else "rgba(220, 53, 69, 0.1)" if change_pct > 0 else "rgba(255, 193, 7, 0.1)"
    else:
        change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
        change_color = "#28a745" if change_pct > 0 else "#dc3545" if change_pct < 0 else "#ffc107"
        change_bg = "rgba(40, 167, 69, 0.1)" if change_pct > 0 else "rgba(220, 53, 69, 0.1)" if change_pct < 0 else "rgba(255, 193, 7, 0.1)"
    
    # Format current value based on unit
    if unit == '%':
        current_display = f"{current_val:.1f}%"
        previous_display = f"{previous_val:.1f}%"
    elif unit == '' and name == 'Diferencia Toneladas':
        current_display = f"{current_val:,.0f}"
        previous_display = f"{previous_val:,.0f}"
    else:
        current_display = f"{current_val:.1f}"
        previous_display = f"{previous_val:.1f}"
    
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; margin: 0.75rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e9ecef; transition: all 0.3s ease; text-align: center;">
        <div style="font-size: 2.2rem; margin-bottom: 0.5rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">{icon}</div>
        <h3 style="color: #495057; margin-bottom: 0.75rem; font-size: 0.95rem; font-weight: 600; letter-spacing: 0.3px; text-transform: uppercase;">
            {name}
        </h3>
        <div style="font-size: 2rem; font-weight: 700; color: #2c3e50; margin-bottom: 0.5rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            {current_display}
        </div>
        <div style="font-size: 0.85rem; color: {change_color}; margin-bottom: 0.5rem; padding: 0.3rem 0.8rem; background: {change_bg}; border-radius: 20px; display: inline-block; font-weight: 600;">
            {change_icon} {change_pct:+.1f}%
        </div>
        <div style="font-size: 0.75rem; color: #6c757d; font-weight: 500;">
            Anterior: {previous_display}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_product_analysis_card(product_data: Dict[str, Any], title: str, period_name: str) -> None:
    """
    Render a product analysis card showing best/worst products (premium version)
    
    Args:
        product_data: Dictionary containing product analysis data
        title: Title for the period (e.g., "Semana Actual")
        period_name: Name of the period for display
    """
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h3 style="color: #2c3e50; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 600; letter-spacing: 0.5px;">
            {title}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Worst product card
    if product_data.get('worst_product'):
        worst = product_data['worst_product']
        worst_name = worst.get('nombre_producto', 'N/A')
        worst_sackoff = worst.get('sackoff', 0)
        worst_diferencia = worst.get('diferencia_toneladas', 0)
        worst_producidas = worst.get('total_toneladas_producidas', 0)
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.25rem; margin: 0.75rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e9ecef; border-left: 5px solid #dc3545; transition: all 0.3s ease;">
            <div style="text-align: center; margin-bottom: 0.75rem;">
                <div style="font-size: 1.8rem; margin-bottom: 0.4rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">🚨</div>
                <h4 style="color: #dc3545; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">
                    Mayor Sackoff
                </h4>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #dc3545; margin-bottom: 0.4rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    {worst_name}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #dc3545; margin-bottom: 0.4rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    {worst_sackoff:.1f}%
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.3rem; font-weight: 500;">
                    Diferencia: {worst_diferencia:,.0f} ton
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; font-weight: 500;">
                    Producidas: {worst_producidas:,.0f} ton
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Best product card
    if product_data.get('best_product'):
        best = product_data['best_product']
        best_name = best.get('nombre_producto', 'N/A')
        best_sackoff = best.get('sackoff', 0)
        best_diferencia = best.get('diferencia_toneladas', 0)
        best_producidas = best.get('total_toneladas_producidas', 0)
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.25rem; margin: 0.75rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e9ecef; border-left: 5px solid #28a745; transition: all 0.3s ease;">
            <div style="text-align: center; margin-bottom: 0.75rem;">
                <div style="font-size: 1.8rem; margin-bottom: 0.4rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">🏆</div>
                <h4 style="color: #28a745; margin-bottom: 0.4rem; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;">
                    Menor Sackoff
                </h4>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.3rem; font-weight: 700; color: #28a745; margin-bottom: 0.4rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    {best_name}
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #28a745; margin-bottom: 0.4rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    {best_sackoff:.1f}%
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.3rem; font-weight: 500;">
                    Diferencia: {best_diferencia:,.0f} ton
                </div>
                <div style="font-size: 0.8rem; color: #6c757d; font-weight: 500;">
                    Producidas: {best_producidas:,.0f} ton
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_main_kpis_section(kpis: Dict[str, Any]) -> None:
    """
    Render the main KPIs section with all KPI cards (3 per row) - Professional Design
    
    Args:
        kpis: Dictionary containing all KPI data
    """
    st.markdown("""
    <div style="margin: 3rem 0 2rem 0; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
        <h2 style="color: #2c3e50; text-align: center; margin-bottom: 0; font-size: 1.8rem; font-weight: 600; letter-spacing: 0.5px;">
            📊 DASHBOARD DE PRODUCCIÓN
        </h2>
        <p style="color: #6c757d; text-align: center; margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 400;">
            Indicadores Clave de Rendimiento - Semana Actual vs Mes Anterior
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # First row: PDI, Dureza, Fino
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'pdi_mean_agroindustrial' in kpis:
            render_kpi_card(kpis['pdi_mean_agroindustrial'])
    
    with col2:
        if 'dureza_mean_agroindustrial' in kpis:
            render_kpi_card(kpis['dureza_mean_agroindustrial'])
    
    with col3:
        if 'fino_mean_agroindustrial' in kpis:
            render_kpi_card(kpis['fino_mean_agroindustrial'])
    
    # Second row: Sackoff con Adiflow, Sackoff sin Adiflow, Diferencia Toneladas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'sackoff' in kpis:
            render_kpi_card(kpis['sackoff'])
    
    with col2:
        if 'sackoff_sin_adiflow' in kpis:
            render_kpi_card(kpis['sackoff_sin_adiflow'])
    
    with col3:
        if 'diferencia_toneladas' in kpis:
            render_kpi_card(kpis['diferencia_toneladas'])


def render_product_analysis_section(product_kpis: Dict[str, Any]) -> None:
    """
    Render the product analysis section (without title, integrated layout)
    
    Args:
        product_kpis: Dictionary containing product analysis data
    """
    # Create 2-column layout for product analysis
    col1, col2 = st.columns(2)
    
    with col1:
        render_product_analysis_card(
            product_kpis.get('current_week', {}),
            "📅 Semana Actual",
            "current_week"
        )
    
    with col2:
        render_product_analysis_card(
            product_kpis.get('previous_month', {}),
            "📊 Mes Anterior",
            "previous_month"
        )


def render_period_info(period_info: str) -> None:
    """
    Render period information with professional styling
    
    Args:
        period_info: String describing the analysis period
    """
    st.markdown(f"""
    <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%); border-radius: 12px; border: 1px solid #c3e6cb; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center;">
        <p style="color: #155724; font-size: 1.1rem; margin: 0; font-weight: 600; letter-spacing: 0.3px;">
            📅 <strong>Período de Análisis:</strong> {period_info}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_debug_info(debug_info: Dict[str, Any]) -> None:
    """
    Render debug information for sackoff calculations with professional styling
    
    Args:
        debug_info: Dictionary containing debug information
    """
    current = debug_info.get('current_week', {})
    previous = debug_info.get('previous_month', {})
    
    st.markdown(f"""
    <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 12px; border: 1px solid #90caf9; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <h4 style="color: #1565c0; font-size: 1.2rem; margin-bottom: 1rem; font-weight: 600; text-align: center; letter-spacing: 0.5px;">
            📊 CÁLCULO DE SACKOFF
        </h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #2196f3;">
                <h5 style="color: #1976d2; font-size: 1rem; margin-bottom: 0.75rem; font-weight: 600;">Con Adiflow</h5>
                <p style="color: #424242; font-size: 0.9rem; margin: 0.3rem 0; font-weight: 500;">
                    <strong>Semana actual:</strong> {current.get('sackoff', 0):.1f}%
                </p>
                <p style="color: #424242; font-size: 0.9rem; margin: 0.3rem 0; font-weight: 500;">
                    <strong>Mes anterior:</strong> {previous.get('sackoff', 0):.1f}%
                </p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #ff9800;">
                <h5 style="color: #f57c00; font-size: 1rem; margin-bottom: 0.75rem; font-weight: 600;">Sin Adiflow</h5>
                <p style="color: #424242; font-size: 0.9rem; margin: 0.3rem 0; font-weight: 500;">
                    <strong>Semana actual:</strong> {current.get('sackoff_sin_adiflow', 0):.1f}%
                </p>
                <p style="color: #424242; font-size: 0.9rem; margin: 0.3rem 0; font-weight: 500;">
                    <strong>Mes anterior:</strong> {previous.get('sackoff_sin_adiflow', 0):.1f}%
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_error_message(error_message: str) -> None:
    """
    Render error message with professional styling
    
    Args:
        error_message: Error message to display
    """
    st.markdown(f"""
    <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); border-radius: 12px; border: 1px solid #ef9a9a; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">❌</div>
        <h4 style="color: #c62828; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 600;">
            Error en el Sistema
        </h4>
        <p style="color: #424242; font-size: 1rem; margin: 0; font-weight: 500;">
            {error_message}
        </p>
    </div>
    """, unsafe_allow_html=True) 