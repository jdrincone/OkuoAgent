"""
KPI UI Components for OkuoAgent
Provides reusable components for displaying KPIs in Streamlit
"""

import streamlit as st
from typing import Dict, Any


def render_kpi_card(kpi_data: Dict[str, Any]) -> None:
    """
    Render a single KPI card with professional styling
    
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
        change_color = "#4CAF50" if change_pct < 0 else "#F44336" if change_pct > 0 else "#FF9800"
    else:
        change_icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
        change_color = "#4CAF50" if change_pct > 0 else "#F44336" if change_pct < 0 else "#FF9800"
    
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
    <div class="professional-card" style="text-align: center; padding: 1.5rem; margin: 1rem 0;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <h3 style="color: var(--primary-color); margin-bottom: 1rem; font-size: 1.2rem;">
            {name}
        </h3>
        <div style="font-size: 2.5rem; font-weight: bold; color: var(--primary-color); margin-bottom: 0.5rem;">
            {current_display}
        </div>
        <div style="font-size: 1rem; color: {change_color}; margin-bottom: 0.5rem;">
            {change_icon} {change_pct:+.1f}% vs mes anterior
        </div>
        <div style="font-size: 0.9rem; color: var(--secondary-color);">
            Mes anterior: {previous_display}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_product_analysis_card(product_data: Dict[str, Any], title: str, period_name: str) -> None:
    """
    Render a product analysis card showing best/worst products
    
    Args:
        product_data: Dictionary containing product analysis data
        title: Title for the period (e.g., "Semana Actual")
        period_name: Name of the period for display
    """
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h3 style="color: var(--primary-color); font-size: 1.5rem; margin-bottom: 1rem;">
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
        <div class="professional-card" style="padding: 1.5rem; margin: 1rem 0; border-left: 5px solid #F44336;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚨</div>
                <h4 style="color: #F44336; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    Mayor Sackoff
                </h4>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: bold; color: #F44336; margin-bottom: 0.5rem;">
                    {worst_name}
                </div>
                <div style="font-size: 2rem; font-weight: bold; color: #F44336; margin-bottom: 0.5rem;">
                    {worst_sackoff:.1f}%
                </div>
                <div style="font-size: 0.9rem; color: var(--secondary-color); margin-bottom: 0.5rem;">
                    Diferencia: {worst_diferencia:,.0f} ton
                </div>
                <div style="font-size: 0.9rem; color: var(--secondary-color);">
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
        <div class="professional-card" style="padding: 1.5rem; margin: 1rem 0; border-left: 5px solid #4CAF50;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏆</div>
                <h4 style="color: #4CAF50; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    Menor Sackoff
                </h4>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 1.8rem; font-weight: bold; color: #4CAF50; margin-bottom: 0.5rem;">
                    {best_name}
                </div>
                <div style="font-size: 2rem; font-weight: bold; color: #4CAF50; margin-bottom: 0.5rem;">
                    {best_sackoff:.1f}%
                </div>
                <div style="font-size: 0.9rem; color: var(--secondary-color); margin-bottom: 0.5rem;">
                    Diferencia: {best_diferencia:,.0f} ton
                </div>
                <div style="font-size: 0.9rem; color: var(--secondary-color);">
                    Producidas: {best_producidas:,.0f} ton
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_main_kpis_section(kpis: Dict[str, Any]) -> None:
    """
    Render the main KPIs section with all KPI cards
    
    Args:
        kpis: Dictionary containing all KPI data
    """
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="color: var(--primary-color); text-align: center; margin-bottom: 2rem; font-size: 2rem;">
            📊 KPIs de Producción - Semana Actual vs Mes Anterior
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create 2-column layout for KPIs
    col1, col2 = st.columns(2)
    
    with col1:
        # First column KPIs
        for kpi_key in ['pdi_mean_agroindustrial', 'dureza_mean_agroindustrial', 'fino_mean_agroindustrial']:
            if kpi_key in kpis:
                render_kpi_card(kpis[kpi_key])
    
    with col2:
        # Second column KPIs
        for kpi_key in ['sackoff', 'sackoff_sin_adiflow', 'diferencia_toneladas']:
            if kpi_key in kpis:
                render_kpi_card(kpis[kpi_key])


def render_product_analysis_section(product_kpis: Dict[str, Any]) -> None:
    """
    Render the product analysis section
    
    Args:
        product_kpis: Dictionary containing product analysis data
    """
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="color: var(--primary-color); text-align: center; margin-bottom: 2rem; font-size: 2rem;">
            🏆 Análisis de Sackoff por Producto
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
    Render period information
    
    Args:
        period_info: String describing the analysis period
    """
    st.markdown(f"""
    <div style="margin: 2rem 0; padding: 1rem; background-color: var(--very-light-green); border-radius: 10px; text-align: center;">
        <p style="color: var(--dark-green); font-size: 1rem; margin: 0;">
            📅 <strong>Período de análisis:</strong> {period_info}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_debug_info(debug_info: Dict[str, Any]) -> None:
    """
    Render debug information for sackoff calculations
    
    Args:
        debug_info: Dictionary containing debug information
    """
    current = debug_info.get('current_week', {})
    previous = debug_info.get('previous_month', {})
    
    st.info(f"""
    📊 **Cálculo de Sackoff:**
    
    **Con Adiflow:**
    - **Semana actual:** Sackoff = {current.get('sackoff', 0):.1f}%
    - **Mes anterior:** Sackoff = {previous.get('sackoff', 0):.1f}%
    
    **Sin Adiflow:**
    - **Semana actual:** Sackoff = {current.get('sackoff_sin_adiflow', 0):.1f}%
    - **Mes anterior:** Sackoff = {previous.get('sackoff_sin_adiflow', 0):.1f}%
    """)


def render_error_message(error_message: str) -> None:
    """
    Render error message with proper styling
    
    Args:
        error_message: Error message to display
    """
    st.error(f"❌ {error_message}") 