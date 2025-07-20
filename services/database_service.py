"""
Database service for OkuoAgent
Handles database connections and operations
"""

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Tuple
import logging
from config import config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations."""
    
    def __init__(self):
        self.engine = None
        self.connection = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to the database."""
        try:
            connection_string = config.get_database_connection_string()
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            self.is_connected = True
            logger.info(f"Successfully connected to {config.DATABASE_TYPE} database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()
        self.is_connected = False
        logger.info("Disconnected from database")
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            if not self.is_connected:
                return self.connect()
            
            # Simple query to test connection
            result = self.connection.execute(text("SELECT 1"))
            result.fetchone()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            self.is_connected = False
            return False
    
    def get_tables(self) -> List[str]:
        """Get list of available tables."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return []
            
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict:
        """Get information about a specific table."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return {}
            
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            # Get row count
            result = self.connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.fetchone()[0]
            
            return {
                "name": table_name,
                "columns": [col["name"] for col in columns],
                "column_types": {col["name"]: str(col["type"]) for col in columns},
                "row_count": row_count
            }
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {str(e)}")
            return {}
    
    def load_table_as_dataframe(self, table_name: str, limit: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Load a table as a pandas DataFrame."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return None
            
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql(query, self.connection)
            logger.info(f"Loaded table {table_name} with {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Failed to load table {table_name}: {str(e)}")
            return None
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute a custom SQL query and return results as DataFrame."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return None
            
            df = pd.read_sql(query, self.connection)
            logger.info(f"Executed query with {len(df)} rows returned")
            return df
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            return None
    
    def get_database_info(self) -> Dict:
        """Get general database information."""
        try:
            if not self.is_connected:
                if not self.connect():
                    return {}
            
            tables = self.get_tables()
            table_info = {}
            
            for table in tables:
                table_info[table] = self.get_table_info(table)
            
            return {
                "database_type": config.DATABASE_TYPE,
                "database_name": config.DATABASE_NAME,
                "host": config.DATABASE_HOST,
                "port": config.DATABASE_PORT,
                "tables": tables,
                "table_details": table_info
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {str(e)}")
            return {}

# Global database service instance
db_service = DatabaseService() 