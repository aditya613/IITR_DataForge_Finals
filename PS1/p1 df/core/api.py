"""
FastAPI Backend for Hallucination Hunter
REST API for fact-checking and citation verification.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
import uuid
from datetime import datetime

# Import our custom modules
from ingestion import atomize_claims, ingest_pdf
from embedding_engine import EmbeddingEngine
from claim_verifier import ClaimVerifier
from citation_linker import CitationLinker
from correction_engine import CorrectionEngine


# Initialize FastAPI app
app = FastAPI(
    title="Hallucination Hunter API",
    description="API for automated fact-checking and citation of LLM-generated content",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Initialize components
embedding_engine = None
claim_verifier = None
citation_linker = CitationLinker()
correction_engine = CorrectionEngine()

# Storage for verification jobs
jobs = {}


# Pydantic models for API
class VerifyRequest(BaseModel):
    """Request model for verification endpoint."""
    llm_text: str
    source_doc_id: Optional[str] = None


class VerificationResponse(BaseModel):
    """Response model for verification results."""
    job_id: str
    status: str
    trust_score: Optional[float] = None
    statistics: Optional[Dict] = None
    claims: Optional[List[Dict]] = None
    annotated_html: Optional[str] = None
    citations: Optional[List[Dict]] = None
    corrections: Optional[List[Dict]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup."""
    global embedding_engine, claim_verifier
    
    print("Initializing Hallucination Hunter backend...")
    embedding_engine = EmbeddingEngine()
    claim_verifier = ClaimVerifier()
    print("Backend ready!")


# Root endpoint (no prefix)
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Hallucination Hunter API",
        "version": "1.0.0",
        "status": "running"
    }


@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "embedding_engine": embedding_engine is not None,
        "claim_verifier": claim_verifier is not None,
        "collection_size": embedding_engine.collection.count() if embedding_engine else 0
    }


@api_router.post("/upload-source")
async def upload_source_document(file: UploadFile = File(...)):
    """
    Upload a source document (PDF) to the knowledge base.
    
    Args:
        file: PDF file upload
        
    Returns:
        Document ID and ingestion statistics
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Ingest into vector database
        num_chunks = embedding_engine.ingest_pdf(temp_path, doc_id=file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "doc_id": file.filename,
            "chunks_ingested": num_chunks,
            "message": f"Successfully ingested {num_chunks} chunks from {file.filename}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@api_router.post("/verify", response_model=VerificationResponse)
async def verify_text(request: VerifyRequest):
    """
    Verify LLM-generated text against source documents.
    
    Args:
        request: Verification request with LLM text
        
    Returns:
        Verification results with citations and corrections
    """
    # Generate job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Store job
    jobs[job_id] = {
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "llm_text": request.llm_text
    }
    
    try:
        # Step 1: Atomize claims
        claims = atomize_claims(request.llm_text)
        
        # Step 2: Verify claims
        verification_results = claim_verifier.verify_document(claims)
        
        # Step 3: Generate citations
        annotated_data = citation_linker.annotate_text_with_citations(
            request.llm_text,
            verification_results['claims']
        )
        
        # Step 4: Generate corrections
        correction_report = correction_engine.generate_correction_report(
            verification_results['claims']
        )
        
        # Step 5: Generate HTML
        annotated_html = citation_linker.generate_html_annotated_text(annotated_data)
        
        # Prepare response
        response = {
            "job_id": job_id,
            "status": "completed",
            "trust_score": verification_results['trust_score'],
            "statistics": verification_results['statistics'],
            "claims": verification_results['claims'],
            "annotated_html": annotated_html,
            "citations": annotated_data['citations'],
            "corrections": correction_report['corrections']
        }
        
        # Update job
        jobs[job_id] = {**jobs[job_id], **response, "status": "completed"}
        
        return response
    
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@api_router.get("/results/{job_id}", response_model=VerificationResponse)
async def get_results(job_id: str):
    """
    Get verification results for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Verification results
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]


@api_router.get("/evidence/{claim_index}")
async def get_evidence(claim_index: int, job_id: str):
    """
    Get detailed evidence for a specific claim.
    
    Args:
        claim_index: Index of the claim
        job_id: Job identifier
        
    Returns:
        Evidence details
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if claim_index >= len(job.get('claims', [])):
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim_result = job['claims'][claim_index]
    
    return {
        "claim": claim_result['claim'],
        "status": claim_result['status'],
        "confidence": claim_result['confidence'],
        "explanation": claim_result['explanation'],
        "evidence": claim_result.get('evidence'),
        "all_evidence": claim_result.get('all_evidence', [])
    }


@api_router.delete("/clear-knowledge-base")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base."""
    try:
        embedding_engine.clear_collection()
        return {"status": "success", "message": "Knowledge base cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear knowledge base: {str(e)}")


@api_router.get("/knowledge-base")
async def get_knowledge_base():
    """Get list of documents in the knowledge base."""
    try:
        results = embedding_engine.collection.get(limit=100)
        sources = {}
        
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if metadata and 'source' in metadata:
                    source = metadata['source']
                    if source not in sources:
                        sources[source] = {
                            "name": source,
                            "status": "indexed",
                            "chunks": 0
                        }
                    sources[source]["chunks"] += 1
        
        return {"sources": list(sources.values()), "total": len(sources)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge base: {str(e)}")


@api_router.get("/stats")
async def get_stats():
    """Get dashboard statistics."""
    # Calculate stats from jobs history
    total_verifications = len(jobs)
    completed = sum(1 for j in jobs.values() if j.get('status') == 'completed')
    
    if completed > 0:
        avg_trust = sum(j.get('trust_score', 0) for j in jobs.values() if j.get('status') == 'completed') / completed
        total_contradictions = sum(
            j.get('statistics', {}).get('contradicted', 0) 
            for j in jobs.values() 
            if j.get('status') == 'completed'
        )
    else:
        avg_trust = 0
        total_contradictions = 0
    
    return {
        "total_verifications": total_verifications,
        "avg_trust_score": round(avg_trust * 100, 1),
        "total_contradictions": total_contradictions,
        "knowledge_base_size": embedding_engine.collection.count() if embedding_engine else 0
    }


# Include the API router
app.include_router(api_router)


# Run the server
if __name__ == "__main__":
    import uvicorn
    
    print("Starting Hallucination Hunter API server...")
    print("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
