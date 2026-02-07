# Hallucination Hunter 🔍

An automated fact-checking and citation system for LLM-generated content. Detects hallucinations, provides source citations, and suggests corrections using RAG + NLI.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter build errors on Windows, use:
```bash
pip install --only-binary :all: sentence-transformers chromadb transformers torch
```

### 2. Run the Complete Pipeline

```bash
python pipeline.py
```

This will:
1. Load the ML models (sentence-transformers + NLI)
2. Ingest source documents into the vector database
3. Verify your LLM-generated text
4. Generate an annotated HTML report

### 3. Start the API Server

```bash
python api.py
```

Then open `http://localhost:8000/docs` for the interactive API documentation.

## 📁 Project Structure

```
.
├── ingestion.py           # PDF extraction & claim atomization
├── embedding_engine.py    # ChromaDB + sentence-transformers
├── claim_verifier.py      # NLI-based verification
├── citation_linker.py     # Citation generation & HTML annotation
├── correction_engine.py   # Hallucination correction suggestions
├── api.py                 # FastAPI backend
├── pipeline.py            # End-to-end CLI pipeline
└── requirements.txt       # Python dependencies
```

## 🧠 ML Models Used

1. **Embedding Model**: `all-MiniLM-L6-v2` (sentence-transformers)
   - Generates semantic embeddings for RAG retrieval
   - Fast and lightweight (<100MB)

2. **NLI Model**: `microsoft/deberta-v3-base-mnli`
   - Classifies claims as entailment/contradiction/neutral
   - State-of-the-art accuracy on MNLI

3. **Claim Atomization**: spaCy `en_core_web_sm`
   - Dependency parsing for claim extraction

## 🔧 Backend API Endpoints

### `POST /upload-source`
Upload a PDF source document to the knowledge base.

**Request**: Multipart form with PDF file

**Response**:
```json
{
  "status": "success",
  "filename": "medical_guidelines.pdf",
  "chunks_ingested": 42
}
```

### `POST /verify`
Verify LLM-generated text against source documents.

**Request**:
```json
{
  "llm_text": "The patient has Type 2 Diabetes..."
}
```

**Response**:
```json
{
  "job_id": "a3b2c1d4",
  "trust_score": 0.85,
  "statistics": {
    "total": 5,
    "supported": 4,
    "contradicted": 1,
    "unverifiable": 0
  },
  "claims": [...],
  "citations": [...],
  "corrections": [...]
}
```

### `GET /results/{job_id}`
Retrieve verification results for a job.

### `GET /evidence/{claim_index}?job_id={job_id}`
Get detailed evidence for a specific claim.

## 🎯 Key Features

### 1. **Claim Verification**
- Atomic claim decomposition
- RAG-based retrieval of relevant passages
- NLI model classifies: Supported / Contradicted / Unverifiable

### 2. **Citation Linking**
- Maps each claim to exact source passages
- Includes page numbers and confidence scores
- Generates formatted footnotes

### 3. **Hallucination Detection**
- Identifies contradictions with source documents
- Provides evidence for contradictions
- Suggests corrections based on source text

### 4. **Trust Scoring**
- Overall document trust score (0-1)
- Weighted by claim importance and confidence
- Penalizes contradictions heavily

### 5. **HTML Annotation**
- Color-coded claims:
  - 🟢 Green = Supported
  - 🔴 Red = Contradicted
  - 🟡 Yellow = Unverifiable
- Inline citation markers
- Hover tooltips with explanations

## 📊 Example Output

```
VERIFICATION SUMMARY
