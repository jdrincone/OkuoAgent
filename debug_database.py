#!/usr/bin/env python3
"""
Debug script to check database connection and available tables
"""

import sys
import os

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.database_service import db_service
from config import config
import pandas as pd

def main():
    print("🔍 Diagnóstico de Base de Datos")
    print("=" * 50)
    
    # Test connection
    print("\n1. Probando conexión a la base de datos...")
    if db_service.test_connection():
        print("✅ Conexión exitosa")
    else:
        print("❌ Error de conexión")
        return
    
    # Get database info
    print("\n2. Información de la base de datos...")
    db_info = db_service.get_database_info()
    print(f"Tipo: {db_info.get('database_type', 'N/A')}")
    print(f"Nombre: {db_info.get('database_name', 'N/A')}")
    print(f"Host: {db_info.get('host', 'N/A')}")
    print(f"Puerto: {db_info.get('port', 'N/A')}")
    
    # Get available tables
    print("\n3. Tablas disponibles...")
    tables = db_service.get_tables()
    if tables:
        print(f"✅ Se encontraron {len(tables)} tablas:")
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table}")
    else:
        print("❌ No se encontraron tablas")
        return
    
    # Check for production_aliar specifically
    print("\n4. Verificando tabla 'production_aliar'...")
    if 'production_aliar' in tables:
        print("✅ La tabla 'production_aliar' existe")
        
        # Get table info
        table_info = db_service.get_table_info('production_aliar')
        if table_info:
            print(f"   Filas: {table_info.get('row_count', 'N/A')}")
            print(f"   Columnas: {len(table_info.get('columns', []))}")
            print("   Columnas disponibles:")
            for col in table_info.get('columns', []):
                print(f"     - {col}")
        
        # Try to load the table
        print("\n5. Intentando cargar la tabla 'production_aliar'...")
        df = db_service.load_table_as_dataframe('production_aliar')
        if df is not None:
            print(f"✅ Tabla cargada exitosamente con {len(df)} filas y {len(df.columns)} columnas")
            print("\nPrimeras 5 filas:")
            print(df.head())
        else:
            print("❌ Error al cargar la tabla")
    else:
        print("❌ La tabla 'production_aliar' NO existe")
        print("\n💡 Sugerencias:")
        print("   - Verifica el nombre exacto de la tabla")
        print("   - Revisa si la tabla tiene un nombre diferente")
        print("   - Verifica los permisos de acceso")
        
        # Show similar table names
        similar_tables = [t for t in tables if 'produccion' in t.lower() or 'aliar' in t.lower() or 'production' in t.lower()]
        if similar_tables:
            print(f"\n📋 Tablas similares encontradas:")
            for table in similar_tables:
                print(f"   - {table}")
    
    # Close connection
    db_service.disconnect()
    print("\n🔚 Conexión cerrada")

if __name__ == "__main__":
    main() 