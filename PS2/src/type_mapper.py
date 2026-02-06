"""
=============================================================================
MODULE 3: DATA TYPE MAPPER
=============================================================================
Purpose: Handle data type transformations between source and target
Features:
    - Type conversion rules
    - Transformation functions
    - Loss detection (e.g., precision loss)
    - Custom transformation support
=============================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
import re


class TransformationType(Enum):
    """Types of transformations"""
    DIRECT = "direct"           # No change needed
    IMPLICIT = "implicit"       # Automatic conversion (safe)
    EXPLICIT = "explicit"       # Requires explicit conversion
    LOSSY = "lossy"            # May lose data/precision
    CUSTOM = "custom"          # Requires custom function


@dataclass
class TypeTransformation:
    """Describes a type transformation"""
    source_type: str
    target_type: str
    transformation_type: TransformationType
    description: str
    sql_function: Optional[str] = None  # SQL conversion function
    python_function: Optional[Callable] = None
    potential_loss: bool = False
    warnings: List[str] = field(default_factory=list)


class DataTypeMapper:
    """
    Handles data type mappings and transformations
    """
    
    # Type normalization mapping
    TYPE_ALIASES = {
        # Integer types
        "INT": "INTEGER",
        "INT4": "INTEGER",
        "INT8": "BIGINT",
        "SMALLINT": "SMALLINT",
        "TINYINT": "TINYINT",
        "BIGINT": "BIGINT",
        "SERIAL": "INTEGER",
        "BIGSERIAL": "BIGINT",
        
        # Floating point
        "FLOAT": "FLOAT",
        "FLOAT4": "FLOAT",
        "FLOAT8": "DOUBLE",
        "DOUBLE": "DOUBLE",
        "DOUBLE PRECISION": "DOUBLE",
        "REAL": "REAL",
        "NUMERIC": "NUMERIC",
        "DECIMAL": "DECIMAL",
        
        # String types
        "VARCHAR": "VARCHAR",
        "CHARACTER VARYING": "VARCHAR",
        "CHAR": "CHAR",
        "CHARACTER": "CHAR",
        "TEXT": "TEXT",
        "STRING": "TEXT",
        "NVARCHAR": "NVARCHAR",
        "NCHAR": "NCHAR",
        "CLOB": "TEXT",
        
        # Binary
        "BLOB": "BLOB",
        "BINARY": "BLOB",
        "VARBINARY": "BLOB",
        "BYTEA": "BLOB",
        
        # Date/Time
        "DATE": "DATE",
        "TIME": "TIME",
        "DATETIME": "DATETIME",
        "TIMESTAMP": "TIMESTAMP",
        "TIMESTAMP WITHOUT TIME ZONE": "TIMESTAMP",
        "TIMESTAMP WITH TIME ZONE": "TIMESTAMPTZ",
        
        # Boolean
        "BOOLEAN": "BOOLEAN",
        "BOOL": "BOOLEAN",
        "BIT": "BOOLEAN",
        
        # JSON
        "JSON": "JSON",
        "JSONB": "JSON",
    }
    
    # Transformation rules: (source_normalized, target_normalized) -> TransformationType
    TRANSFORMATION_RULES = {
        # Integer conversions
        ("INTEGER", "INTEGER"): (TransformationType.DIRECT, "No conversion needed"),
        ("INTEGER", "BIGINT"): (TransformationType.IMPLICIT, "Safe upcast to larger integer"),
        ("BIGINT", "INTEGER"): (TransformationType.LOSSY, "May overflow if value > 2^31"),
        ("INTEGER", "FLOAT"): (TransformationType.IMPLICIT, "Safe conversion to float"),
        ("INTEGER", "VARCHAR"): (TransformationType.EXPLICIT, "Convert number to string"),
        ("INTEGER", "TEXT"): (TransformationType.EXPLICIT, "Convert number to string"),
        
        # Float conversions
        ("FLOAT", "FLOAT"): (TransformationType.DIRECT, "No conversion needed"),
        ("FLOAT", "DOUBLE"): (TransformationType.IMPLICIT, "Safe upcast to double"),
        ("DOUBLE", "FLOAT"): (TransformationType.LOSSY, "May lose precision"),
        ("FLOAT", "INTEGER"): (TransformationType.LOSSY, "Truncates decimal portion"),
        ("FLOAT", "VARCHAR"): (TransformationType.EXPLICIT, "Convert number to string"),
        
        # String conversions
        ("VARCHAR", "VARCHAR"): (TransformationType.DIRECT, "No conversion needed"),
        ("VARCHAR", "TEXT"): (TransformationType.IMPLICIT, "Safe conversion to unlimited text"),
        ("TEXT", "VARCHAR"): (TransformationType.LOSSY, "May truncate if too long"),
        ("CHAR", "VARCHAR"): (TransformationType.IMPLICIT, "Safe conversion"),
        ("VARCHAR", "INTEGER"): (TransformationType.EXPLICIT, "Parse string as integer"),
        ("VARCHAR", "FLOAT"): (TransformationType.EXPLICIT, "Parse string as float"),
        
        # Date conversions
        ("DATE", "DATE"): (TransformationType.DIRECT, "No conversion needed"),
        ("DATE", "DATETIME"): (TransformationType.IMPLICIT, "Add midnight time component"),
        ("DATE", "TIMESTAMP"): (TransformationType.IMPLICIT, "Add midnight time component"),
        ("DATETIME", "DATE"): (TransformationType.LOSSY, "Time component will be lost"),
        ("TIMESTAMP", "DATE"): (TransformationType.LOSSY, "Time component will be lost"),
        ("DATETIME", "TIMESTAMP"): (TransformationType.DIRECT, "Same precision"),
        ("VARCHAR", "DATE"): (TransformationType.EXPLICIT, "Parse string as date"),
        ("VARCHAR", "DATETIME"): (TransformationType.EXPLICIT, "Parse string as datetime"),
        
        # Boolean conversions
        ("BOOLEAN", "BOOLEAN"): (TransformationType.DIRECT, "No conversion needed"),
        ("BOOLEAN", "INTEGER"): (TransformationType.EXPLICIT, "Convert to 0/1"),
        ("INTEGER", "BOOLEAN"): (TransformationType.EXPLICIT, "Non-zero = true"),
        ("VARCHAR", "BOOLEAN"): (TransformationType.EXPLICIT, "Parse yes/no, true/false, 1/0"),
        
        # JSON
        ("JSON", "JSON"): (TransformationType.DIRECT, "No conversion needed"),
        ("JSON", "TEXT"): (TransformationType.IMPLICIT, "Serialize to string"),
        ("TEXT", "JSON"): (TransformationType.EXPLICIT, "Parse as JSON"),
    }
    
    def __init__(self):
        self.custom_transformations: Dict[tuple, TypeTransformation] = {}
    
    def normalize_type(self, data_type: str) -> str:
        """Normalize a data type to standard form"""
        # Remove size specifications
        base_type = re.sub(r'\([^)]*\)', '', data_type).strip().upper()
        return self.TYPE_ALIASES.get(base_type, base_type)
    
    def extract_size(self, data_type: str) -> Optional[int]:
        """Extract size from type like VARCHAR(255)"""
        match = re.search(r'\((\d+)\)', data_type)
        return int(match.group(1)) if match else None
    
    def get_transformation(self, source_type: str, target_type: str) -> TypeTransformation:
        """
        Get the transformation needed between two data types
        """
        # Normalize types
        src_normalized = self.normalize_type(source_type)
        tgt_normalized = self.normalize_type(target_type)
        
        # Check for custom transformation first
        if (src_normalized, tgt_normalized) in self.custom_transformations:
            return self.custom_transformations[(src_normalized, tgt_normalized)]
        
        # Check predefined rules
        if (src_normalized, tgt_normalized) in self.TRANSFORMATION_RULES:
            trans_type, description = self.TRANSFORMATION_RULES[(src_normalized, tgt_normalized)]
            
            transformation = TypeTransformation(
                source_type=source_type,
                target_type=target_type,
                transformation_type=trans_type,
                description=description,
                potential_loss=(trans_type == TransformationType.LOSSY)
            )
            
            # Add size-based warnings
            src_size = self.extract_size(source_type)
            tgt_size = self.extract_size(target_type)
            
            if src_size and tgt_size and src_size > tgt_size:
                transformation.warnings.append(
                    f"Source size ({src_size}) > target size ({tgt_size}). Data may be truncated."
                )
                transformation.potential_loss = True
            
            # Add SQL conversion functions
            transformation.sql_function = self._get_sql_function(
                src_normalized, tgt_normalized
            )
            
            return transformation
        
        # Types are same (after normalization)
        if src_normalized == tgt_normalized:
            return TypeTransformation(
                source_type=source_type,
                target_type=target_type,
                transformation_type=TransformationType.DIRECT,
                description="Types are equivalent"
            )
        
        # Unknown transformation
        return TypeTransformation(
            source_type=source_type,
            target_type=target_type,
            transformation_type=TransformationType.CUSTOM,
            description=f"Unknown conversion: {src_normalized} → {tgt_normalized}",
            warnings=["Manual review recommended"]
        )
    
    def _get_sql_function(self, source: str, target: str) -> Optional[str]:
        """Get SQL conversion function"""
        sql_functions = {
            ("INTEGER", "VARCHAR"): "CAST({column} AS VARCHAR)",
            ("FLOAT", "VARCHAR"): "CAST({column} AS VARCHAR)",
            ("VARCHAR", "INTEGER"): "CAST({column} AS INTEGER)",
            ("VARCHAR", "FLOAT"): "CAST({column} AS FLOAT)",
            ("VARCHAR", "DATE"): "CAST({column} AS DATE)",
            ("DATE", "VARCHAR"): "CAST({column} AS VARCHAR)",
            ("DATETIME", "DATE"): "CAST({column} AS DATE)",
            ("INTEGER", "BOOLEAN"): "CASE WHEN {column} != 0 THEN TRUE ELSE FALSE END",
            ("BOOLEAN", "INTEGER"): "CASE WHEN {column} THEN 1 ELSE 0 END",
        }
        return sql_functions.get((source, target))
    
    def register_custom_transformation(self, 
                                       source_type: str,
                                       target_type: str,
                                       transformation: TypeTransformation):
        """Register a custom transformation rule"""
        src_normalized = self.normalize_type(source_type)
        tgt_normalized = self.normalize_type(target_type)
        self.custom_transformations[(src_normalized, tgt_normalized)] = transformation
    
    def generate_migration_sql(self, 
                               column_name: str,
                               source_type: str,
                               target_type: str,
                               target_column: str = None) -> str:
        """Generate SQL for migrating a column"""
        target_column = target_column or column_name
        transformation = self.get_transformation(source_type, target_type)
        
        if transformation.sql_function:
            return transformation.sql_function.format(column=column_name)
        else:
            return column_name  # Direct copy


@dataclass
class MigrationPlan:
    """Complete plan for migrating a table"""
    source_table: str
    target_table: str
    column_mappings: List[Dict]  # List of {source, target, transformation}
    warnings: List[str] = field(default_factory=list)
    pre_migration_checks: List[str] = field(default_factory=list)
    post_migration_checks: List[str] = field(default_factory=list)
    
    def generate_select_sql(self) -> str:
        """Generate SELECT statement for migration"""
        select_parts = []
        for mapping in self.column_mappings:
            if mapping.get('sql_function'):
                select_parts.append(
                    f"{mapping['sql_function'].format(column=mapping['source'])} AS {mapping['target']}"
                )
            else:
                if mapping['source'] != mapping['target']:
                    select_parts.append(f"{mapping['source']} AS {mapping['target']}")
                else:
                    select_parts.append(mapping['source'])
        
        return f"SELECT\n  " + ",\n  ".join(select_parts) + f"\nFROM {self.source_table}"
    
    def generate_insert_sql(self) -> str:
        """Generate INSERT statement for migration"""
        target_columns = [m['target'] for m in self.column_mappings]
        
        return f"INSERT INTO {self.target_table} ({', '.join(target_columns)})\n{self.generate_select_sql()}"


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Data Type Mapper Module Loaded")
    
    mapper = DataTypeMapper()
    
    # Test conversions
    test_cases = [
        ("INTEGER", "BIGINT"),
        ("VARCHAR(100)", "VARCHAR(50)"),
        ("DATETIME", "DATE"),
        ("TEXT", "JSON"),
    ]
    
    print("\nTransformation examples:")
    for src, tgt in test_cases:
        trans = mapper.get_transformation(src, tgt)
        print(f"  {src} → {tgt}")
        print(f"    Type: {trans.transformation_type.value}")
        print(f"    Description: {trans.description}")
        if trans.warnings:
            print(f"    Warnings: {trans.warnings}")
        print()
