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
======================================================================

Trust Score: 75.0% ⭐

Total Claims: 4
  ✓ Supported: 3 (75.0%)
  ✗ Contradicted: 1 (25.0%)
  ? Unverifiable: 0 (0.0%)

HALLUCINATIONS DETECTED
======================================================================

✗ Claim: patient should avoid if they have severe liver disease
  Issue: Contradicts evidence - should be kidney, not liver
  Evidence: Severe kidney disease (eGFR < 30 mL/min/1.73 m²)...
```

## 🧪 Testing the System

### Test with Sample Data

```python
from pipeline import HallucinationHunter

hunter = HallucinationHunter()

# Ingest source documents
hunter.ingest_source_documents(["medical_guidelines.pdf"])

# Test LLM output with known hallucination
llm_text = """
The patient has Type 2 Diabetes and was prescribed Metformin.
The patient should avoid Metformin if they have severe liver disease.
"""

# Run verification
results = hunter.verify_llm_output(llm_text)

# Print summary
hunter.print_summary(results)
```

## 🔬 How It Works

1. **Ingestion**: Source PDFs are chunked and embedded into ChromaDB
2. **Retrieval**: For each claim, retrieve top-k similar passages using semantic search
3. **Verification**: NLI model checks if evidence entails/contradicts the claim
4. **Citation**: Link claims to source passages with confidence scores
5. **Correction**: For contradictions, suggest corrections from source text

## 📈 Performance Metrics

- **Latency**: < 5 seconds for single-page document
- **Accuracy**: Depends on NLI model (~90% on MNLI benchmark)
- **Citation Precision**: Links to exact source paragraphs

## 🛠️ Customization

### Change NLI Model

In `claim_verifier.py`:
```python
verifier = ClaimVerifier(nli_model_name="roberta-large-mnli")
```

### Adjust Confidence Thresholds

In `claim_verifier.py`, edit:
```python
ENTAILMENT_THRESHOLD = 0.7  # Increase for stricter verification
CONTRADICTION_THRESHOLD = 0.7
```

### Change Embedding Model

In `embedding_engine.py`:
```python
engine = EmbeddingEngine(model_name="all-mpnet-base-v2")  # Better but slower
```

## 📝 License

MIT License - Feel free to use for your hackathon!

## 🙌 Credits

Built with:
- [sentence-transformers](https://www.sbert.net/)
- [transformers](https://huggingface.co/transformers/)
- [ChromaDB](https://www.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [spaCy](https://spacy.io/)
