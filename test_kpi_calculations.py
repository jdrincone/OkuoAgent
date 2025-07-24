#!/usr/bin/env python3
"""
Script de prueba para verificar los cálculos de los KPIs
"""

import pandas as pd
import numpy as np
from services.kpi_service import create_kpi_service
from utils.production_metrics import compute_metric_by_group

def test_sackoff_calculation():
    """Prueba el cálculo del sackoff para verificar que esté correcto"""
    
    # Crear datos de prueba con todas las columnas necesarias
    test_data = {
        'fecha_produccion': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
        'nombre_producto': ['Producto A', 'Producto B', 'Producto A', 'Producto B'],
        'orden_produccion': ['OP001', 'OP002', 'OP003', 'OP004'],
        'toneladas_a_producir': [100, 150, 120, 180],
        'toneladas_materia_prima_consumida': [95, 145, 115, 175],
        'toneladas_producidas': [90, 140, 110, 160],
        'toneladas_anuladas': [5, 5, 8, 10],
        'durabilidad_pct_qa_agroindustrial': [85, 88, 82, 90],
        'dureza_qa_agroindustrial': [75, 78, 72, 80],
        'finos_pct_qa_agroindustrial': [12, 10, 15, 8],
        'durabilidad_pct_produccion': [83, 86, 80, 88],
        'dureza_produccion': [73, 76, 70, 78],
        'finos_pct_produccion': [14, 12, 17, 10],
        'control_aceite_postengrase_pct': [85, 87, 83, 89],
        'control_presion_distribuidor_psi': [120, 125, 118, 130],
        'control_carga_alimentador_pct': [75, 78, 72, 80],
        'control_presion_acondicionador_psi': [90, 95, 88, 98],
        'tiene_adiflow': [1, 0, 1, 0]
    }
    
    df = pd.DataFrame(test_data)
    df['fecha_produccion'] = pd.to_datetime(df['fecha_produccion'])
    
    print("=== DATOS DE PRUEBA ===")
    print(df)
    print("\n")
    
    # Probar compute_metric_by_group
    print("=== PRUEBA DE compute_metric_by_group ===")
    metrics_by_date = compute_metric_by_group(df, 'fecha_produccion')
    print("Métricas por fecha:")
    print(metrics_by_date)
    print("\n")
    
    # Verificar cálculo manual del sackoff
    print("=== VERIFICACIÓN MANUAL DEL SACKOFF ===")
    for date in df['fecha_produccion'].unique():
        date_data = df[df['fecha_produccion'] == date]
        
        total_a_producir = date_data['toneladas_a_producir'].sum()
        total_producidas = date_data['toneladas_producidas'].sum()
        total_anuladas = date_data['toneladas_anuladas'].sum()
        
        diferencia = total_a_producir - total_producidas - total_anuladas
        sackoff = (diferencia / total_producidas) * 100 if total_producidas > 0 else 0
        
        print(f"Fecha: {date}")
        print(f"  Total a producir: {total_a_producir}")
        print(f"  Total producidas: {total_producidas}")
        print(f"  Total anuladas: {total_anuladas}")
        print(f"  Diferencia: {diferencia}")
        print(f"  Sackoff calculado: {sackoff:.2f}%")
        print()
    
    # Probar KPI Service
    print("=== PRUEBA DE KPI SERVICE ===")
    kpi_service = create_kpi_service(df)
    
    # Calcular KPIs
    main_kpis = kpi_service.calculate_main_kpis(current_days=2, previous_days=2)
    
    print("KPIs calculados:")
    for kpi_name, kpi_data in main_kpis.items():
        print(f"{kpi_name}:")
        print(f"  Nombre: {kpi_data['name']}")
        print(f"  Valor actual: {kpi_data['current']:.2f}")
        print(f"  Valor anterior: {kpi_data['previous']:.2f}")
        print(f"  Cambio %: {kpi_data['change_pct']:.2f}%")
        print()
    
    # Probar análisis de productos
    print("=== ANÁLISIS DE PRODUCTOS ===")
    product_kpis = kpi_service.calculate_product_kpis(current_days=2, previous_days=2)
    
    print("Análisis de productos:")
    for period, data in product_kpis.items():
        print(f"\n{period}:")
        if data.get('worst_product'):
            worst = data['worst_product']
            print(f"  Peor producto: {worst.get('nombre_producto', 'N/A')} - Sackoff: {worst.get('sackoff', 0):.2f}%")
        if data.get('best_product'):
            best = data['best_product']
            print(f"  Mejor producto: {best.get('nombre_producto', 'N/A')} - Sackoff: {best.get('sackoff', 0):.2f}%")
    
    print("\n=== VERIFICACIÓN COMPLETADA ===")

def test_real_data():
    """Prueba con datos reales si están disponibles"""
    try:
        from services.database_service import db_service
        
        if db_service.test_connection():
            df = db_service.load_table_as_dataframe("produccion_aliar")
            if df is not None:
                print("=== PRUEBA CON DATOS REALES ===")
                print(f"Datos cargados: {len(df)} registros")
                print(f"Columnas disponibles: {list(df.columns)}")
                
                # Verificar columnas requeridas
                required_columns = [
                    'nombre_producto', 'fecha_produccion', 'toneladas_a_producir',
                    'toneladas_producidas', 'toneladas_anuladas',
                    'durabilidad_pct_qa_agroindustrial', 'dureza_qa_agroindustrial',
                    'finos_pct_qa_agroindustrial'
                ]
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    print(f"⚠️ Columnas faltantes: {missing_columns}")
                else:
                    print("✅ Todas las columnas requeridas están presentes")
                    
                    # Probar KPI Service con datos reales
                    kpi_service = create_kpi_service(df)
                    main_kpis = kpi_service.calculate_main_kpis()
                    
                    print("\nKPIs con datos reales:")
                    for kpi_name, kpi_data in main_kpis.items():
                        print(f"{kpi_name}: {kpi_data['current']:.2f} (cambio: {kpi_data['change_pct']:.2f}%)")
                
        else:
            print("❌ No se pudo conectar a la base de datos")
    except ImportError:
        print("❌ Servicio de base de datos no disponible")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE CÁLCULO DE KPIs")
    print("=" * 50)
    
    test_sackoff_calculation()
    test_real_data()
    
    print("\n✅ PRUEBAS COMPLETADAS") 