"""
=============================================================================
FASTAPI BACKEND: Data Migration API
=============================================================================
RESTful API backend for the React dashboard.
Run with: uvicorn api:app --reload --port 8000
=============================================================================
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import sys
import json
import shutil
import uuid
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.schema_extractor import SchemaExtractor, DatabaseSchema
from src.hybrid_ai_engine import HybridAIEngine, ModelConfig, LLMProvider, create_hybrid_engine
from src.type_mapper import DataTypeMapper
from src.validation_engine import ValidationEngine
from src.migration_executor import MigrationExecutor
from src.simple_explainer import SimpleExplainer

# =============================================================================
# APP SETUP
# =============================================================================

app = FastAPI(
    title="AI Data Migration Platform API",
    description="Hybrid AI-powered database migration with LLM + BERT + TF-IDF",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# DATA MODELS
# =============================================================================

class LLMConfig(BaseModel):
    provider: str = Field(default="none", description="LLM provider: openai, azure_openai, ollama, groq, none")
    api_key: str = Field(default="", description="API key for the provider")
    model: str = Field(default="gpt-4o-mini", description="Model name")
    base_url: str = Field(default="", description="Base URL for API")

class AnalysisRequest(BaseModel):
    source_db_path: str
    target_db_path: str
    threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    llm_config: Optional[LLMConfig] = None

class MigrationRequest(BaseModel):
    source_db_path: str
    target_db_path: str
    mappings: List[Dict]
    batch_size: int = Field(default=100, ge=1)
    use_transaction: bool = True

class ColumnMapping(BaseModel):
    source_column: str
    target_column: str
    source_table: str
    target_table: str
    ensemble_score: float
    bert_score: float
    llm_score: float
    tfidf_score: float
    domain_score: float
    confidence_level: str
    llm_reasoning: str = ""

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class AppState:
    """Global application state"""
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.hybrid_engine: Optional[HybridAIEngine] = None
        
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "status": "initialized",
            "source_schema": None,
            "target_schema": None,
            "mappings": [],
            "validation_results": [],
            "migration_result": None
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, data: Dict):
        if session_id in self.sessions:
            self.sessions[session_id].update(data)

state = AppState()

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    return {
        "message": "AI Data Migration Platform API",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "Hybrid AI matching (BERT + LLM + TF-IDF + Domain)",
            "Schema extraction",
            "Data validation",
            "Migration execution",
            "Real-time progress tracking"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# -----------------------------------------------------------------------------
# SESSION MANAGEMENT
# -----------------------------------------------------------------------------

@app.post("/api/sessions")
async def create_session():
    """Create a new analysis session"""
    session_id = state.create_session()
    return {"session_id": session_id, "status": "created"}

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session status and data"""
    session = state.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# -----------------------------------------------------------------------------
# DATABASE UPLOAD
# -----------------------------------------------------------------------------

@app.post("/api/upload/database")
async def upload_database(file: UploadFile = File(...)):
    """Upload a SQLite database file"""
    os.makedirs("data/uploads", exist_ok=True)
    
    file_path = f"data/uploads/{uuid.uuid4()}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"file_path": file_path, "filename": file.filename}


# -----------------------------------------------------------------------------
# SCHEMA EXTRACTION
# -----------------------------------------------------------------------------

@app.post("/api/schema/extract")
async def extract_schema(db_path: str):
    """Extract schema from a database"""
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"Database not found: {db_path}")
    
    try:
        extractor = SchemaExtractor(db_path)
        schema = extractor.extract_schema()
        
        return {
            "database": db_path,
            "tables": [
                {
                    "name": table.name,
                    "row_count": table.row_count,
                    "columns": [
                        {
                            "name": col.name,
                            "type": col.data_type,
                            "nullable": col.is_nullable,
                            "is_primary_key": col.is_primary_key,
                            "is_foreign_key": col.is_foreign_key,
                            "sample_values": col.sample_values[:5] if col.sample_values else []
                        }
                        for col in table.columns
                    ]
                }
                for table in schema.tables
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# HYBRID AI MATCHING
# -----------------------------------------------------------------------------

@app.post("/api/match/analyze")
async def analyze_and_match(request: AnalysisRequest):
    """Run hybrid AI analysis on source and target databases"""
    
    # Validate paths
    if not os.path.exists(request.source_db_path):
        raise HTTPException(status_code=404, detail="Source database not found")
    if not os.path.exists(request.target_db_path):
        raise HTTPException(status_code=404, detail="Target database not found")
    
    try:
        # Initialize hybrid engine
        llm_config = request.llm_config or LLMConfig()
        engine = create_hybrid_engine(
            provider=llm_config.provider,
            api_key=llm_config.api_key,
            model=llm_config.model,
            base_url=llm_config.base_url
        )
        
        # Extract schemas
        source_extractor = SchemaExtractor(request.source_db_path)
        target_extractor = SchemaExtractor(request.target_db_path)
        
        source_schema = source_extractor.extract_schema()
        target_schema = target_extractor.extract_schema()
        
        # Match columns for each table combination
        all_mappings = []
        
        for src_table in source_schema.tables:
            for tgt_table in target_schema.tables:
                # Convert columns to dict format
                src_cols = [
                    {"name": c.name, "type": c.data_type}
                    for c in src_table.columns
                ]
                tgt_cols = [
                    {"name": c.name, "type": c.data_type}
                    for c in tgt_table.columns
                ]
                
                matches = engine.match_columns(
                    src_cols, tgt_cols,
                    source_table=src_table.name,
                    target_table=tgt_table.name,
                    threshold=request.threshold
                )
                
                for match in matches:
                    all_mappings.append(match.to_dict())
        
        # Group by table pair
        grouped_mappings = {}
        for m in all_mappings:
            key = f"{m['source_table']} → {m['target_table']}"
            if key not in grouped_mappings:
                grouped_mappings[key] = []
            grouped_mappings[key].append(m)
        
        # Calculate statistics
        total_mappings = len(all_mappings)
        high_conf = sum(1 for m in all_mappings if m['confidence_level'] == 'high')
        medium_conf = sum(1 for m in all_mappings if m['confidence_level'] == 'medium')
        low_conf = sum(1 for m in all_mappings if m['confidence_level'] == 'low')
        
        avg_bert = sum(m['bert_score'] for m in all_mappings) / max(1, total_mappings)
        avg_llm = sum(m['llm_score'] for m in all_mappings) / max(1, total_mappings)
        avg_tfidf = sum(m['tfidf_score'] for m in all_mappings) / max(1, total_mappings)
        avg_domain = sum(m['domain_score'] for m in all_mappings) / max(1, total_mappings)
        
        return {
            "status": "success",
            "source_tables": len(source_schema.tables),
            "target_tables": len(target_schema.tables),
            "total_mappings": total_mappings,
            "statistics": {
                "high_confidence": high_conf,
                "medium_confidence": medium_conf,
                "low_confidence": low_conf,
                "average_scores": {
                    "bert": round(avg_bert, 4),
                    "llm": round(avg_llm, 4),
                    "tfidf": round(avg_tfidf, 4),
                    "domain": round(avg_domain, 4)
                }
            },
            "llm_enabled": engine.llm_available,
            "grouped_mappings": grouped_mappings,
            "all_mappings": all_mappings
        }
        
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


# -----------------------------------------------------------------------------
# VALIDATION
# -----------------------------------------------------------------------------

@app.post("/api/validate")
async def validate_migration(source_path: str, target_path: str):
    """Run validation checks on databases"""
    
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="Source database not found")
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Target database not found")
    
    try:
        validation_engine = ValidationEngine(source_path, target_path)
        source_extractor = SchemaExtractor(source_path)
        source_schema = source_extractor.extract_schema()
        
        all_results = []
        
        for table in source_schema.tables:
            report = validation_engine.validate_pre_migration(table.name)
            all_results.extend([r.to_dict() for r in report.results])
        
        # Summarize
        passed = sum(1 for r in all_results if r['status'] == 'passed')
        failed = sum(1 for r in all_results if r['status'] == 'failed')
        warnings = sum(1 for r in all_results if r['status'] == 'warning')
        
        return {
            "status": "success",
            "summary": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "total": len(all_results)
            },
            "results": all_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# MIGRATION EXECUTION
# -----------------------------------------------------------------------------

@app.post("/api/migrate/execute")
async def execute_migration(request: MigrationRequest, background_tasks: BackgroundTasks):
    """Execute the migration with tracking"""
    
    if not os.path.exists(request.source_db_path):
        raise HTTPException(status_code=404, detail="Source database not found")
    if not os.path.exists(request.target_db_path):
        raise HTTPException(status_code=404, detail="Target database not found")
    
    try:
        executor = MigrationExecutor(request.source_db_path, request.target_db_path)
        
        total_migrated = 0
        total_failed = 0
        all_failed_records = []
        table_results = []
        
        # Group mappings by table
        table_mappings = {}
        for m in request.mappings:
            key = (m['source_table'], m['target_table'])
            if key not in table_mappings:
                table_mappings[key] = {}
            table_mappings[key][m['source_column']] = m['target_column']
        
        # Execute migration for each table
        for (src_table, tgt_table), col_mappings in table_mappings.items():
            result = executor.migrate_table(
                source_table=src_table,
                target_table=tgt_table,
                column_mappings=col_mappings,
                batch_size=request.batch_size,
                use_transaction=request.use_transaction
            )
            
            total_migrated += result.records_migrated
            total_failed += result.records_failed
            all_failed_records.extend([fr.to_dict() for fr in result.failed_records])
            
            table_results.append({
                "source_table": src_table,
                "target_table": tgt_table,
                "records_migrated": result.records_migrated,
                "records_failed": result.records_failed
            })
        
        success_rate = (total_migrated / max(1, total_migrated + total_failed)) * 100
        
        return {
            "status": "success" if total_failed == 0 else "completed_with_errors",
            "summary": {
                "total_migrated": total_migrated,
                "total_failed": total_failed,
                "success_rate": round(success_rate, 2)
            },
            "table_results": table_results,
            "failed_records": all_failed_records[:100]  # Limit to first 100
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# EXPLANATIONS
# -----------------------------------------------------------------------------

@app.post("/api/explain/mapping")
async def explain_mapping(mapping: ColumnMapping):
    """Get detailed explanation for a column mapping"""
    
    explainer = SimpleExplainer()
    
    explanation = explainer.explain_column_mapping(
        source_col=mapping.source_column,
        target_col=mapping.target_column,
        confidence=mapping.ensemble_score,
        source_type=mapping.source_column,
        target_type=mapping.target_column
    )
    
    return {
        "heading": explanation.heading,
        "plain_english": explanation.plain_english,
        "analogy": explanation.analogy,
        "details": explanation.details,
        "confidence_level": mapping.confidence_level,
        "model_scores": {
            "bert": mapping.bert_score,
            "llm": mapping.llm_score,
            "tfidf": mapping.tfidf_score,
            "domain": mapping.domain_score,
            "ensemble": mapping.ensemble_score
        }
    }


# -----------------------------------------------------------------------------
# SAMPLE DATA
# -----------------------------------------------------------------------------

@app.post("/api/sample-data/create")
async def create_sample_data():
    """Create sample databases for testing"""
    try:
        from create_sample_data import create_sample_databases
        create_sample_databases()
        
        return {
            "status": "success",
            "source_path": "data/source_legacy_crm.db",
            "target_path": "data/target_modern_crm.db"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-data/status")
async def check_sample_data():
    """Check if sample databases exist"""
    source_exists = os.path.exists("data/source_legacy_crm.db")
    target_exists = os.path.exists("data/target_modern_crm.db")
    
    return {
        "source_exists": source_exists,
        "target_exists": target_exists,
        "ready": source_exists and target_exists,
        "source_path": "data/source_legacy_crm.db",
        "target_path": "data/target_modern_crm.db"
    }


# -----------------------------------------------------------------------------
# VISUALIZATION DATA
# -----------------------------------------------------------------------------

@app.post("/api/visualizations/sankey")
async def get_sankey_data(mappings: List[Dict]):
    """Get data formatted for Sankey diagram"""
    
    nodes = []
    links = []
    node_index = {}
    
    for m in mappings:
        src_node = f"src_{m['source_table']}_{m['source_column']}"
        tgt_node = f"tgt_{m['target_table']}_{m['target_column']}"
        
        if src_node not in node_index:
            node_index[src_node] = len(nodes)
            nodes.append({
                "id": src_node,
                "name": f"{m['source_table']}.{m['source_column']}",
                "type": "source"
            })
        
        if tgt_node not in node_index:
            node_index[tgt_node] = len(nodes)
            nodes.append({
                "id": tgt_node,
                "name": f"{m['target_table']}.{m['target_column']}",
                "type": "target"
            })
        
        links.append({
            "source": node_index[src_node],
            "target": node_index[tgt_node],
            "value": m.get('ensemble_score', 0.5) * 10,
            "confidence": m.get('confidence_level', 'medium')
        })
    
    return {"nodes": nodes, "links": links}


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
