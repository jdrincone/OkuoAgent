"""
Metadata service for OkuoAgent
Handles loading and management of table metadata from YAML files
"""

import yaml
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config import config
import logging

logger = logging.getLogger(__name__)

@dataclass
class ColumnMetadata:
    """Metadata for a single column"""
    nombre: str
    tipo: str
    descripcion: str

@dataclass
class CalculatedMetric:
    """Metadata for a calculated metric"""
    nombre: str
    formula: str
    descripcion: str

@dataclass
class BusinessRelation:
    """Business relationship or concept"""
    concepto: str
    descripcion: str

@dataclass
class TableMetadata:
    """Complete metadata for a table"""
    tabla: str
    descripcion: str
    columnas: List[ColumnMetadata]
    metricas_calculadas: List[CalculatedMetric]
    relaciones_negocio: List[BusinessRelation]
    rangos_esperados: Dict[str, Dict[str, Any]]
    analisis_recomendados: List[Dict[str, Any]]

class MetadataService:
    """Service for managing table metadata"""
    
    def __init__(self):
        self.metadata_cache = {}
        self.metadata_dir = os.path.join(config.PROJECT_ROOT, "data", "metadata")
        
        # Ensure metadata directory exists
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)
    
    def load_table_metadata(self, table_name: str) -> Optional[TableMetadata]:
        """Load metadata for a specific table"""
        try:
            # Check cache first
            if table_name in self.metadata_cache:
                return self.metadata_cache[table_name]
            
            # Load from YAML file
            yaml_path = os.path.join(self.metadata_dir, f"{table_name}.yaml")
            if not os.path.exists(yaml_path):
                logger.warning(f"Metadata file not found for table {table_name}: {yaml_path}")
                return None
            
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Parse metadata
            metadata = self._parse_metadata(data)
            
            # Cache the result
            self.metadata_cache[table_name] = metadata
            
            logger.info(f"Loaded metadata for table {table_name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Error loading metadata for table {table_name}: {str(e)}")
            return None
    
    def _parse_metadata(self, data: Dict) -> TableMetadata:
        """Parse YAML data into TableMetadata object"""
        # Parse columns
        columnas = []
        for col_data in data.get('columnas', []):
            columnas.append(ColumnMetadata(
                nombre=col_data['nombre'],
                tipo=col_data['tipo'],
                descripcion=col_data['descripcion']
            ))
        
        # Parse calculated metrics
        metricas_calculadas = []
        for metric_data in data.get('metricas_calculadas', []):
            metricas_calculadas.append(CalculatedMetric(
                nombre=metric_data['nombre'],
                formula=metric_data['formula'],
                descripcion=metric_data['descripcion']
            ))
        
        # Parse business relations
        relaciones_negocio = []
        for rel_data in data.get('relaciones_negocio', []):
            relaciones_negocio.append(BusinessRelation(
                concepto=rel_data['concepto'],
                descripcion=rel_data['descripcion']
            ))
        
        return TableMetadata(
            tabla=data['tabla'],
            descripcion=data['descripcion'],
            columnas=columnas,
            metricas_calculadas=metricas_calculadas,
            relaciones_negocio=relaciones_negocio,
            rangos_esperados=data.get('rangos_esperados', {}),
            analisis_recomendados=data.get('analisis_recomendados', [])
        )
    
    def get_column_description(self, table_name: str, column_name: str) -> Optional[str]:
        """Get description for a specific column"""
        metadata = self.load_table_metadata(table_name)
        if not metadata:
            return None
        
        for col in metadata.columnas:
            if col.nombre == column_name:
                return col.descripcion
        
        return None
    
    def get_calculated_metrics(self, table_name: str) -> List[CalculatedMetric]:
        """Get all calculated metrics for a table"""
        metadata = self.load_table_metadata(table_name)
        if not metadata:
            return []
        
        return metadata.metricas_calculadas
    
    def get_business_context(self, table_name: str) -> str:
        """Get business context summary for a table"""
        metadata = self.load_table_metadata(table_name)
        if not metadata:
            return ""
        
        context_parts = [f"Tabla: {metadata.tabla}"]
        context_parts.append(f"Descripción: {metadata.descripcion}")
        
        if metadata.relaciones_negocio:
            context_parts.append("\nRelaciones de Negocio:")
            for rel in metadata.relaciones_negocio:
                context_parts.append(f"- {rel.concepto}: {rel.descripcion}")
        
        if metadata.metricas_calculadas:
            context_parts.append("\nMétricas Calculadas:")
            for metric in metadata.metricas_calculadas:
                context_parts.append(f"- {metric.nombre}: {metric.descripcion} (Fórmula: {metric.formula})")
        
        if metadata.analisis_recomendados:
            context_parts.append("\nAnálisis Recomendados:")
            for analisis in metadata.analisis_recomendados:
                context_parts.append(f"- {analisis['tipo']}: {analisis['descripcion']}")
        
        return "\n".join(context_parts)
    
    def get_column_info(self, table_name: str) -> Dict[str, str]:
        """Get all column descriptions for a table"""
        metadata = self.load_table_metadata(table_name)
        if not metadata:
            return {}
        
        return {col.nombre: col.descripcion for col in metadata.columnas}
    
    def validate_data_ranges(self, table_name: str, df) -> Dict[str, List[str]]:
        """Validate data against expected ranges"""
        metadata = self.load_table_metadata(table_name)
        if not metadata or not metadata.rangos_esperados:
            return {}
        
        validation_results = {}
        
        for column, ranges in metadata.rangos_esperados.items():
            if column not in df.columns:
                continue
            
            errors = []
            col_data = df[column].dropna()
            
            if 'min' in ranges and col_data.min() < ranges['min']:
                errors.append(f"Valor mínimo ({col_data.min()}) está por debajo del rango esperado ({ranges['min']})")
            
            if 'max' in ranges and col_data.max() > ranges['max']:
                errors.append(f"Valor máximo ({col_data.max()}) está por encima del rango esperado ({ranges['max']})")
            
            if errors:
                validation_results[column] = errors
        
        return validation_results
    
    def get_analysis_suggestions(self, table_name: str) -> List[Dict[str, Any]]:
        """Get suggested analyses for a table"""
        metadata = self.load_table_metadata(table_name)
        if not metadata:
            return []
        
        return metadata.analisis_recomendados

# Global metadata service instance
metadata_service = MetadataService() 