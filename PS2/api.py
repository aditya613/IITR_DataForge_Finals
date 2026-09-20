import os
import json
import sqlite3
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hybrid_ai_engine import HybridAIEngine, MatchResult, create_engine
from schema_extractor import SchemaExtractor
from validation_engine import ValidationEngine

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")


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

sessions: Dict[str, Dict] = {}
engine: Optional[HybridAIEngine] = None
migration_status: Dict[str, Dict] = {}
active_websockets: Dict[str, List[WebSocket]] = {}


def get_engine() -> HybridAIEngine:
    global engine
    if engine is None:
        engine = create_engine(groq_api_key=GROQ_API_KEY)
    return engine


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
    llm_score: float
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


@app.get("/")
async def root():
    return {
        "name": "DataForge Migration API",
        "version": "1.0.0",
        "llm_enabled": bool(GROQ_API_KEY),
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
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / session_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    source_path = temp_dir / "source.db"
    target_path = temp_dir / "target.db"
    
    with open(source_path, "wb") as f:
        f.write(await source_db.read())
    with open(target_path, "wb") as f:
        f.write(await target_db.read())
    source_extractor = SchemaExtractor(str(source_path))
    target_extractor = SchemaExtractor(str(target_path))
    
    source_schema_obj = source_extractor.extract_schema()
    target_schema_obj = target_extractor.extract_schema()
    source_schema = {}
    for table in source_schema_obj.tables:
        source_schema[table.name] = {
            "columns": [{
                "name": col.name, 
                "type": col.data_type,
                "samples": col.sample_values
            } for col in table.columns]
        }
    target_schema = {}
    for table in target_schema_obj.tables:
        target_schema[table.name] = {
            "columns": [{
                "name": col.name, 
                "type": col.data_type,
                "samples": col.sample_values
            } for col in table.columns]
        }
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
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    ai_engine = get_engine()
    source_schema = {}
    target_schema = {}
    
    for table, info in session["source_schema"].items():
        source_schema[table] = {
            col["name"]: {
                "type": col["type"],
                "samples": col.get("samples", [])
            } for col in info["columns"]
        }
    
    for table, info in session["target_schema"].items():
        target_schema[table] = {
            col["name"]: {
                "type": col["type"],
                "samples": col.get("samples", [])
            } for col in info["columns"]
        }
    print(f"Source schema: {source_schema}")
    print(f"Target schema: {target_schema}")
    print(f"Threshold: {request.threshold}")
    mappings, stats = ai_engine.match_columns(
        source_schema, target_schema, threshold=request.threshold
    )
    
    print(f"Mappings found: {len(mappings)}")
    for m in mappings[:5]:
        print(f"  {m.source_column} -> {m.target_column} (score={m.ensemble_score:.2f})")
    unmapped = ai_engine.get_unmapped_columns(source_schema, target_schema, mappings)
    session["mappings"] = mappings
    session["stats"] = stats
    session["unmapped"] = unmapped
    
    return {
        "session_id": request.session_id,
        "total_mappings": len(mappings),
        "statistics": stats,
        "unmapped_source": len(unmapped["source"]),
        "unmapped_target": len(unmapped["target"]),
        "llm_used": ai_engine.llm_available
    }


@app.get("/api/mapping-report/{session_id}")
async def get_mapping_report(session_id: str):
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
                "llm": round(m.llm_score, 4),
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
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    source_path = session["source_path"]
    target_path = session["target_path"]
    mappings = session["mappings"]
    source_conn = sqlite3.connect(source_path)
    target_conn = sqlite3.connect(target_path)
    
    rows_migrated = 0
    rows_failed = 0
    failed_records = []
    
    try:
        table_mappings: Dict[tuple, List] = {}
        for m in mappings:
            key = (m.source_table, m.target_table)
            if key not in table_mappings:
                table_mappings[key] = []
            table_mappings[key].append(m)
        for (src_table, tgt_table), cols in table_mappings.items():
            source_cols = [m.source_column for m in cols]
            target_cols = [m.target_column for m in cols]
            query = f"SELECT {', '.join(source_cols)} FROM {src_table}"
            cursor = source_conn.execute(query)
            rows = cursor.fetchall()
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
        "failed_records": failed_records[:10],
        "validation_summary": validation["summary"],
        "timestamp": datetime.now().isoformat()
    }


async def validate_migration(session_id: str, source_path: str, target_path: str,
                            mappings: List[MatchResult]) -> Dict:
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
        table_pairs = set((m.source_table, m.target_table) for m in mappings)
        
        for src_table, tgt_table in table_pairs:
            try:
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
            except Exception as e:
                validation_results["row_counts"][f"{src_table} -> {tgt_table}"] = {
                    "source": 0, "target": 0, "difference": 0,                     "match": False, "error": str(e)
                }
            for m in mappings:
                if m.source_table == src_table:
                    try:
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
                    except Exception:
                        pass
            for m in mappings:
                if m.source_table == src_table and 'id' in m.source_column.lower():
                    try:
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
                    except Exception:
                        pass
        total_issues = sum(1 for v in validation_results["row_counts"].values() if not v.get("match", True))
        total_issues += sum(1 for v in validation_results["duplicate_checks"].values() if v.get("has_duplicates", False))
        
        if total_issues == 0:
            validation_results["summary"] = "âœ“ All validation checks passed. Data migration is complete and accurate."
        else:
            validation_results["summary"] = f"âš  {total_issues} validation issues found. Review the detailed report."
        
        return validation_results
    finally:
        source_conn.close()
        target_conn.close()


@app.get("/api/validation-report/{session_id}")
async def get_validation_report(session_id: str):
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
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    mappings = session["mappings"]
    unmapped = session.get("unmapped", {"source": [], "target": []})
    nodes = []
    links = []
    node_map = {}
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
    table_mappings = {}
    for m in mappings:
        key = f"{m.source_table} â†’ {m.target_table}"
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
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    mappings = session["mappings"]
    unmapped = session.get("unmapped", {"source": [], "target": []})
    validation = session.get("validation", {})
    migration = session.get("migration_result", {})
    explanations = {
        "column_mappings": [],
        "ignored_columns": [],
        "transformations": [],
        "failed_data": [],
        "summary": ""
    }
    for m in mappings:
        explanations["column_mappings"].append({
            "question": f"Why was '{m.source_column}' mapped to '{m.target_column}'?",
            "answer": m.why_mapped or m.explanation,
            "confidence": f"{m.ensemble_score * 100:.1f}% confident",
                "details": {
                    "Semantic analysis": f"BERT score: {m.bert_score * 100:.0f}%",
                "LLM reasoning": f"LLM score: {m.llm_score * 100:.0f}%",
                "Pattern matching": f"TF-IDF score: {m.tfidf_score * 100:.0f}%",
                "Database conventions": f"Domain score: {m.domain_score * 100:.0f}%"
            }
        })
    for u in unmapped["source"]:
        explanations["ignored_columns"].append({
            "question": f"Why was '{u['table']}.{u['column']}' not mapped?",
            "answer": u["reason"]
        })
    for m in mappings:
        if m.transformation and m.transformation != "none":
            explanations["transformations"].append({
                "question": f"What transformation was applied to '{m.source_column}'?",
                "answer": m.transformation,
                "source_type": m.data_type_source,
                "target_type": m.data_type_target
            })
    for record in migration.get("failed_records", [])[:10]:
        explanations["failed_data"].append({
            "question": f"Why did this record fail to migrate?",
            "record": record.get("data", {}),
            "error": record.get("error", "Unknown error"),
            "reason": record.get("reason", "Check data types and constraints")
        })
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
2. **Large Language Model** - Provides contextual reasoning like a human expert
3. **Pattern Matching** - Finds similar text patterns
4. **Database Knowledge** - Knows common abbreviations and conventions

### Key Insights
{validation.get('summary', 'Run migration to see validation results.')}
"""
    
    return explanations


@app.get("/api/sample-data")
async def create_sample_data():
    """
    Creates sample databases simulating the Apollo Munich + HDFC Ergo merger scenario.
    Minimal version with 2 core tables and ~150 records to stay within API limits.
    """
    import random
    
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / "sample"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    source_path = temp_dir / "legacy_crm.db"
    target_path = temp_dir / "modern_crm.db"
    
    # Indian names and cities
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rajesh", "Kavita",
                   "Suresh", "Deepika", "Arun", "Meena", "Sanjay", "Pooja", "Manoj", "Swati"]
    
    last_names = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Mehta", "Joshi",
                  "Agarwal", "Reddy", "Nair", "Iyer", "Rao", "Menon", "Shah", "Malhotra"]
    
    cities_states = [
        ("Mumbai", "MH", "400001"), ("Delhi", "DL", "110001"), ("Bangalore", "KA", "560001"),
        ("Hyderabad", "TS", "500001"), ("Chennai", "TN", "600001"), ("Pune", "MH", "411001")
    ]
    
    policy_types = [("OPT", "Optima Restore", 500000), ("EAZ", "Easy Health", 300000),
                    ("ENG", "Energy Gold", 700000), ("CRI", "Critical Advantage", 1500000)]
    
    # ============================================================================
    # SOURCE: Apollo Munich Legacy System (2 tables, ~150 records)
    # ============================================================================
    
    source_conn = sqlite3.connect(str(source_path))
    source_conn.executescript("""
        DROP TABLE IF EXISTS amb_policyholders;
        DROP TABLE IF EXISTS amb_policies;
        
        CREATE TABLE amb_policyholders (
            ph_id INTEGER PRIMARY KEY,
            ph_fname TEXT,
            ph_lname TEXT,
            ph_dob TEXT,
            ph_gender TEXT,
            ph_pan TEXT,
            ph_aadhar TEXT,
            ph_email TEXT,
            ph_mob TEXT,
            ph_addr1 TEXT,
            ph_city TEXT,
            ph_state TEXT,
            ph_pin TEXT,
            ph_kyc_status TEXT,
            ph_created_dt TEXT
        );
        
        CREATE TABLE amb_policies (
            pol_id INTEGER PRIMARY KEY,
            pol_no TEXT UNIQUE,
            ph_id INTEGER,
            pol_type TEXT,
            pol_name TEXT,
            sum_insured REAL,
            premium_amt REAL,
            pol_start_dt TEXT,
            pol_end_dt TEXT,
            ncb_pct REAL,
            copay_pct REAL,
            pol_status TEXT
        );
    """)
    
    # Generate 50 Policyholders
    policyholders = []
    for i in range(1, 51):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        city, state, pin = random.choice(cities_states)
        dob = f"{random.randint(1965, 1995)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        gender = random.choice(["M", "F"])
        pan = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000,9999)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))}"
        aadhar = f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
        email = f"{fname.lower()}.{lname.lower()}{i}@gmail.com"
        mob = f"+91{random.randint(7000000000, 9999999999)}"
        addr = f"{random.randint(1,500)}, Sector {random.randint(1,50)}"
        kyc = random.choice(["VERIFIED", "PENDING"])
        created = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        policyholders.append((i, fname, lname, dob, gender, pan, aadhar, email, mob, addr, city, state, pin, kyc, created))
    
    source_conn.executemany("INSERT INTO amb_policyholders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", policyholders)
    
    # Generate 100 Policies
    policies = []
    for i in range(1, 101):
        pol_no = f"AMB/HLT/2024/{i:05d}"
        ph_id = random.randint(1, 50)
        pol_type, pol_name, sum_ins = random.choice(policy_types)
        premium = int(sum_ins * random.uniform(0.015, 0.025))
        start_dt = f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        end_dt = f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        ncb = random.choice([0, 10, 20, 30])
        copay = random.choice([0, 10, 20])
        status = random.choice(["ACTIVE", "ACTIVE", "LAPSED"])
        policies.append((i, pol_no, ph_id, pol_type, pol_name, sum_ins, premium, start_dt, end_dt, ncb, copay, status))
    
    source_conn.executemany("INSERT INTO amb_policies VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", policies)
    source_conn.commit()
    source_conn.close()
    
    # ============================================================================
    # TARGET: HDFC Ergo Modern System (2 tables, empty)
    # ============================================================================
    
    target_conn = sqlite3.connect(str(target_path))
    target_conn.executescript("""
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS insurance_policies;
        
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            gender TEXT,
            pan_number TEXT,
            aadhaar_number TEXT,
            email_address TEXT,
            mobile_number TEXT,
            address_line_1 TEXT,
            city TEXT,
            state_code TEXT,
            pin_code TEXT,
            kyc_verification_status TEXT,
            created_at TEXT
        );
        
        CREATE TABLE insurance_policies (
            policy_id INTEGER PRIMARY KEY,
            policy_number TEXT,
            customer_id INTEGER,  -- FK removed for migration flexibility
            policy_type_code TEXT,
            policy_product_name TEXT,
            sum_assured REAL,
            annual_premium REAL,
            policy_start_date TEXT,
            policy_end_date TEXT,
            no_claim_bonus_percent REAL,
            co_payment_percent REAL,
            policy_status TEXT
        );
    """)
    target_conn.close()
    
    total_records = 50 + 100  # 150 total
    
    return {
        "message": f"Apollo Munich -> HDFC Ergo merger databases created with {total_records} records",
        "source_path": str(source_path),
        "target_path": str(target_path),
        "scenario": "Insurance Company Merger: Apollo Munich Health Insurance -> HDFC Ergo Health Insurance",
        "description": {
            "source": "Apollo Munich Legacy System (amb_* prefix, abbreviated columns)",
            "target": "HDFC Ergo Modern System (full descriptive column names)"
        },
        "tables": {
            "source": {
                "amb_policyholders": "50 policyholder records (15 columns with ph_* prefix)",
                "amb_policies": "100 insurance policies (12 columns with pol_* prefix)"
            },
            "target": {
                "customers": "Empty - ready for migration (15 columns, full names)",
                "insurance_policies": "Empty - ready for migration (12 columns, full names)"
            }
        },
        "statistics": {
            "policyholders": 50,
            "policies": 100,
            "total_records": total_records
        },
        "mapping_challenges": [
            "ph_id -> customer_id (ID field renaming)",
            "ph_fname -> first_name (prefix removal)",
            "ph_lname -> last_name (prefix removal)",
            "ph_dob -> date_of_birth (abbreviation expansion)",
            "ph_pan -> pan_number (abbreviation expansion)",
            "ph_aadhar -> aadhaar_number (spelling + expansion)",
            "ph_mob -> mobile_number (abbreviation expansion)",
            "pol_no -> policy_number (abbreviation expansion)",
            "sum_insured -> sum_assured (terminology change)",
            "premium_amt -> annual_premium (terminology change)",
            "ncb_pct -> no_claim_bonus_percent (abbreviation expansion)",
            "copay_pct -> co_payment_percent (abbreviation expansion)"
        ]
    }


@app.get("/api/sample-file/{file_type}")
async def get_sample_file(file_type: str):
    temp_dir = Path(tempfile.gettempdir()) / "dataforge" / "sample"
    
    if file_type == "source":
        file_path = temp_dir / "legacy_crm.db"
    elif file_type == "target":
        file_path = temp_dir / "modern_crm.db"
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'source' or 'target'")
    if not file_path.exists():
        await create_sample_data()
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/x-sqlite3"
    )


@app.websocket("/ws/migration/{session_id}")
async def websocket_migration(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in active_websockets:
        active_websockets[session_id] = []
    active_websockets[session_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        if session_id in active_websockets:
            active_websockets[session_id].remove(websocket)


async def broadcast_migration_update(session_id: str, update: Dict):
    if session_id in active_websockets:
        for ws in active_websockets[session_id]:
            try:
                await ws.send_text(json.dumps(update))
            except:
                pass


@app.post("/api/migrate-live")
async def execute_live_migration(session_id: str = Form(...)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["mappings"] is None:
        raise HTTPException(status_code=400, detail="Analysis not run yet")
    
    source_path = session["source_path"]
    target_path = session["target_path"]
    mappings = session["mappings"]
    migration_status[session_id] = {
        "status": "initializing",
        "phase": "setup",
        "total_tables": 0,
        "migrated_tables": 0,
        "total_rows": 0,
        "migrated_rows": 0,
        "failed_rows": 0,
        "current_table": "",
        "current_progress": 0,
        "tables_progress": [],
        "start_time": datetime.now().isoformat(),
        "errors": []
    }
    await broadcast_migration_update(session_id, {
        "type": "migration_start",
        "data": migration_status[session_id]
    })
    source_conn = sqlite3.connect(source_path)
    target_conn = sqlite3.connect(target_path)
    
    rows_migrated = 0
    rows_failed = 0
    failed_records = []
    
    try:
        table_mappings: Dict[tuple, List] = {}
        for m in mappings:
            key = (m.source_table, m.target_table)
            if key not in table_mappings:
                table_mappings[key] = []
            table_mappings[key].append(m)
        total_tables = len(table_mappings)
        migration_status[session_id]["total_tables"] = total_tables
        migration_status[session_id]["status"] = "migrating"
        migration_status[session_id]["phase"] = "data_transfer"
        total_rows = 0
        table_row_counts = {}
        for (src_table, tgt_table), cols in table_mappings.items():
            try:
                cursor = source_conn.execute(f"SELECT COUNT(*) FROM {src_table}")
                count = cursor.fetchone()[0]
                table_row_counts[(src_table, tgt_table)] = count
                total_rows += count
            except:
                table_row_counts[(src_table, tgt_table)] = 0
        
        migration_status[session_id]["total_rows"] = total_rows
        await broadcast_migration_update(session_id, {
            "type": "migration_progress",
            "data": {
                "phase": "counting",
                "total_tables": total_tables,
                "total_rows": total_rows
            }
        })
        table_index = 0
        for (src_table, tgt_table), cols in table_mappings.items():
            table_index += 1
            source_cols = [m.source_column for m in cols]
            target_cols = [m.target_column for m in cols]
            row_count = table_row_counts.get((src_table, tgt_table), 0)
            
            migration_status[session_id]["current_table"] = f"{src_table} â†’ {tgt_table}"
            migration_status[session_id]["tables_progress"].append({
                "source": src_table,
                "target": tgt_table,
                "status": "migrating",
                "rows": row_count,
                "migrated": 0,
                "failed": 0
            })
            await broadcast_migration_update(session_id, {
                "type": "table_start",
                "data": {
                    "table_index": table_index,
                    "source_table": src_table,
                    "target_table": tgt_table,
                    "total_rows": row_count,
                    "columns": list(zip(source_cols, target_cols))
                }
            })
            try:
                query = f"SELECT {', '.join(source_cols)} FROM {src_table}"
                cursor = source_conn.execute(query)
                rows = cursor.fetchall()
            except Exception as e:
                migration_status[session_id]["errors"].append({
                    "table": src_table,
                    "error": str(e),
                    "type": "read_error"
                })
                await broadcast_migration_update(session_id, {
                    "type": "table_error",
                    "data": {"table": src_table, "error": str(e)}
                })
                continue
            placeholders = ", ".join(["?" for _ in target_cols])
            insert_query = f"INSERT INTO {tgt_table} ({', '.join(target_cols)}) VALUES ({placeholders})"
            
            table_migrated = 0
            table_failed = 0
            batch_size = max(1, len(rows) // 20)
            for i, row in enumerate(rows):
                try:
                    target_conn.execute(insert_query, row)
                    rows_migrated += 1
                    table_migrated += 1
                except Exception as e:
                    rows_failed += 1
                    table_failed += 1
                    error_msg = str(e)
                    failed_records.append({
                        "source_table": src_table,
                        "target_table": tgt_table,
                        "row_index": i,
                        "data": dict(zip(source_cols, [str(v)[:50] for v in row])),
                        "error": error_msg
                    })
                    await broadcast_migration_update(session_id, {
                        "type": "row_failed",
                        "data": {
                            "table": src_table,
                            "row_index": i,
                            "error": error_msg,
                            "sample_data": dict(zip(source_cols[:3], [str(v)[:30] for v in row[:3]]))
                        }
                    })
                if i > 0 and i % batch_size == 0:
                    progress = (i / len(rows)) * 100
                    migration_status[session_id]["migrated_rows"] = rows_migrated
                    migration_status[session_id]["failed_rows"] = rows_failed
                    migration_status[session_id]["current_progress"] = progress
                    
                    await broadcast_migration_update(session_id, {
                        "type": "row_progress",
                        "data": {
                            "table": src_table,
                            "current_row": i,
                            "total_rows": len(rows),
                            "progress_percent": round(progress, 1),
                            "migrated": table_migrated,
                            "failed": table_failed,
                            "overall_migrated": rows_migrated,
                            "overall_failed": rows_failed
                        }
                    })
                    await asyncio.sleep(0.05)
            target_conn.commit()
            migration_status[session_id]["migrated_tables"] = table_index
            migration_status[session_id]["tables_progress"][-1]["status"] = "completed"
            migration_status[session_id]["tables_progress"][-1]["migrated"] = table_migrated
            migration_status[session_id]["tables_progress"][-1]["failed"] = table_failed
            
            await broadcast_migration_update(session_id, {
                "type": "table_complete",
                "data": {
                    "table_index": table_index,
                    "source_table": src_table,
                    "target_table": tgt_table,
                    "migrated": table_migrated,
                    "failed": table_failed,
                    "duration_seconds": 0
                }
            })
            await asyncio.sleep(0.1)
        migration_status[session_id]["phase"] = "validation"
        await broadcast_migration_update(session_id, {
            "type": "phase_change",
            "data": {"phase": "validation", "message": "Validating migrated data..."}
        })
        validation = await validate_migration(session_id, source_path, target_path, mappings)
        session["validation"] = validation
        await asyncio.sleep(0.3)
        migration_status[session_id]["status"] = "completed"
        migration_status[session_id]["phase"] = "finished"
        migration_status[session_id]["end_time"] = datetime.now().isoformat()
        
        session["migration_result"] = {
            "rows_migrated": rows_migrated,
            "rows_failed": rows_failed,
            "failed_records": failed_records
        }
        
        await broadcast_migration_update(session_id, {
            "type": "migration_complete",
            "data": {
                "success": rows_failed == 0,
                "total_migrated": rows_migrated,
                "total_failed": rows_failed,
                "tables_migrated": len(table_mappings),
                "validation_summary": validation.get("summary", {}),
                "duration_seconds": 0
            }
        })
    except Exception as e:
        migration_status[session_id]["status"] = "error"
        migration_status[session_id]["errors"].append({"error": str(e)})
        await broadcast_migration_update(session_id, {
            "type": "migration_error",
            "data": {"error": str(e)}
        })
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        source_conn.close()
        target_conn.close()
    return {
        "success": rows_failed == 0,
        "rows_migrated": rows_migrated,
        "rows_failed": rows_failed,
        "failed_records": failed_records[:10],
        "validation_summary": validation.get("summary", {}),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/migration-status/{session_id}")
async def get_migration_status(session_id: str):
    if session_id not in migration_status:
        return {"status": "not_started"}
    return migration_status[session_id]


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("DataForge Migration API")
    print("="*60)
    print(f"Groq LLM: {'Enabled' if GROQ_API_KEY else 'Disabled (set GROQ_API_KEY)'}")
    print("Model: Llama 3.3 70B Versatile")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
