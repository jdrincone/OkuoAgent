"""
Utilidades para cálculo de métricas de producción de Aliar.
Este módulo contiene funciones especializadas para análisis de datos de producción.
"""

import pandas as pd
import numpy as np
from typing import Union, List


def compute_metric_by_group(df: pd.DataFrame, cols: Union[str, List[str]]) -> pd.DataFrame:
    """
    Calcula métricas agregadas por grupo de columnas especificadas.
    
    Args:
        df: DataFrame con datos de producción
        cols: Columna(s) para agrupar (string o lista de strings)
    
    Returns:
        DataFrame con métricas calculadas por grupo
    """
    df_group = df.groupby(cols).agg(
        total_toneladas_a_producir=("toneladas_a_producir", "sum"),
        total_toneladas_materia_prima_consumida=("toneladas_materia_prima_consumida", "sum"),
        total_toneladas_anuladas=("toneladas_anuladas", "sum"),
        total_toneladas_producidas=("toneladas_producidas", "sum"),
        cantidad_orden_produccion=("orden_produccion", "nunique"),

        pdi_mean_agroindustrial=('durabilidad_pct_qa_agroindustrial', "mean"),
        dureza_mean_agroindustrial=('dureza_qa_agroindustrial', "mean"),
        fino_mean_agroindustrial=('finos_pct_qa_agroindustrial', "mean"),

        pdi_mean_prod=('durabilidad_pct_produccion', "median"),
        dureza_mean_prod=('dureza_produccion', "median"),
        fino_mean_prod=('finos_pct_produccion', "median"),

        aceite_postengrase_mean=('control_aceite_postengrase_pct', "median"),
        presion_distribuidor_mean=('control_presion_distribuidor_psi', "median"),
        carga_alimentador_mean=('control_carga_alimentador_pct', 'median'),
        presion_acondicionador_mean=('control_presion_acondicionador_psi', "median"),
    ).reset_index()

    df_group["diferencia_toneladas"] = (df_group["total_toneladas_a_producir"] -
                                  df_group["total_toneladas_producidas"]-
                                  df_group["total_toneladas_anuladas"])

    df_group["sackoff"] = df_group["diferencia_toneladas"].div(df_group["total_toneladas_producidas"])*100
    df_group.sort_values(by=cols, ascending=True, inplace=True)
    df_group = df_group.round(3)

    return df_group


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula KPIs principales de producción.
    
    Args:
        df: DataFrame con datos de producción
    
    Returns:
        Diccionario con KPIs calculados
    """
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
    metrics = compute_metric_by_group(df, group_col)
    
    # Calcular variaciones mes a mes
    metrics['variacion_sackoff'] = metrics['sackoff'].pct_change() * 100
    metrics['variacion_produccion'] = metrics['total_toneladas_producidas'].pct_change() * 100
    metrics['variacion_eficiencia'] = metrics['total_toneladas_producidas'].div(
        metrics['total_toneladas_producidas'] + metrics['total_toneladas_anuladas']
    ).pct_change() * 100
    
    return metrics.round(3)


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


# Ejemplos de uso para el agente:
"""
# Calcular métricas por mes
metricas_mensuales = compute_metric_by_group(produccion_aliar, "mes_produccion")

# Calcular métricas por producto
metricas_producto = compute_metric_by_group(produccion_aliar, "nombre_producto")

# Calcular métricas por mes y producto
metricas_mes_producto = compute_metric_by_group(produccion_aliar, ["mes_produccion", "nombre_producto"])

# Calcular KPIs globales
kpis = calculate_kpis(produccion_aliar)

# Analizar tendencias
tendencias = analyze_trends(produccion_aliar)

# Detectar anomalías en sackoff
anomalias_sackoff = detect_anomalies(produccion_aliar, "sackoff_por_orden_produccion")
""" 