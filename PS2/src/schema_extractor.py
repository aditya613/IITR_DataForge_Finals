"""
=============================================================================
MODULE 1: SCHEMA EXTRACTOR
=============================================================================
Purpose: Extract complete schema information from source and target databases
Features:
    - Table names, column names, data types
    - Primary keys, foreign keys, constraints
    - Sample data for validation
    - Metadata (nullability, defaults, indexes)
=============================================================================
"""

import sqlite3
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import json


@dataclass
class ColumnInfo:
    """Represents a single column's metadata"""
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_ref: Optional[str] = None  # "table.column" format
    default_value: Optional[Any] = None
    max_length: Optional[int] = None
    sample_values: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "data_type": self.data_type,
            "is_nullable": self.is_nullable,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "foreign_key_ref": self.foreign_key_ref,
            "default_value": self.default_value,
            "max_length": self.max_length,
            "sample_values": self.sample_values[:5]  # Limit samples
        }


@dataclass
class TableInfo:
    """Represents a single table's metadata"""
    name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    row_count: int = 0
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: Dict[str, str] = field(default_factory=dict)  # col -> ref
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "columns": [col.to_dict() for col in self.columns],
            "row_count": self.row_count,
            "primary_keys": self.primary_keys,
            "foreign_keys": self.foreign_keys
        }


@dataclass
class DatabaseSchema:
    """Complete database schema representation"""
    db_name: str
    db_type: str  # "sqlite", "postgresql", "mysql"
    tables: List[TableInfo] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "db_name": self.db_name,
            "db_type": self.db_type,
            "tables": [table.to_dict() for table in self.tables]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def get_table(self, table_name: str) -> Optional[TableInfo]:
        """Get table by name"""
        for table in self.tables:
            if table.name.lower() == table_name.lower():
                return table
        return None


class SchemaExtractor:
    """
    Extract schema from various database types
    Currently supports: SQLite (expandable to PostgreSQL, MySQL)
    """
    
    def __init__(self, db_path: str, db_type: str = "sqlite"):
        self.db_path = db_path
        self.db_type = db_type
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        if self.db_type == "sqlite":
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        else:
            raise NotImplementedError(f"Database type {self.db_type} not yet supported")
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def extract_schema(self) -> DatabaseSchema:
        """Main method: Extract complete schema"""
        self.connect()
        try:
            db_name = Path(self.db_path).stem
            schema = DatabaseSchema(db_name=db_name, db_type=self.db_type)
            
            # Get all tables
            table_names = self._get_table_names()
            
            for table_name in table_names:
                table_info = self._extract_table_info(table_name)
                schema.tables.append(table_info)
            
            return schema
        finally:
            self.disconnect()
    
    def _get_table_names(self) -> List[str]:
        """Get all table names from database"""
        cursor = self.connection.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            return [row[0] for row in cursor.fetchall()]
        
        return []
    
    def _extract_table_info(self, table_name: str) -> TableInfo:
        """Extract complete information for a single table"""
        cursor = self.connection.cursor()
        
        table_info = TableInfo(name=table_name)
        
        # Get column info using PRAGMA
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_raw = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        fk_raw = cursor.fetchall()
        fk_map = {}
        for fk in fk_raw:
            fk_map[fk[3]] = f"{fk[2]}.{fk[4]}"  # from_col -> table.to_col
        
        # Process each column
        for col in columns_raw:
            col_name = col[1]
            col_type = col[2]
            is_nullable = col[3] == 0
            is_pk = col[5] == 1
            default = col[4]
            
            # Get sample values
            sample_values = self._get_sample_values(table_name, col_name)
            
            column_info = ColumnInfo(
                name=col_name,
                data_type=col_type,
                is_nullable=is_nullable,
                is_primary_key=is_pk,
                is_foreign_key=col_name in fk_map,
                foreign_key_ref=fk_map.get(col_name),
                default_value=default,
                sample_values=sample_values
            )
            
            table_info.columns.append(column_info)
            
            if is_pk:
                table_info.primary_keys.append(col_name)
        
        table_info.foreign_keys = fk_map
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        table_info.row_count = cursor.fetchone()[0]
        
        return table_info
    
    def _get_sample_values(self, table_name: str, column_name: str, limit: int = 5) -> List[Any]:
        """Get sample values from a column for understanding data patterns"""
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT DISTINCT "{column_name}" 
                FROM "{table_name}" 
                WHERE "{column_name}" IS NOT NULL 
                LIMIT {limit}
            """)
            return [row[0] for row in cursor.fetchall()]
        except:
            return []


def compare_schemas(source: DatabaseSchema, target: DatabaseSchema) -> Dict:
    """
    Compare two schemas and identify differences
    Returns: Dictionary with comparison results
    """
    comparison = {
        "source_tables": [t.name for t in source.tables],
        "target_tables": [t.name for t in target.tables],
        "common_tables": [],
        "source_only_tables": [],
        "target_only_tables": [],
        "table_comparisons": {}
    }
    
    source_table_names = set(t.name.lower() for t in source.tables)
    target_table_names = set(t.name.lower() for t in target.tables)
    
    comparison["common_tables"] = list(source_table_names & target_table_names)
    comparison["source_only_tables"] = list(source_table_names - target_table_names)
    comparison["target_only_tables"] = list(target_table_names - source_table_names)
    
    return comparison


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    # Demo usage
    print("Schema Extractor Module Loaded")
    print("Usage:")
    print("  extractor = SchemaExtractor('path/to/database.db')")
    print("  schema = extractor.extract_schema()")
    print("  print(schema.to_json())")
