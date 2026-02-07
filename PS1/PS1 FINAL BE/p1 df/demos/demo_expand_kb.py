"""
Demo: Expanding Knowledge Base Dynamically
Shows how to add multiple documents to the same knowledge base
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from embedding_engine import EmbeddingEngine

print("="*70)
print("DEMO: Expanding Knowledge Base")
print("="*70)

# Initialize engine (connects to existing ChromaDB)
engine = EmbeddingEngine()

# Check starting size
initial_count = engine.collection.count()
print(f"\nInitial knowledge base size: {initial_count} chunks")

# List current documents
print(f"\nCurrent documents in knowledge base:")
results = engine.collection.get(limit=100)
sources = set()
if results and 'metadatas' in results:
    for metadata in results['metadatas']:
        if metadata and 'source' in metadata:
            sources.add(metadata['source'])
    for source in sorted(sources):
        print(f"  - {source}")

print("\n" + "="*70)
print("You can add more PDFs anytime:")
print("="*70)
print("""
# Method 1: Python
engine.ingest_pdf("new_document.pdf", doc_id="new_001")

# Method 2: Pipeline
hunter.ingest_source_documents(["doc1.pdf", "doc2.pdf", "doc3.pdf"])

# Method 3: API
POST /upload-source with your PDF file

All methods ADD to the existing knowledge base!
No need to re-upload previous documents.
""")

print("\n" + "="*70)
print("Scalability:")
print("="*70)
print("- ChromaDB can handle MILLIONS of chunks")
print("- Each PDF adds ~10-50 chunks (depends on size)")
print("- No practical limit for hackathon/production use")
print("- Search stays fast even with 1000+ documents")
print("="*70)
