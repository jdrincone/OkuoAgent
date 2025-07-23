"""
Metadata service for OkuoAgent
Handles loading and management of table metadata from YAML files
"""

import os
import yaml
from typing import Dict, Optional
from utils.logger import logger

class MetadataService:
    def __init__(self):
        self.metadata_dir = os.path.join(os.path.dirname(__file__), "../data/metadata")
        self._metadata_cache = {}
        
    def get_table_metadata(self, table_name: str) -> Optional[Dict]:
        """Obtiene la metadata completa de una tabla desde archivo YAML"""
        if table_name in self._metadata_cache:
            return self._metadata_cache[table_name]
            
        metadata_file = os.path.join(self.metadata_dir, f"{table_name}.yaml")
        
        if not os.path.exists(metadata_file):
            logger.warning(f"Metadata file not found: {metadata_file}")
            return None
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as file:
                metadata = yaml.safe_load(file)
                self._metadata_cache[table_name] = metadata
                return metadata
        except Exception as e:
            logger.error(f"Error loading metadata for {table_name}: {str(e)}")
            return None
    
    def get_column_info(self, table_name: str) -> Dict[str, str]:
        """Obtiene información de columnas de una tabla"""
        metadata = self.get_table_metadata(table_name)
        if not metadata or 'columns' not in metadata:
            return {}
        
        column_info = {}
        for col in metadata['columns']:
            if isinstance(col, dict) and 'name' in col and 'description' in col:
                column_info[col['name']] = col['description']
            elif isinstance(col, str):
                # Formato simple: "nombre_columna: descripción"
                if ':' in col:
                    name, desc = col.split(':', 1)
                    column_info[name.strip()] = desc.strip()
        
        return column_info
    
    def get_business_context(self, table_name: str) -> str:
        """Obtiene el contexto de negocio de una tabla"""
        metadata = self.get_table_metadata(table_name)
        if not metadata:
            return ""
        
        context_parts = []
        
        if 'description' in metadata:
            context_parts.append(f"Descripción: {metadata['description']}")
        
        if 'business_rules' in metadata:
            context_parts.append("\nReglas de Negocio:")
            for rule in metadata['business_rules']:
                context_parts.append(f"- {rule}")
        
        if 'key_metrics' in metadata:
            context_parts.append("\nMétricas Clave:")
            for metric in metadata['key_metrics']:
                context_parts.append(f"- {metric}")
        
        if 'relationships' in metadata:
            context_parts.append("\nRelaciones:")
            for rel in metadata['relationships']:
                context_parts.append(f"- {rel}")
        
        return "\n".join(context_parts)
    
    def get_prompt_context(self, table_name: str) -> str:
        """Genera contexto completo para el prompt de una tabla"""
        metadata = self.get_table_metadata(table_name)
        if not metadata:
            return ""
        
        context_parts = []
        
        # Descripción general
        if 'description' in metadata:
            context_parts.append(f"## Descripción de la Tabla {table_name}")
            context_parts.append(metadata['description'])
        
        # Columnas principales
        if 'columns' in metadata:
            context_parts.append("\n### Columnas Principales:")
            for col in metadata['columns']:
                if isinstance(col, dict):
                    context_parts.append(f"- **{col['name']}**: {col['description']}")
                    if 'type' in col:
                        context_parts.append(f"  - Tipo: {col['type']}")
                    if 'business_meaning' in col:
                        context_parts.append(f"  - Significado: {col['business_meaning']}")
                elif isinstance(col, str):
                    context_parts.append(f"- {col}")
        
        # Métricas calculadas
        if 'calculated_metrics' in metadata:
            context_parts.append("\n### Métricas Calculadas:")
            for metric in metadata['calculated_metrics']:
                context_parts.append(f"- **{metric['name']}**: {metric['formula']}")
                if 'description' in metric:
                    context_parts.append(f"  - {metric['description']}")
        
        # Reglas de negocio
        if 'business_rules' in metadata:
            context_parts.append("\n### Reglas de Negocio:")
            for rule in metadata['business_rules']:
                context_parts.append(f"- {rule}")
        
        return "\n".join(context_parts)

# Instancia global del servicio
metadata_service = MetadataService() 