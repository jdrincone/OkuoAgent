"""
Utilidades para cálculo de métricas de producción de Aliar.
Este módulo contiene funciones especializadas para análisis de datos de producción.
"""

import pandas as pd
import numpy as np
from typing import Union, List


def compute_metric_sackoff(df: pd.DataFrame) -> float:
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    total_toneladas_a_producir = df["toneladas_a_producir"].sum()
    total_toneladas_producidas = df["toneladas_producidas"].sum()
    total_toneladas_anuladas = df["toneladas_anuladas"].sum()
    diferencia_toneladas = total_toneladas_a_producir - total_toneladas_producidas - total_toneladas_anuladas
    if total_toneladas_producidas == 0:
        return 0
    sackoff = round(diferencia_toneladas / total_toneladas_producidas * 100, 3)
    return sackoff

def compute_metric_pdi_mean_agroindustrial(df: pd.DataFrame) -> float:
    return round(df["durabilidad_pct_qa_agroindustrial"].mean(), 3)

def compute_metric_dureza_mean_agroindustrial(df: pd.DataFrame) -> float:
    return round(df["dureza_qa_agroindustrial"].mean(), 3)

def compute_metric_fino_mean_agroindustrial(df: pd.DataFrame) -> float:
    return round(df["finos_pct_qa_agroindustrial"].mean(), 3)

def compute_metric_diferencia_toneladas(df):
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    total_toneladas_a_producir = df["toneladas_a_producir"].sum()
    total_toneladas_producidas = df["toneladas_producidas"].sum()
    total_toneladas_anuladas = df["toneladas_anuladas"].sum()
    diferencia_toneladas = total_toneladas_a_producir - total_toneladas_producidas - total_toneladas_anuladas
    return diferencia_toneladas

# Funciones de filtrado por Adiflow

def filter_con_adiflow(df: pd.DataFrame) -> pd.DataFrame:
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    return df[df["tiene_adiflow"] == "Con Adiflow"]

def filter_sin_adiflow(df: pd.DataFrame) -> pd.DataFrame:
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    return df[df["tiene_adiflow"] == "Sin Adiflow"]


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs principales de producción.
    
    Args:
        df: DataFrame con datos de producción
    
    Returns:
        Diccionario con KPIs calculados
    """
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    kpis = {
        'total_toneladas_producidas': df['toneladas_producidas'].sum(),
        'total_toneladas_anuladas': df['toneladas_anuladas'].sum(),
        'total_ordenes': df['orden_produccion'].nunique(),
        'eficiencia_global': ((df['toneladas_producidas'].sum() / 
                              (df['toneladas_producidas'].sum() + df['toneladas_anuladas'].sum())) * 100),
        'sackoff_global': ((df['toneladas_a_producir'].sum() - df['toneladas_producidas'].sum() - 
                           df['toneladas_anuladas'].sum()) / df['toneladas_producidas'].sum() * 100),
        'durabilidad_promedio_qa': df['durabilidad_pct_qa_agroindustrial'].mean(),
        'dureza_promedio_qa': df['dureza_qa_agroindustrial'].mean(),
        'finos_promedio_qa': df['finos_pct_qa_agroindustrial'].mean()
    }
    
    return {k: round(v, 3) for k, v in kpis.items()}


def analyze_trends(df: pd.DataFrame, group_col: str = 'mes_produccion') -> pd.DataFrame:
    """
    Analiza tendencias temporales de métricas clave.
    
    Args:
        df: DataFrame con datos de producción
        group_col: Columna para agrupar (por defecto mes_produccion)
    
    Returns:
        DataFrame con análisis de tendencias
    """
    # Calcular variaciones mes a mes
    cond = df["order_produccion_despachada"] == 'Si'
    df = df[cond].copy()
    df['variacion_sackoff'] = df['sackoff'].pct_change() * 100
    df['variacion_produccion'] = df['total_toneladas_producidas'].pct_change() * 100
    df['variacion_eficiencia'] = df['total_toneladas_producidas'].div(
        df['total_toneladas_producidas'] + df['total_toneladas_anuladas']
    ).pct_change() * 100
    
    return df.round(3)


def detect_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.0) -> pd.DataFrame:
    """
    Detecta anomalías en una columna específica usando el método de Z-score.
    
    Args:
        df: DataFrame con datos de producción
        column: Columna a analizar
        threshold: Umbral de Z-score para considerar anomalía (por defecto 2.0)
    
    Returns:
        DataFrame con registros que contienen anomalías
    """
    z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
    anomalies = df[z_scores > threshold].copy()
    anomalies['z_score'] = z_scores[z_scores > threshold]
    
    return anomalies.sort_values('z_score', ascending=False) 