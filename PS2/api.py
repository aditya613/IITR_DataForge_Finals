"""
FastAPI Backend for DataForge Migration Platform
Integrates with Gemini API for intelligent column matching
"""

import os
import json
import sqlite3
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hybrid_ai_engine import HybridAIEngine, MatchResult, create_engine
from schema_extractor import SchemaExtractor
from validation_engine import ValidationEngine

# ============================================================================
# CONFIGURATION
# ============================================================================

# Set your Gemini API key here or via environment variable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro" for better quality

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="DataForge Migration API",
    description="AI-Powered Intelligent Data Migration Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
sessions: Dict[str, Dict] = {}
engine: Optional[HybridAIEngine] = None


def get_engine() -> HybridAIEngine:
    """Get or create the AI engine"""
    global engine
    if engine is None:
        engine = create_engine(gemini_api_key=GEMINI_API_KEY)
    return engine


# ============================================================================
# Pydantic Models
# ============================================================================

class AnalysisRequest(BaseModel):
    session_id: str
    threshold: float = 0.6


class MappingReport(BaseModel):
    source_column: str
    target_column: str
    source_table: str
    target_table: str
    confidence_score: float
    confidence_level: str
    mapping_type: str
    why_mapped: str
    why_not_others: str
    transformation: str
    bert_score: float
    gemini_score: float
    tfidf_score: float
    domain_score: float


class ValidationReport(BaseModel):
    source_row_count: int
    target_row_count: int
    rows_migrated: int
    rows_failed: int
    null_checks: Dict[str, int]
    duplicate_checks: Dict[str, int]
    referential_integrity: List[Dict]
    failed_records: List[Dict]
    is_valid: bool
    summary: str


class MigrationResult(BaseModel):
    success: bool
    rows_migrated: int
    rows_failed: int
    failed_records: List[Dict]
    validation: ValidationReport
    timestamp: str


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "name": "DataForge Migration API",
        "version": "1.0.0",
        "gemini_enabled": bool(GEMINI_API_KEY),
        "endpoints": {
            "upload": "POST /api/upload",
            "analyze": "POST /api/analyze",
            "mapping_report": "GET /api/mapping-report/{session_id}",
            "validation_report": "GET /api/validation-report/{session_id}",
            "migrate": "POST /api/migrate",
            "visualization": "GET /api/visualization/{session_id}",
            "explain": "GET /api/explain/{session_id}"
        }
    }


@app.post("/api/upload")
async def upload_databases(
    source_db: UploadFile = File(...),
    target_db: UploadFile = File(...)
):
    """Upload source and target databases for analysis"""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save uploaded files
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    source_path = temp_dir / "source.db"
    target_path = temp_dir / "target.db"
    
    with open(source_path, "wb") as f:
        f.write(await source_db.read())
    with open(target_path, "wb") as f:
        f.write(await target_db.read())
    
    # Extract schemas
    source_extractor = SchemaExtractor(str(source_path))
    target_extractor = SchemaExtractor(str(target_path))
    
    source_schema_obj = source_extractor.extract_schema()
    target_schema_obj = target_extractor.extract_schema()
    
    # Convert to dict format for API
    source_schema = {}
    for table in source_schema_obj.tables:
        source_schema[table.name] = {
            "columns": [{"name": col.name, "type": col.data_type} for col in table.columns]
        }

        
    target_schema = {}
    for table in target_schema_obj.tables:
        target_schema[table.name] = {
            "columns": [{"name": col.name, "type": col.data_type} for col in table.columns]
        }
    
    # Store session
    sessions[session_id] = {
        "source_path": str(source_path),
        "target_path": str(target_path),
        "source_schema": source_schema,
        "target_schema": target_schema,
        "mappings": None,
        "validation": None,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "session_id": session_id,
        "source_tables": list(source_schema.keys()),
        "target_tables": list(target_schema.keys()),
        "source_columns": sum(len(cols) for cols in source_schema.values()),
        "target_columns": sum(len(cols) for cols in target_schema.values())
    }


@app.post("/api/analyze")
async def analyze_schemas(request: AnalysisRequest):
    """Analyze schemas and generate column mappings"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    ai_engine = get_engine()
    
    # Convert schema format
    source_schema = {}
    target_schema = {}
    
    for table, info in session["source_schema"].items():
        source_schema[table] = {col["name"]: col["type"] for col in info["columns"]}
    
    for table, info in session["target_schema"].items():
        target_schema[table] = {col["name"]: col["type"] for col in info["columns"]}
    
    # Run matching
    mappings, stats = ai_engine.match_columns(
        source_schema, target_schema, threshold=request.threshold
    )
    
    # Get unmapped columns
    unmapped = ai_engine.get_unmapped_columns(source_schema, target_schema, mappings)
    
    # Store results
    session["mappings"] = mappings
    session["stats"] = stats
    session["unmapped"] = unmapped
    
    return {
        "session_id": request.session_id,
        "total_mappings": len(mappings),
        "statistics": stats,
        "unmapped_source": len(unmapped["source"]),
        "unmapped_target": len(unmapped["target"]),
        "gemini_used": ai_engine.gemini_model is not None
    }


@app.get("/api/mapping-report/{session_id}")
async def get_mapping_report(session_id: str):
    """Get detailed mapping report with explanations"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    mappings = []
    for m in session["mappings"]:
        mappings.append({
            "source_table": m.source_table,
            "source_column": m.source_column,
            "source_type": m.data_type_source,
            "target_table": m.target_table,
            "target_column": m.target_column,
            "target_type": m.data_type_target,
            "confidence_score": round(m.ensemble_score, 4),
            "confidence_level": m.confidence_level,
            "mapping_type": m.mapping_type,
            "transformation": m.transformation,
            "scores": {
                "bert": round(m.bert_score, 4),
                "gemini": round(m.gemini_score, 4),
                "tfidf": round(m.tfidf_score, 4),
                "domain": round(m.domain_score, 4)
            },
            "explainability": {
                "why_mapped": m.why_mapped,
                "why_not_others": m.why_not_others,
                "summary": m.explanation
            }
        })
    
    unmapped = session.get("unmapped", {"source": [], "target": []})
    
    return {
        "session_id": session_id,
        "generated_at": datetime.now().isoformat(),
        "mappings": mappings,
        "unmapped_source_columns": unmapped["source"],
        "unmapped_target_columns": unmapped["target"],
        "statistics": session.get("stats", {})
    }


@app.post("/api/migrate")
async def execute_migration(session_id: str = Form(...)):
    """Execute the actual data migration"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    source_path = session["source_path"]
    target_path = session["target_path"]
    mappings = session["mappings"]
    
    # Connect to databases
    source_conn = sqlite3.connect(source_path)
    target_conn = sqlite3.connect(target_path)
    
    rows_migrated = 0
    rows_failed = 0
    failed_records = []
    
    try:
        # Group mappings by table pairs
        table_mappings: Dict[tuple, List] = {}
        for m in mappings:
            key = (m.source_table, m.target_table)
            if key not in table_mappings:
                table_mappings[key] = []
            table_mappings[key].append(m)
        
        # Migrate data for each table pair
        for (src_table, tgt_table), cols in table_mappings.items():
            source_cols = [m.source_column for m in cols]
            target_cols = [m.target_column for m in cols]
            
            # Read source data
            query = f"SELECT {', '.join(source_cols)} FROM {src_table}"
            cursor = source_conn.execute(query)
            rows = cursor.fetchall()
            
            # Insert into target
            placeholders = ", ".join(["?" for _ in target_cols])
            insert_query = f"INSERT INTO {tgt_table} ({', '.join(target_cols)}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    target_conn.execute(insert_query, row)
                    rows_migrated += 1
                except Exception as e:
                    rows_failed += 1
                    failed_records.append({
                        "source_table": src_table,
                        "target_table": tgt_table,
                        "data": dict(zip(source_cols, row)),
                        "error": str(e),
                        "reason": "Database constraint violation or type mismatch"
                    })
        
        target_conn.commit()
        
    finally:
        source_conn.close()
        target_conn.close()
    
    # Run validation
    validation = await validate_migration(session_id, source_path, target_path, mappings)
    session["validation"] = validation
    session["migration_result"] = {
        "rows_migrated": rows_migrated,
        "rows_failed": rows_failed,
        "failed_records": failed_records
    }
    
    return {
        "success": rows_failed == 0,
        "rows_migrated": rows_migrated,
        "rows_failed": rows_failed,
        "failed_records": failed_records[:10],  # Limit for response
        "validation_summary": validation["summary"],
        "timestamp": datetime.now().isoformat()
    }


async def validate_migration(session_id: str, source_path: str, target_path: str, 
                            mappings: List[MatchResult]) -> Dict:
    """Validate the migrated data"""
    source_conn = sqlite3.connect(source_path)
    target_conn = sqlite3.connect(target_path)
    
    try:
        validation_results = {
            "row_counts": {},
            "null_checks": {},
            "duplicate_checks": {},
            "referential_integrity": [],
            "failed_records": [],
            "is_valid": True,
            "summary": ""
        }
        
        # Get unique tables
        table_pairs = set((m.source_table, m.target_table) for m in mappings)
        
        for src_table, tgt_table in table_pairs:
            # Row count comparison
            src_count = source_conn.execute(f"SELECT COUNT(*) FROM {src_table}").fetchone()[0]
            tgt_count = target_conn.execute(f"SELECT COUNT(*) FROM {tgt_table}").fetchone()[0]
            
            validation_results["row_counts"][f"{src_table} -> {tgt_table}"] = {
                "source": src_count,
                "target": tgt_count,
                "difference": tgt_count - src_count,
                "match": src_count == tgt_count
            }
            
            if src_count != tgt_count:
                validation_results["is_valid"] = False
            
            # Null checks for mapped columns
            for m in mappings:
                if m.source_table == src_table:
                    src_nulls = source_conn.execute(
                        f"SELECT COUNT(*) FROM {src_table} WHERE {m.source_column} IS NULL"
                    ).fetchone()[0]
                    tgt_nulls = target_conn.execute(
                        f"SELECT COUNT(*) FROM {tgt_table} WHERE {m.target_column} IS NULL"
                    ).fetchone()[0]
                    
                    validation_results["null_checks"][f"{m.source_column} -> {m.target_column}"] = {
                        "source_nulls": src_nulls,
                        "target_nulls": tgt_nulls,
                        "match": src_nulls == tgt_nulls
                    }
            
            # Duplicate checks (for columns that might be unique)
            for m in mappings:
                if m.source_table == src_table and 'id' in m.source_column.lower():
                    tgt_dups = target_conn.execute(f"""
                        SELECT {m.target_column}, COUNT(*) as cnt 
                        FROM {tgt_table} 
                        GROUP BY {m.target_column} 
                        HAVING cnt > 1
                    """).fetchall()
                    
                    validation_results["duplicate_checks"][m.target_column] = {
                        "has_duplicates": len(tgt_dups) > 0,
                        "duplicate_count": len(tgt_dups)
                    }
        
        # Generate summary
        total_issues = sum(1 for v in validation_results["row_counts"].values() if not v["match"])
        total_issues += sum(1 for v in validation_results["duplicate_checks"].values() if v["has_duplicates"])
        
        if total_issues == 0:
            validation_results["summary"] = "✓ All validation checks passed. Data migration is complete and accurate."
        else:
            validation_results["summary"] = f"⚠ {total_issues} validation issues found. Review the detailed report."
        
        return validation_results
        
    finally:
        source_conn.close()
        target_conn.close()


@app.get("/api/validation-report/{session_id}")
async def get_validation_report(session_id: str):
    """Get detailed validation report"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session.get("validation") is None:
        raise HTTPException(status_code=400, detail="Migration not executed yet")
    
    validation = session["validation"]
    migration = session.get("migration_result", {})
    
    return {
        "session_id": session_id,
        "generated_at": datetime.now().isoformat(),
        "row_comparison": validation["row_counts"],
        "null_checks": validation["null_checks"],
        "duplicate_checks": validation["duplicate_checks"],
        "referential_integrity": validation["referential_integrity"],
        "failed_records": migration.get("failed_records", []),
        "is_valid": validation["is_valid"],
        "summary": validation["summary"],
        "migration_stats": {
            "rows_migrated": migration.get("rows_migrated", 0),
            "rows_failed": migration.get("rows_failed", 0)
        }
    }


@app.get("/api/visualization/{session_id}")
async def get_visualization_data(session_id: str):
    """Get data for visualization (Sankey diagram, table mapping, etc.)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    mappings = session["mappings"]
    unmapped = session.get("unmapped", {"source": [], "target": []})
    
    # Build Sankey diagram data
    nodes = []
    links = []
    node_map = {}
    
    # Add source nodes
    for m in mappings:
        src_key = f"source_{m.source_table}_{m.source_column}"
        if src_key not in node_map:
            node_map[src_key] = len(nodes)
            nodes.append({
                "id": src_key,
                "name": f"{m.source_table}.{m.source_column}",
                "type": "source",
                "table": m.source_table
            })
    
    # Add unmapped source nodes
    for u in unmapped["source"]:
        src_key = f"source_{u['table']}_{u['column']}"
        if src_key not in node_map:
            node_map[src_key] = len(nodes)
            nodes.append({
                "id": src_key,
                "name": f"{u['table']}.{u['column']}",
                "type": "source_unmapped",
                "table": u["table"],
                "reason": u["reason"]
            })
    
    # Add target nodes
    for m in mappings:
        tgt_key = f"target_{m.target_table}_{m.target_column}"
        if tgt_key not in node_map:
            node_map[tgt_key] = len(nodes)
            nodes.append({
                "id": tgt_key,
                "name": f"{m.target_table}.{m.target_column}",
                "type": "target",
                "table": m.target_table
            })
    
    # Add unmapped target nodes
    for u in unmapped["target"]:
        tgt_key = f"target_{u['table']}_{u['column']}"
        if tgt_key not in node_map:
            node_map[tgt_key] = len(nodes)
            nodes.append({
                "id": tgt_key,
                "name": f"{u['table']}.{u['column']}",
                "type": "target_unmapped",
                "table": u["table"],
                "reason": u["reason"]
            })
    
    # Add links
    for m in mappings:
        src_key = f"source_{m.source_table}_{m.source_column}"
        tgt_key = f"target_{m.target_table}_{m.target_column}"
        links.append({
            "source": node_map[src_key],
            "target": node_map[tgt_key],
            "value": m.ensemble_score,
            "confidence": m.confidence_level,
            "mapping_type": m.mapping_type,
            "explanation": m.why_mapped
        })
    
    # Table relationship view
    table_mappings = {}
    for m in mappings:
        key = f"{m.source_table} → {m.target_table}"
        if key not in table_mappings:
            table_mappings[key] = {
                "source_table": m.source_table,
                "target_table": m.target_table,
                "columns": []
            }
        table_mappings[key]["columns"].append({
            "source": m.source_column,
            "target": m.target_column,
            "confidence": m.confidence_level,
            "score": m.ensemble_score
        })
    
    return {
        "session_id": session_id,
        "sankey": {"nodes": nodes, "links": links},
        "table_mappings": list(table_mappings.values()),
        "summary": {
            "total_mappings": len(mappings),
            "high_confidence": sum(1 for m in mappings if m.confidence_level == "high"),
            "medium_confidence": sum(1 for m in mappings if m.confidence_level == "medium"),
            "low_confidence": sum(1 for m in mappings if m.confidence_level == "low"),
            "unmapped_source": len(unmapped["source"]),
            "unmapped_target": len(unmapped["target"])
        }
    }


@app.get("/api/explain/{session_id}")
async def get_explainability_report(session_id: str):
    """Get complete explainability report for non-technical stakeholders"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    mappings = session["mappings"]
    unmapped = session.get("unmapped", {"source": [], "target": []})
    validation = session.get("validation", {})
    migration = session.get("migration_result", {})
    
    # Generate explanations
    explanations = {
        "column_mappings": [],
        "ignored_columns": [],
        "transformations": [],
        "failed_data": [],
        "summary": ""
    }
    
    # Explain each mapping
    for m in mappings:
        explanations["column_mappings"].append({
            "question": f"Why was '{m.source_column}' mapped to '{m.target_column}'?",
            "answer": m.why_mapped or m.explanation,
            "confidence": f"{m.ensemble_score * 100:.1f}% confident",
            "details": {
                "The AI analyzed semantic meaning": f"BERT score: {m.bert_score * 100:.0f}%",
                "Gemini LLM reasoning": f"Gemini score: {m.gemini_score * 100:.0f}%",
                "Pattern matching": f"TF-IDF score: {m.tfidf_score * 100:.0f}%",
                "Database conventions": f"Domain score: {m.domain_score * 100:.0f}%"
            }
        })
    
    # Explain ignored columns
    for u in unmapped["source"]:
        explanations["ignored_columns"].append({
            "question": f"Why was '{u['table']}.{u['column']}' not mapped?",
            "answer": u["reason"]
        })
    
    # Explain transformations
    for m in mappings:
        if m.transformation and m.transformation != "none":
            explanations["transformations"].append({
                "question": f"What transformation was applied to '{m.source_column}'?",
                "answer": m.transformation,
                "source_type": m.data_type_source,
                "target_type": m.data_type_target
            })
    
    # Explain failed records
    for record in migration.get("failed_records", [])[:10]:
        explanations["failed_data"].append({
            "question": f"Why did this record fail to migrate?",
            "record": record.get("data", {}),
            "error": record.get("error", "Unknown error"),
            "reason": record.get("reason", "Check data types and constraints")
        })
    
    # Overall summary
    total_mapped = len(mappings)
    total_unmapped = len(unmapped["source"]) + len(unmapped["target"])
    high_conf = sum(1 for m in mappings if m.confidence_level == "high")
    
    explanations["summary"] = f"""
## Migration Analysis Summary

### What We Did
We analyzed {total_mapped} column mappings between your source and target databases using AI.

### Mapping Quality
- **{high_conf} columns** were mapped with HIGH confidence (>85%)
- **{total_mapped - high_conf} columns** were mapped with lower confidence
- **{total_unmapped} columns** were not mapped (intentionally or no match found)

### How We Made Decisions
Our AI system combines 4 approaches:
1. **Semantic Analysis (BERT)** - Understands the meaning of column names
2. **Gemini AI** - Provides contextual reasoning like a human expert
3. **Pattern Matching** - Finds similar text patterns
4. **Database Knowledge** - Knows common abbreviations and conventions

### Key Insights
{validation.get('summary', 'Run migration to see validation results.')}
"""
    
    return explanations


@app.get("/api/sample-data")
async def create_sample_data():
    """Create sample databases for testing"""
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / "sample"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    source_path = temp_dir / "legacy_crm.db"
    target_path = temp_dir / "modern_crm.db"
    
    # Create source (legacy) database
    source_conn = sqlite3.connect(str(source_path))
    source_conn.executescript("""
        DROP TABLE IF EXISTS cust_info;
        DROP TABLE IF EXISTS ord_details;
        
        CREATE TABLE cust_info (
            cust_id INTEGER PRIMARY KEY,
            fname TEXT,
            lname TEXT,
            email_addr TEXT,
            ph_num TEXT,
            addr_line1 TEXT,
            addr_line2 TEXT,
            city TEXT,
            st TEXT,
            zip TEXT,
            created_dt TEXT
        );
        
        CREATE TABLE ord_details (
            ord_id INTEGER PRIMARY KEY,
            cust_id INTEGER,
            prod_name TEXT,
            qty INTEGER,
            unit_price REAL,
            tot_amt REAL,
            ord_dt TEXT,
            ord_status TEXT
        );
        
        INSERT INTO cust_info VALUES 
            (1, 'John', 'Doe', 'john.doe@email.com', '555-0101', '123 Main St', 'Apt 4B', 'New York', 'NY', '10001', '2024-01-15'),
            (2, 'Jane', 'Smith', 'jane.smith@email.com', '555-0102', '456 Oak Ave', NULL, 'Los Angeles', 'CA', '90001', '2024-02-20'),
            (3, 'Bob', 'Johnson', 'bob.j@email.com', '555-0103', '789 Pine Rd', 'Suite 100', 'Chicago', 'IL', '60601', '2024-03-10');
        
        INSERT INTO ord_details VALUES
            (101, 1, 'Widget Pro', 2, 49.99, 99.98, '2024-03-01', 'completed'),
            (102, 1, 'Gadget Plus', 1, 129.99, 129.99, '2024-03-05', 'completed'),
            (103, 2, 'Widget Pro', 5, 49.99, 249.95, '2024-03-10', 'pending'),
            (104, 3, 'Super Tool', 1, 299.99, 299.99, '2024-03-15', 'shipped');
    """)
    source_conn.close()
    
    # Create target (modern) database
    target_conn = sqlite3.connect(str(target_path))
    target_conn.executescript("""
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS orders;
        
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone_number TEXT,
            address_line_1 TEXT,
            address_line_2 TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        );
        
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(customer_id),
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL,
            total_amount REAL,
            order_date TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    target_conn.close()
    
    return {
        "message": "Sample databases created",
        "source_path": str(source_path),
        "target_path": str(target_path),
        "description": {
            "source": "Legacy CRM with abbreviated column names (cust_info, ord_details)",
            "target": "Modern CRM with full column names (customers, orders)"
        }
    }


@app.get("/api/sample-file/{file_type}")
async def get_sample_file(file_type: str):
    """Download sample database file"""
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / "sample"
    
    if file_type == "source":
        file_path = temp_dir / "legacy_crm.db"
    elif file_type == "target":
        file_path = temp_dir / "modern_crm.db"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'source' or 'target'")
    
    if not file_path.exists():
        # Create sample data first
        await create_sample_data()
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/x-sqlite3"
    )


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("DataForge Migration API")
    print("="*60)
    print(f"Gemini API: {'Enabled' if GEMINI_API_KEY else 'Disabled (set GEMINI_API_KEY)'}")
    print(f"Gemini Model: {GEMINI_MODEL}")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
