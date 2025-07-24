"""
KPI Service for OkuoAgent
Handles all KPI calculations and data processing for production metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.production_metrics import (
    compute_metric_sackoff,
    compute_metric_pdi_mean_agroindustrial,
    compute_metric_dureza_mean_agroindustrial,
    compute_metric_fino_mean_agroindustrial,
    filter_con_adiflow,
    filter_sin_adiflow,
)


class KPIService:
    """Service class for calculating and managing KPIs"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize KPI service with production data
        
        Args:
            df: DataFrame with production data from produccion_aliar table
        """
        self.df = df.copy()
        if self.df['fecha_produccion'].dtype != 'datetime64[ns]':
            self.df['fecha_produccion'] = pd.to_datetime(self.df['fecha_produccion'])
    
    def _validate_data(self) -> None:
        """Validate that required columns exist in the dataset"""
        required_columns = [
            'nombre_producto', 'fecha_produccion', 'toneladas_a_producir',
            'toneladas_producidas', 'toneladas_anuladas',
            'durabilidad_pct_qa_agroindustrial', 'dureza_qa_agroindustrial',
            'finos_pct_qa_agroindustrial'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
    
    def _prepare_data(self) -> None:
        """Prepare data for KPI calculations"""
        # Convert date column to datetime
        self.df['fecha_produccion'] = pd.to_datetime(self.df['fecha_produccion'])
        
        # Sort by date to ensure proper temporal analysis
        self.df = self.df.sort_values('fecha_produccion')
    
    def _get_temporal_data(self, current_days: int = 7, previous_days: int = 30) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get current and previous period data
        
        Args:
            current_days: Number of days for current period
            previous_days: Number of days for previous period
            
        Returns:
            Tuple of (current_period_data, previous_period_data)
        """
        # Get current period (last N days)
        current_data = self.df.tail(current_days)
        
        # Get previous period (days N+1 to M from the end)
        previous_data = self.df.tail(previous_days).head(previous_days - current_days)
        
        return current_data, previous_data
    
    def _get_product_analysis(self, data: pd.DataFrame):
        if len(data) == 0:
            return None, None
        
        # Obtener todos los productos únicos
        productos = data['nombre_producto'].unique()
        resultados = []
        for producto in productos:
            df_prod = data[data['nombre_producto'] == producto]
            sackoff = compute_metric_sackoff(df_prod)
            resultados.append({
                'nombre_producto': producto,
                'sackoff': sackoff
            })
        if not resultados:
            return None, None
        # Ordenar por sackoff
        resultados = sorted(resultados, key=lambda x: x['sackoff'])
        best = resultados[0]
        worst = resultados[-1]
        return worst, best
    
    def get_last_n_days(self, n: int) -> pd.DataFrame:
        date_n_days_ago = datetime.now() - timedelta(days=n)
        return self.df[self.df['fecha_produccion'] >= date_n_days_ago]

    def calculate_kpis(self):
        # Últimos 7 días (current)
        df_7d = self.get_last_n_days(7)
        # Días 8-30 anteriores (previous)
        df_30d = self.get_last_n_days(30)
        df_prev = df_30d.head(23)  # Días 8-30

        # Con/Sin Adiflow
        df_7d_con_adiflow = filter_con_adiflow(df_7d)
        df_7d_sin_adiflow = filter_sin_adiflow(df_7d)
        df_prev_con_adiflow = filter_con_adiflow(df_prev)
        df_prev_sin_adiflow = filter_sin_adiflow(df_prev)

        def pct_change(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100

        kpis = {
            'pdi_mean_agroindustrial': {
                'name': 'PDI Mean Agroindustrial',
                'icon': '📊',
                'unit': '%',
                'inverted': False,
                'current': compute_metric_pdi_mean_agroindustrial(df_7d),
                'previous': compute_metric_pdi_mean_agroindustrial(df_prev),
            },
            'dureza_mean_agroindustrial': {
                'name': 'Dureza Mean Agroindustrial',
                'icon': '💪',
                'unit': '',
                'inverted': False,
                'current': compute_metric_dureza_mean_agroindustrial(df_7d),
                'previous': compute_metric_dureza_mean_agroindustrial(df_prev),
            },
            'fino_mean_agroindustrial': {
                'name': 'Fino Mean Agroindustrial',
                'icon': '🔬',
                'unit': '%',
                'inverted': False,
                'current': compute_metric_fino_mean_agroindustrial(df_7d),
                'previous': compute_metric_fino_mean_agroindustrial(df_prev),
            },
            'sackoff_con_adiflow': {
                'name': 'Sackoff con Adiflow',
                'icon': '📉',
                'unit': '%',
                'inverted': True,
                'current': compute_metric_sackoff(df_7d_con_adiflow),
                'previous': compute_metric_sackoff(df_prev_con_adiflow),
            },
            'sackoff_sin_adiflow': {
                'name': 'Sackoff sin Adiflow',
                'icon': '📉',
                'unit': '%',
                'inverted': True,
                'current': compute_metric_sackoff(df_7d_sin_adiflow),
                'previous': compute_metric_sackoff(df_prev_sin_adiflow),
            }
        }
        # Calcular change_pct para cada KPI
        for k in kpis:
            kpis[k]['change_pct'] = pct_change(kpis[k]['current'], kpis[k]['previous'])
        return kpis
    
    def calculate_product_kpis(self, current_days: int = 7, previous_days: int = 30) -> Dict:
        """
        Calculate product-specific KPI analysis
        
        Args:
            current_days: Number of days for current period
            previous_days: Number of days for previous period
            
        Returns:
            Dictionary with product analysis data
        """
        # Get temporal data
        current_data, previous_data = self._get_temporal_data(current_days, previous_days)
        
        # Get product analysis for both periods
        current_worst, current_best = self._get_product_analysis(current_data)
        previous_worst, previous_best = self._get_product_analysis(previous_data)
        
        return {
            'current_week': {
                'worst_product': current_worst,
                'best_product': current_best
            },
            'previous_month': {
                'worst_product': previous_worst,
                'best_product': previous_best
            }
        }
    
    def get_debug_info(self, current_days: int = 7, previous_days: int = 30) -> Dict:
        """
        Get debug information for sackoff calculations
        
        Args:
            current_days: Number of days for current period
            previous_days: Number of days for previous period
            
        Returns:
            Dictionary with debug information
        """
        current_data, previous_data = self._get_temporal_data(current_days, previous_days)
        
        # Eliminar _calculate_period_metrics y _calculate_period_metrics_without_adiflow y cualquier referencia a compute_metric_by_group
        # Mantener solo el uso de funciones centralizadas para KPIs y productos
        
        return {
            'current_week': {
                'diferencia_toneladas': 0, # Placeholder, actual calculation removed
                'total_toneladas_producidas': 0, # Placeholder, actual calculation removed
                'sackoff': 0, # Placeholder, actual calculation removed
                'sackoff_sin_adiflow': 0 # Placeholder, actual calculation removed
            },
            'previous_month': {
                'diferencia_toneladas': 0, # Placeholder, actual calculation removed
                'total_toneladas_producidas': 0, # Placeholder, actual calculation removed
                'sackoff': 0, # Placeholder, actual calculation removed
                'sackoff_sin_adiflow': 0 # Placeholder, actual calculation removed
            }
        }
    
    def get_period_info(self):
        return "Comparativo: Últimos 7 días vs Días 8-30 anteriores"


def create_kpi_service(df: pd.DataFrame) -> KPIService:
    """
    Factory function to create KPI service
    
    Args:
        df: DataFrame with production data
        
    Returns:
        KPIService instance
    """
    return KPIService(df) 