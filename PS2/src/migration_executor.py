"""
=============================================================================
MODULE 7: MIGRATION EXECUTOR
=============================================================================
Purpose: Safely execute data migration with rollback support
Features:
    - Transaction-based migration
    - Batch processing
    - Failed record tracking
    - Rollback capability
    - Progress reporting
    - Data transformation during migration
=============================================================================
"""

import sqlite3
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import json
import traceback


class MigrationStatus(Enum):
    """Status of migration operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PARTIAL = "partial"


@dataclass
class FailedRecord:
    """Represents a record that failed to migrate"""
    source_table: str
    record_id: Any
    record_data: Dict
    error_message: str
    error_type: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "source_table": self.source_table,
            "record_id": str(self.record_id),
            "record_data": self.record_data,
            "error_message": self.error_message,
            "error_type": self.error_type,
            "timestamp": self.timestamp
        }


@dataclass
class TransformationRule:
    """Defines a transformation to apply during migration"""
    source_column: str
    target_column: str
    transformation_type: str  # "direct", "cast", "split", "merge", "custom"
    transformation_func: Optional[Callable] = None
    sql_expression: Optional[str] = None
    description: str = ""


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    source_table: str
    target_table: str
    status: MigrationStatus
    records_attempted: int = 0
    records_migrated: int = 0
    records_failed: int = 0
    failed_records: List[FailedRecord] = field(default_factory=list)
    start_time: str = ""
    end_time: str = ""
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    transformations_applied: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "source_table": self.source_table,
            "target_table": self.target_table,
            "status": self.status.value,
            "records_attempted": self.records_attempted,
            "records_migrated": self.records_migrated,
            "records_failed": self.records_failed,
            "failed_records": [fr.to_dict() for fr in self.failed_records[:100]],  # Limit
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": round(self.duration_seconds, 2),
            "error_message": self.error_message,
            "transformations_applied": self.transformations_applied,
            "success_rate": f"{(self.records_migrated/self.records_attempted*100):.1f}%" if self.records_attempted > 0 else "N/A"
        }


class MigrationExecutor:
    """
    Executes data migration between source and target databases
    with transaction support, error handling, and rollback capability.
    """
    
    def __init__(self, source_db_path: str, target_db_path: str):
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.source_conn = None
        self.target_conn = None
        self.results: List[MigrationResult] = []
        self.is_dry_run = False
        
    def connect(self):
        """Establish database connections"""
        self.source_conn = sqlite3.connect(self.source_db_path)
        self.source_conn.row_factory = sqlite3.Row
        self.target_conn = sqlite3.connect(self.target_db_path)
        
    def disconnect(self):
        """Close database connections"""
        if self.source_conn:
            self.source_conn.close()
        if self.target_conn:
            self.target_conn.close()
    
    def migrate_table(self,
                     source_table: str,
                     target_table: str,
                     column_mappings: List[Dict],
                     transformations: List[TransformationRule] = None,
                     batch_size: int = 1000,
                     dry_run: bool = False) -> MigrationResult:
        """
        Migrate data from source table to target table
        
        Args:
            source_table: Name of source table
            target_table: Name of target table
            column_mappings: List of {source_column, target_column, ...}
            transformations: Optional transformation rules
            batch_size: Number of records per batch
            dry_run: If True, don't actually insert data
            
        Returns:
            MigrationResult with details of the operation
        """
        self.is_dry_run = dry_run
        start_time = datetime.now()
        
        result = MigrationResult(
            source_table=source_table,
            target_table=target_table,
            status=MigrationStatus.IN_PROGRESS,
            start_time=start_time.isoformat()
        )
        
        try:
            self.connect()
            
            # Build column lists
            source_columns = [m.get('source_column', m.get('source', '').split('.')[-1]) 
                            for m in column_mappings]
            target_columns = [m.get('target_column', m.get('target', '').split('.')[-1]) 
                            for m in column_mappings]
            
            # Get total count
            cursor = self.source_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            total_records = cursor.fetchone()[0]
            result.records_attempted = total_records
            
            if dry_run:
                result.status = MigrationStatus.COMPLETED
                result.records_migrated = total_records
                result.end_time = datetime.now().isoformat()
                result.duration_seconds = (datetime.now() - start_time).total_seconds()
                return result
            
            # Process in batches
            offset = 0
            while offset < total_records:
                batch_result = self._migrate_batch(
                    source_table, target_table,
                    source_columns, target_columns,
                    transformations or [],
                    batch_size, offset,
                    result
                )
                offset += batch_size
            
            # Commit if successful
            if result.records_failed == 0:
                self.target_conn.commit()
                result.status = MigrationStatus.COMPLETED
            else:
                self.target_conn.commit()  # Commit successful records
                result.status = MigrationStatus.PARTIAL
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.error_message = str(e)
            if self.target_conn:
                self.target_conn.rollback()
            traceback.print_exc()
            
        finally:
            result.end_time = datetime.now().isoformat()
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.disconnect()
            self.results.append(result)
        
        return result
    
    def _migrate_batch(self,
                      source_table: str,
                      target_table: str,
                      source_columns: List[str],
                      target_columns: List[str],
                      transformations: List[TransformationRule],
                      batch_size: int,
                      offset: int,
                      result: MigrationResult) -> bool:
        """Migrate a single batch of records"""
        
        # Build transformation map
        transform_map = {t.source_column: t for t in transformations}
        
        # Fetch batch from source
        select_cols = ", ".join([f'"{c}"' for c in source_columns])
        query = f'SELECT rowid, {select_cols} FROM "{source_table}" LIMIT {batch_size} OFFSET {offset}'
        
        cursor = self.source_conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Process each row
        target_cursor = self.target_conn.cursor()
        
        for row in rows:
            try:
                rowid = row[0]
                values = []
                
                for i, src_col in enumerate(source_columns):
                    value = row[i + 1]  # +1 because rowid is first
                    
                    # Apply transformation if exists
                    if src_col in transform_map:
                        transform = transform_map[src_col]
                        value = self._apply_transformation(value, transform)
                        if transform.description and transform.description not in result.transformations_applied:
                            result.transformations_applied.append(transform.description)
                    
                    values.append(value)
                
                # Insert into target
                placeholders = ", ".join(["?" for _ in target_columns])
                target_cols = ", ".join([f'"{c}"' for c in target_columns])
                insert_sql = f'INSERT INTO "{target_table}" ({target_cols}) VALUES ({placeholders})'
                
                target_cursor.execute(insert_sql, values)
                result.records_migrated += 1
                
            except Exception as e:
                # Record failure but continue
                record_data = {source_columns[i]: row[i+1] for i in range(len(source_columns))}
                failed = FailedRecord(
                    source_table=source_table,
                    record_id=row[0],
                    record_data=record_data,
                    error_message=str(e),
                    error_type=type(e).__name__
                )
                result.failed_records.append(failed)
                result.records_failed += 1
        
        return True
    
    def _apply_transformation(self, value: Any, transform: TransformationRule) -> Any:
        """Apply a transformation rule to a value"""
        
        if transform.transformation_func:
            return transform.transformation_func(value)
        
        if transform.transformation_type == "direct":
            return value
        
        elif transform.transformation_type == "cast_int":
            try:
                return int(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        elif transform.transformation_type == "cast_float":
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        
        elif transform.transformation_type == "cast_str":
            return str(value) if value is not None else None
        
        elif transform.transformation_type == "uppercase":
            return str(value).upper() if value is not None else None
        
        elif transform.transformation_type == "lowercase":
            return str(value).lower() if value is not None else None
        
        elif transform.transformation_type == "trim":
            return str(value).strip() if value is not None else None
        
        elif transform.transformation_type == "null_to_default":
            return value if value is not None else transform.sql_expression
        
        return value
    
    def rollback_migration(self, target_table: str) -> bool:
        """
        Rollback a migration by clearing the target table
        WARNING: This deletes all data in the target table!
        """
        try:
            self.connect()
            cursor = self.target_conn.cursor()
            cursor.execute(f'DELETE FROM "{target_table}"')
            self.target_conn.commit()
            return True
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def generate_migration_report(self) -> Dict:
        """Generate a comprehensive migration report"""
        total_attempted = sum(r.records_attempted for r in self.results)
        total_migrated = sum(r.records_migrated for r in self.results)
        total_failed = sum(r.records_failed for r in self.results)
        
        return {
            "summary": {
                "total_tables": len(self.results),
                "total_records_attempted": total_attempted,
                "total_records_migrated": total_migrated,
                "total_records_failed": total_failed,
                "overall_success_rate": f"{(total_migrated/total_attempted*100):.1f}%" if total_attempted > 0 else "N/A",
                "status": "SUCCESS" if total_failed == 0 else "PARTIAL" if total_migrated > 0 else "FAILED"
            },
            "table_results": [r.to_dict() for r in self.results],
            "all_failed_records": [
                fr.to_dict() 
                for r in self.results 
                for fr in r.failed_records
            ][:500]  # Limit to 500 failed records
        }


# =============================================================================
# FIELD MAPPING TYPES (1:1, 1:Many, Many:1)
# =============================================================================

class MappingType(Enum):
    """Types of field mappings"""
    ONE_TO_ONE = "1:1"           # Single source → single target
    ONE_TO_MANY = "1:N"          # Single source → multiple targets (split)
    MANY_TO_ONE = "N:1"          # Multiple sources → single target (merge)
    TRANSFORMATION = "transform"  # Requires transformation


@dataclass
class AdvancedColumnMapping:
    """Advanced column mapping with support for complex relationships"""
    mapping_type: MappingType
    source_columns: List[str]  # Can be multiple for Many:1
    target_columns: List[str]  # Can be multiple for 1:Many
    source_table: str
    target_table: str
    transformation_logic: Optional[str] = None
    split_delimiter: Optional[str] = None  # For 1:Many splits
    merge_template: Optional[str] = None   # For Many:1 merges (e.g., "{first_name} {last_name}")
    confidence_score: float = 1.0
    explanation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "mapping_type": self.mapping_type.value,
            "source_columns": self.source_columns,
            "target_columns": self.target_columns,
            "source_table": self.source_table,
            "target_table": self.target_table,
            "transformation_logic": self.transformation_logic,
            "confidence_score": self.confidence_score,
            "explanation": self.explanation
        }


class AdvancedMigrationExecutor(MigrationExecutor):
    """
    Extended migration executor with support for:
    - 1:Many field splits
    - Many:1 field merges
    - Complex transformations
    """
    
    def detect_split_candidates(self, source_table: str, column: str) -> Optional[Dict]:
        """
        Detect if a column might need to be split
        (e.g., "John Smith" → first_name, last_name)
        """
        self.connect()
        try:
            cursor = self.source_conn.cursor()
            cursor.execute(f'SELECT "{column}" FROM "{source_table}" WHERE "{column}" IS NOT NULL LIMIT 100')
            samples = [row[0] for row in cursor.fetchall()]
            
            if not samples:
                return None
            
            # Check for common delimiters
            delimiters = [' ', ',', ';', '|', '-', '_']
            delimiter_counts = {}
            
            for delim in delimiters:
                count = sum(1 for s in samples if delim in str(s))
                if count > len(samples) * 0.5:  # More than 50% have this delimiter
                    delimiter_counts[delim] = count
            
            if delimiter_counts:
                best_delim = max(delimiter_counts, key=delimiter_counts.get)
                avg_parts = sum(len(str(s).split(best_delim)) for s in samples) / len(samples)
                
                return {
                    "column": column,
                    "recommended_delimiter": best_delim,
                    "average_parts": round(avg_parts, 1),
                    "sample": str(samples[0]).split(best_delim) if samples else []
                }
            
            return None
            
        finally:
            self.disconnect()
    
    def detect_merge_candidates(self, 
                               source_table: str, 
                               columns: List[str]) -> Optional[Dict]:
        """
        Detect if columns might be candidates for merging
        (e.g., first_name + last_name → full_name)
        """
        # Common merge patterns
        merge_patterns = [
            (["first_name", "last_name"], "full_name", "{0} {1}"),
            (["fname", "lname"], "name", "{0} {1}"),
            (["street", "city", "state", "zip"], "address", "{0}, {1}, {2} {3}"),
            (["addr", "city", "state", "zip"], "full_address", "{0}, {1}, {2} {3}"),
            (["day", "month", "year"], "date", "{2}-{1}-{0}"),
            (["area_code", "phone"], "phone_number", "({0}) {1}"),
        ]
        
        normalized_cols = [c.lower().replace("_", "") for c in columns]
        
        for pattern_cols, target, template in merge_patterns:
            pattern_normalized = [c.replace("_", "") for c in pattern_cols]
            if all(p in normalized_cols for p in pattern_normalized):
                return {
                    "source_columns": [columns[normalized_cols.index(p)] for p in pattern_normalized if p in normalized_cols],
                    "suggested_target": target,
                    "merge_template": template
                }
        
        return None
    
    def execute_advanced_migration(self,
                                  mappings: List[AdvancedColumnMapping],
                                  batch_size: int = 1000,
                                  dry_run: bool = False) -> List[MigrationResult]:
        """
        Execute migration with advanced mapping support
        """
        results = []
        
        # Group mappings by table pair
        table_pairs = {}
        for mapping in mappings:
            key = (mapping.source_table, mapping.target_table)
            if key not in table_pairs:
                table_pairs[key] = []
            table_pairs[key].append(mapping)
        
        for (source_table, target_table), table_mappings in table_pairs.items():
            result = self._execute_advanced_table_migration(
                source_table, target_table, table_mappings, batch_size, dry_run
            )
            results.append(result)
        
        return results
    
    def _execute_advanced_table_migration(self,
                                         source_table: str,
                                         target_table: str,
                                         mappings: List[AdvancedColumnMapping],
                                         batch_size: int,
                                         dry_run: bool) -> MigrationResult:
        """Execute migration for a single table with advanced mappings"""
        
        start_time = datetime.now()
        result = MigrationResult(
            source_table=source_table,
            target_table=target_table,
            status=MigrationStatus.IN_PROGRESS,
            start_time=start_time.isoformat()
        )
        
        try:
            self.connect()
            
            # Get all source columns needed
            all_source_cols = []
            for m in mappings:
                all_source_cols.extend(m.source_columns)
            all_source_cols = list(set(all_source_cols))
            
            # Get target columns
            all_target_cols = []
            for m in mappings:
                all_target_cols.extend(m.target_columns)
            
            # Get row count
            cursor = self.source_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            result.records_attempted = cursor.fetchone()[0]
            
            if dry_run:
                result.status = MigrationStatus.COMPLETED
                result.records_migrated = result.records_attempted
                result.end_time = datetime.now().isoformat()
                result.duration_seconds = (datetime.now() - start_time).total_seconds()
                return result
            
            # Fetch all source data
            select_cols = ", ".join([f'"{c}"' for c in all_source_cols])
            cursor.execute(f'SELECT rowid, {select_cols} FROM "{source_table}"')
            rows = cursor.fetchall()
            
            # Process each row
            target_cursor = self.target_conn.cursor()
            
            for row in rows:
                try:
                    rowid = row[0]
                    source_values = {all_source_cols[i]: row[i+1] for i in range(len(all_source_cols))}
                    
                    # Build target values based on mappings
                    target_values = {}
                    
                    for mapping in mappings:
                        if mapping.mapping_type == MappingType.ONE_TO_ONE:
                            # Simple 1:1 mapping
                            target_values[mapping.target_columns[0]] = source_values.get(mapping.source_columns[0])
                            
                        elif mapping.mapping_type == MappingType.MANY_TO_ONE:
                            # Merge multiple source columns
                            if mapping.merge_template:
                                values = [source_values.get(c, '') for c in mapping.source_columns]
                                merged = mapping.merge_template.format(*values)
                                target_values[mapping.target_columns[0]] = merged
                            else:
                                # Default: concatenate with space
                                values = [str(source_values.get(c, '')) for c in mapping.source_columns]
                                target_values[mapping.target_columns[0]] = ' '.join(values)
                                
                        elif mapping.mapping_type == MappingType.ONE_TO_MANY:
                            # Split single source column
                            source_val = str(source_values.get(mapping.source_columns[0], ''))
                            delim = mapping.split_delimiter or ' '
                            parts = source_val.split(delim)
                            
                            for i, target_col in enumerate(mapping.target_columns):
                                target_values[target_col] = parts[i] if i < len(parts) else None
                    
                    # Insert into target
                    cols = list(target_values.keys())
                    vals = [target_values[c] for c in cols]
                    
                    placeholders = ", ".join(["?" for _ in cols])
                    col_names = ", ".join([f'"{c}"' for c in cols])
                    insert_sql = f'INSERT INTO "{target_table}" ({col_names}) VALUES ({placeholders})'
                    
                    target_cursor.execute(insert_sql, vals)
                    result.records_migrated += 1
                    
                except Exception as e:
                    failed = FailedRecord(
                        source_table=source_table,
                        record_id=row[0],
                        record_data=source_values,
                        error_message=str(e),
                        error_type=type(e).__name__
                    )
                    result.failed_records.append(failed)
                    result.records_failed += 1
            
            self.target_conn.commit()
            result.status = MigrationStatus.COMPLETED if result.records_failed == 0 else MigrationStatus.PARTIAL
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.error_message = str(e)
            if self.target_conn:
                self.target_conn.rollback()
                
        finally:
            result.end_time = datetime.now().isoformat()
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            self.disconnect()
        
        return result


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Migration Executor Module Loaded")
    print("\nUsage:")
    print("  executor = MigrationExecutor('source.db', 'target.db')")
    print("  result = executor.migrate_table('old_users', 'new_users', mappings)")
    print("  print(result.to_dict())")
