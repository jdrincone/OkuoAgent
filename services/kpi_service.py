"""
KPI Service for OkuoAgent
Handles all KPI calculations and data processing for production metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.production_metrics import compute_metric_by_group


class KPIService:
    """Service class for calculating and managing KPIs"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize KPI service with production data
        
        Args:
            df: DataFrame with production data from produccion_aliar table
        """
        self.df = df.copy()
        self._validate_data()
        self._prepare_data()
    
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
    
    def _calculate_period_metrics(self, data: pd.DataFrame, group_by: str = 'fecha_produccion') -> Dict:
        """
        Calculate metrics for a specific period using compute_metric_by_group
        
        Args:
            data: DataFrame for the period
            group_by: Column to group by (default: fecha_produccion)
            
        Returns:
            Dictionary with calculated metrics
        """
        if len(data) == 0:
            return {}
        
        # Use the compute_metric_by_group function for correct sackoff calculation
        metrics_df = compute_metric_by_group(data, group_by)
        
        # Sum numeric columns for total metrics
        numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
        total_metrics = metrics_df[numeric_columns].sum()
        
        # CORRECCIÓN: Recalcular el sackoff correctamente para el período total
        # En lugar de sumar los sackoffs por fecha, calcular el sackoff del período total
        if total_metrics['total_toneladas_producidas'] > 0:
            total_metrics['sackoff'] = (total_metrics['diferencia_toneladas'] / 
                                      total_metrics['total_toneladas_producidas'] * 100)
        else:
            total_metrics['sackoff'] = 0
        
        return total_metrics.to_dict()
    
    def _calculate_period_metrics_without_adiflow(self, data: pd.DataFrame, group_by: str = 'fecha_produccion') -> Dict:
        """
        Calculate metrics for a specific period excluding Adiflow records
        
        Args:
            data: DataFrame for the period
            group_by: Column to group by (default: fecha_produccion)
            
        Returns:
            Dictionary with calculated metrics (without Adiflow)
        """
        if len(data) == 0:
            return {}
        
        # Filter data to exclude Adiflow records (tiene_adiflow = 0)
        if 'tiene_adiflow' in data.columns:
            data_without_adiflow = data[data['tiene_adiflow'] == 0]
        else:
            # If column doesn't exist, use all data
            data_without_adiflow = data
        
        if len(data_without_adiflow) == 0:
            return {}
        
        # Use the compute_metric_by_group function for correct sackoff calculation
        metrics_df = compute_metric_by_group(data_without_adiflow, group_by)
        
        # Sum numeric columns for total metrics
        numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
        total_metrics = metrics_df[numeric_columns].sum()
        
        # CORRECCIÓN: Recalcular el sackoff correctamente para el período total
        # En lugar de sumar los sackoffs por fecha, calcular el sackoff del período total
        if total_metrics['total_toneladas_producidas'] > 0:
            total_metrics['sackoff'] = (total_metrics['diferencia_toneladas'] / 
                                      total_metrics['total_toneladas_producidas'] * 100)
        else:
            total_metrics['sackoff'] = 0
        
        return total_metrics.to_dict()
    
    def _get_product_analysis(self, data: pd.DataFrame) -> Tuple[Optional[Dict], Optional[Dict]]:
        """
        Get best and worst products by sackoff for a period
        
        Args:
            data: DataFrame for the period
            
        Returns:
            Tuple of (worst_product, best_product) dictionaries
        """
        if len(data) == 0:
            return None, None
        
        # Calculate metrics by product
        product_metrics = compute_metric_by_group(data, 'nombre_producto')
        
        if len(product_metrics) == 0:
            return None, None
        
        # Sort by sackoff (descending - worst first)
        product_metrics = product_metrics.sort_values('sackoff', ascending=False)
        
        # Get worst and best products
        worst_product = product_metrics.iloc[0].to_dict()
        best_product = product_metrics.iloc[-1].to_dict()
        
        return worst_product, best_product
    
    def calculate_main_kpis(self, current_days: int = 7, previous_days: int = 30) -> Dict:
        """
        Calculate main KPIs comparing current vs previous period
        
        Args:
            current_days: Number of days for current period
            previous_days: Number of days for previous period
            
        Returns:
            Dictionary with KPI data
        """
        # Get temporal data
        current_data, previous_data = self._get_temporal_data(current_days, previous_days)
        
        # Calculate metrics for both periods
        current_metrics = self._calculate_period_metrics(current_data)
        previous_metrics = self._calculate_period_metrics(previous_data)
        
        # Calculate metrics without Adiflow for both periods
        current_metrics_without_adiflow = self._calculate_period_metrics_without_adiflow(current_data)
        previous_metrics_without_adiflow = self._calculate_period_metrics_without_adiflow(previous_data)
        
        # Calculate KPIs with comparison
        kpis = {}
        
        # Define KPI configurations
        kpi_configs = {
            'pdi_mean_agroindustrial': {
                'name': 'PDI Mean Agroindustrial',
                'unit': '%',
                'icon': '📊',
                'inverted': False
            },
            'dureza_mean_agroindustrial': {
                'name': 'Dureza Mean Agroindustrial',
                'unit': '',
                'icon': '💪',
                'inverted': False
            },
            'fino_mean_agroindustrial': {
                'name': 'Fino Mean Agroindustrial',
                'unit': '%',
                'icon': '🔬',
                'inverted': False
            },
            'sackoff': {
                'name': 'Sackoff con Adiflow',
                'unit': '%',
                'icon': '📉',
                'inverted': True  # Lower is better
            },
            'sackoff_sin_adiflow': {
                'name': 'Sackoff sin Adiflow',
                'unit': '%',
                'icon': '📉',
                'inverted': True  # Lower is better
            },
            'diferencia_toneladas': {
                'name': 'Diferencia Toneladas',
                'unit': '',
                'icon': '⚖️',
                'inverted': True  # Lower is better
            }
        }
        
        # Calculate each KPI
        for metric_key, config in kpi_configs.items():
            # Special handling for sackoff_sin_adiflow
            if metric_key == 'sackoff_sin_adiflow':
                current_val = current_metrics_without_adiflow.get('sackoff', 0)
                previous_val = previous_metrics_without_adiflow.get('sackoff', 0)
            else:
                current_val = current_metrics.get(metric_key, 0)
                previous_val = previous_metrics.get(metric_key, 0)
            
            # Calculate percentage change
            if previous_val != 0:
                change_pct = ((current_val - previous_val) / previous_val) * 100
            else:
                change_pct = 0
            
            kpis[metric_key] = {
                'name': config['name'],
                'icon': config['icon'],
                'unit': config['unit'],
                'inverted': config['inverted'],
                'current': current_val,
                'previous': previous_val,
                'change_pct': change_pct
            }
        
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
        
        current_metrics = self._calculate_period_metrics(current_data)
        previous_metrics = self._calculate_period_metrics(previous_data)
        
        # Calculate metrics without Adiflow
        current_metrics_without_adiflow = self._calculate_period_metrics_without_adiflow(current_data)
        previous_metrics_without_adiflow = self._calculate_period_metrics_without_adiflow(previous_data)
        
        return {
            'current_week': {
                'diferencia_toneladas': current_metrics.get('diferencia_toneladas', 0),
                'total_toneladas_producidas': current_metrics.get('total_toneladas_producidas', 0),
                'sackoff': current_metrics.get('sackoff', 0),
                'sackoff_sin_adiflow': current_metrics_without_adiflow.get('sackoff', 0)
            },
            'previous_month': {
                'diferencia_toneladas': previous_metrics.get('diferencia_toneladas', 0),
                'total_toneladas_producidas': previous_metrics.get('total_toneladas_producidas', 0),
                'sackoff': previous_metrics.get('sackoff', 0),
                'sackoff_sin_adiflow': previous_metrics_without_adiflow.get('sackoff', 0)
            }
        }
    
    def get_period_info(self, current_days: int = 7, previous_days: int = 30) -> str:
        """
        Get human-readable period information
        
        Args:
            current_days: Number of days for current period
            previous_days: Number of days for previous period
            
        Returns:
            String describing the analysis period
        """
        return f"Últimos {current_days} días vs Días {current_days + 1}-{previous_days} anteriores"


def create_kpi_service(df: pd.DataFrame) -> KPIService:
    """
    Factory function to create KPI service
    
    Args:
        df: DataFrame with production data
        
    Returns:
        KPIService instance
    """
    return KPIService(df) 