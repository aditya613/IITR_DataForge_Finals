"""
=============================================================================
MAIN APPLICATION: DATA MIGRATION PLATFORM
=============================================================================
This is the main orchestrator that ties all modules together.
Run this to execute a complete migration analysis.
=============================================================================
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.schema_extractor import SchemaExtractor, DatabaseSchema, compare_schemas
from src.semantic_matcher import SemanticMatcher, ColumnMatch
from src.type_mapper import DataTypeMapper, MigrationPlan
from src.validation_engine import ValidationEngine, ValidationReport
from src.visualization import VisualizationEngine
from src.explainability import ExplainabilityEngine


class DataMigrationPlatform:
    """
    Main orchestrator for the Data Migration Platform
    
    Usage:
        platform = DataMigrationPlatform()
        platform.load_databases("source.db", "target.db")
        platform.analyze()
        platform.generate_report()
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        
        # Initialize all engines
        self.schema_extractor_source = None
        self.schema_extractor_target = None
        self.semantic_matcher = None
        self.type_mapper = DataTypeMapper()
        self.validation_engine = None
        self.visualization_engine = VisualizationEngine()
        self.explainability_engine = ExplainabilityEngine()
        
        # Data stores
        self.source_schema: Optional[DatabaseSchema] = None
        self.target_schema: Optional[DatabaseSchema] = None
        self.column_mappings: Dict[str, List[ColumnMatch]] = {}
        self.validation_report: Optional[ValidationReport] = None
        self.migration_plans: List[MigrationPlan] = []
        
        self._log("DataMigration Platform initialized")
    
    def _log(self, message: str):
        """Log message if verbose mode is on"""
        if self.verbose:
            print(f"[DataMigration] {message}")
    
    def load_databases(self, source_path: str, target_path: str):
        """
        Load source and target database schemas
        """
        self._log(f"Loading source database: {source_path}")
        self.schema_extractor_source = SchemaExtractor(source_path)
        self.source_schema = self.schema_extractor_source.extract_schema()
        self._log(f"  Found {len(self.source_schema.tables)} table(s)")
        
        self._log(f"Loading target database: {target_path}")
        self.schema_extractor_target = SchemaExtractor(target_path)
        self.target_schema = self.schema_extractor_target.extract_schema()
        self._log(f"  Found {len(self.target_schema.tables)} table(s)")
        
        # Initialize validation engine
        self.validation_engine = ValidationEngine(source_path, target_path)
        
        # Initialize semantic matcher
        self._log("Loading AI model for semantic matching...")
        self.semantic_matcher = SemanticMatcher()
    
    def analyze(self, threshold: float = 0.4) -> Dict:
        """
        Run complete analysis: schema comparison, column matching, validation
        
        Returns:
            Dictionary with analysis results
        """
        if not self.source_schema or not self.target_schema:
            raise ValueError("Databases not loaded. Call load_databases() first.")
        
        results = {
            "schema_comparison": {},
            "column_mappings": {},
            "validation": {},
            "recommendations": []
        }
        
        # 1. Schema comparison
        self._log("Comparing schemas...")
        results["schema_comparison"] = compare_schemas(
            self.source_schema, 
            self.target_schema
        )
        
        # 2. Column matching using AI
        self._log("Running AI-powered column matching...")
        self.column_mappings = self.semantic_matcher.match_schemas(
            self.source_schema,
            self.target_schema,
            threshold=threshold
        )
        
        # Convert to serializable format
        for key, matches in self.column_mappings.items():
            results["column_mappings"][key] = [m.to_dict() for m in matches]
            
            # Generate explanations
            for match in matches:
                src_table_name = match.source_table
                src_table = self.source_schema.get_table(src_table_name)
                if src_table:
                    src_col = next(
                        (c for c in src_table.columns if c.name == match.source_column), 
                        None
                    )
                    if src_col:
                        tgt_table = self.target_schema.get_table(match.target_table)
                        if tgt_table:
                            tgt_col = next(
                                (c for c in tgt_table.columns if c.name == match.target_column),
                                None
                            )
                            if tgt_col:
                                self.explainability_engine.explain_column_mapping(
                                    source_col=match.source_column,
                                    target_col=match.target_column,
                                    semantic_score=match.semantic_score,
                                    syntactic_score=match.syntactic_score,
                                    type_score=match.type_score,
                                    source_type=src_col.data_type,
                                    target_type=tgt_col.data_type,
                                    overall_score=match.overall_score
                                )
        
        self._log(f"  Found mappings for {len(self.column_mappings)} table pair(s)")
        
        # 3. Validation
        self._log("Running pre-migration validation...")
        validation_results = []
        for table in self.source_schema.tables:
            report = self.validation_engine.validate_pre_migration(table.name)
            validation_results.extend([r.to_dict() for r in report.results])
        
        results["validation"] = validation_results
        
        # 4. Generate recommendations
        self._log("Generating recommendations...")
        all_mappings = []
        for matches in self.column_mappings.values():
            all_mappings.extend([m.to_dict() for m in matches])
        
        recommendations = self.explainability_engine.generate_recommendations(
            all_mappings,
            validation_results
        )
        results["recommendations"] = [r.to_dict() for r in recommendations]
        
        self._log("Analysis complete!")
        return results
    
    def generate_visualizations(self, output_dir: str = "output"):
        """
        Generate all visualizations and save to output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Table-level Sankey diagram
        if self.source_schema and self.target_schema:
            self._log("Generating table-level Sankey diagram...")
            
            source_tables = [t.name for t in self.source_schema.tables]
            target_tables = [t.name for t in self.target_schema.tables]
            
            # Aggregate mappings by table
            table_mappings = []
            for key, matches in self.column_mappings.items():
                if matches:
                    avg_confidence = sum(m.overall_score for m in matches) / len(matches)
                    table_mappings.append({
                        "source_table": matches[0].source_table,
                        "target_table": matches[0].target_table,
                        "confidence": avg_confidence,
                        "column_count": len(matches)
                    })
            
            table_sankey = self.visualization_engine.create_sankey_diagram(
                source_tables,
                target_tables,
                table_mappings,
                title="Table-Level Migration Flow"
            )
            
            with open(os.path.join(output_dir, "table_sankey.html"), "w") as f:
                f.write(f"<!DOCTYPE html><html><head><title>Table Mappings</title></head><body>{table_sankey.html}</body></html>")
        
        # 2. Column-level Sankey diagrams (one per table pair)
        for key, matches in self.column_mappings.items():
            if matches:
                self._log(f"Generating column Sankey for {key}...")
                
                src_table_name = matches[0].source_table
                tgt_table_name = matches[0].target_table
                
                src_table = self.source_schema.get_table(src_table_name)
                tgt_table = self.target_schema.get_table(tgt_table_name)
                
                if src_table and tgt_table:
                    source_cols = [
                        {
                            "name": c.name,
                            "type": c.data_type,
                            "is_primary_key": c.is_primary_key,
                            "is_foreign_key": c.is_foreign_key
                        }
                        for c in src_table.columns
                    ]
                    
                    target_cols = [
                        {
                            "name": c.name,
                            "type": c.data_type,
                            "is_primary_key": c.is_primary_key,
                            "is_foreign_key": c.is_foreign_key
                        }
                        for c in tgt_table.columns
                    ]
                    
                    col_sankey = self.visualization_engine.create_column_sankey(
                        source_cols,
                        target_cols,
                        [m.to_dict() for m in matches],
                        source_table=src_table_name,
                        target_table=tgt_table_name
                    )
                    
                    filename = f"column_sankey_{src_table_name}_to_{tgt_table_name}.html"
                    with open(os.path.join(output_dir, filename), "w") as f:
                        f.write(f"<!DOCTYPE html><html><head><title>Column Mappings</title></head><body>{col_sankey.html}</body></html>")
        
        self._log(f"Visualizations saved to {output_dir}/")
    
    def generate_report(self, output_path: str = "migration_report.md") -> str:
        """
        Generate complete markdown report
        """
        report = self.explainability_engine.generate_report(format="markdown")
        
        with open(output_path, "w") as f:
            f.write(report)
        
        self._log(f"Report saved to {output_path}")
        return report
    
    def generate_migration_sql(self) -> str:
        """
        Generate SQL statements for migration
        """
        sql_statements = []
        
        for key, matches in self.column_mappings.items():
            if matches:
                src_table = matches[0].source_table
                tgt_table = matches[0].target_table
                
                # Build column list
                select_parts = []
                for match in matches:
                    src_col = match.source_column
                    tgt_col = match.target_column
                    
                    # Check if transformation needed
                    src_table_info = self.source_schema.get_table(src_table)
                    tgt_table_info = self.target_schema.get_table(tgt_table)
                    
                    if src_table_info and tgt_table_info:
                        src_col_info = next(
                            (c for c in src_table_info.columns if c.name == src_col), 
                            None
                        )
                        tgt_col_info = next(
                            (c for c in tgt_table_info.columns if c.name == tgt_col), 
                            None
                        )
                        
                        if src_col_info and tgt_col_info:
                            sql_expr = self.type_mapper.generate_migration_sql(
                                src_col,
                                src_col_info.data_type,
                                tgt_col_info.data_type,
                                tgt_col
                            )
                            if sql_expr != src_col:
                                select_parts.append(f"  {sql_expr} AS {tgt_col}")
                            else:
                                select_parts.append(f"  {src_col} AS {tgt_col}")
                
                if select_parts:
                    sql = f"-- Migration: {src_table} -> {tgt_table}\n"
                    sql += f"INSERT INTO {tgt_table} (\n"
                    sql += ",\n".join(f"  {m.target_column}" for m in matches)
                    sql += "\n)\nSELECT\n"
                    sql += ",\n".join(select_parts)
                    sql += f"\nFROM {src_table};\n"
                    sql_statements.append(sql)
        
        return "\n\n".join(sql_statements)
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the analysis
        """
        total_mappings = sum(len(m) for m in self.column_mappings.values())
        high_conf = sum(
            1 for matches in self.column_mappings.values()
            for m in matches if m.overall_score >= 0.85
        )
        
        return {
            "source_tables": len(self.source_schema.tables) if self.source_schema else 0,
            "target_tables": len(self.target_schema.tables) if self.target_schema else 0,
            "table_pairs_mapped": len(self.column_mappings),
            "total_column_mappings": total_mappings,
            "high_confidence_mappings": high_conf,
            "mapping_confidence_rate": f"{high_conf/total_mappings*100:.1f}%" if total_mappings > 0 else "N/A"
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================
def main():
    """
    Command-line interface
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI-Powered Data Migration Platform"
    )
    parser.add_argument("source", help="Path to source database")
    parser.add_argument("target", help="Path to target database")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--threshold", "-t", type=float, default=0.4, 
                       help="Matching confidence threshold")
    
    args = parser.parse_args()
    
    # Run analysis
    platform = DataMigrationPlatform()
    platform.load_databases(args.source, args.target)
    
    results = platform.analyze(threshold=args.threshold)
    
    # Generate outputs
    platform.generate_visualizations(args.output)
    platform.generate_report(os.path.join(args.output, "report.md"))
    
    # Save SQL
    sql = platform.generate_migration_sql()
    with open(os.path.join(args.output, "migration.sql"), "w") as f:
        f.write(sql)
    
    # Print summary
    print("\n" + "=" * 50)
    print("MIGRATION ANALYSIS SUMMARY")
    print("=" * 50)
    for key, value in platform.get_summary().items():
        print(f"  {key}: {value}")
    print("=" * 50)


if __name__ == "__main__":
    main()
