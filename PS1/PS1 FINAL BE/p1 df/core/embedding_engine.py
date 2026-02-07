"""
Embedding Engine for Hallucination Hunter
Handles document chunking, embedding generation, and vector storage.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import pdfplumber
import hashlib


class EmbeddingEngine:
    """Manages document embeddings and vector database operations."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", persist_dir: str = "./chroma_db"):
        """
        Initialize the embedding engine.
        
        Args:
            model_name: Name of the sentence-transformer model
            persist_dir: Directory to persist ChromaDB data
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="source_documents",
            metadata={"description": "Trusted source documents for fact verification"}
        )
        
        print(f"Embedding engine initialized. Collection size: {self.collection.count()}")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            chunk_size: Target size of each chunk (in characters)
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # Only break if not too early
                    chunk = chunk[:break_point + 1]
                    end = start + len(chunk)
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if c]  # Filter empty chunks
    
    def ingest_pdf(self, pdf_path: str, doc_id: str = None) -> int:
        """
        Ingest a PDF document into the vector database.
        
        Args:
            pdf_path: Path to the PDF file
            doc_id: Optional document identifier (uses filename hash if not provided)
            
        Returns:
            Number of chunks added
        """
        # Generate doc_id from filename if not provided
        if doc_id is None:
            doc_id = hashlib.md5(pdf_path.encode()).hexdigest()[:8]
        
        print(f"Ingesting PDF: {pdf_path}")
        
        # Extract text from PDF
        full_text = ""
        page_boundaries = []  # Track which page each chunk comes from
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    page_start = len(full_text)
                    full_text += page_text + "\n\n"
                    page_boundaries.append((page_start, len(full_text), page_num))
        
        # Chunk the text
        chunks = self.chunk_text(full_text)
        
        # Determine page number for each chunk
        chunk_metadata = []
        current_char = 0
        
        for chunk in chunks:
            chunk_start = full_text.find(chunk, current_char)
            chunk_end = chunk_start + len(chunk)
            
            # Find which page this chunk belongs to
            page_num = 1
            for page_start, page_end, pnum in page_boundaries:
                if chunk_start >= page_start and chunk_start < page_end:
                    page_num = pnum
                    break
            
            chunk_metadata.append({
                "doc_id": doc_id,
                "source": pdf_path,
                "page": page_num,
                "char_start": chunk_start,
                "char_end": chunk_end
            })
            current_char = chunk_end
        
        # Generate embeddings
        print(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        
        # Add to ChromaDB
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            metadatas=chunk_metadata,
            ids=ids
        )
        
        print(f"Successfully ingested {len(chunks)} chunks from {pdf_path}")
        return len(chunks)
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for chunks most similar to the query.
        
        Args:
            query: Query text (claim to verify)
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'score'
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.client.delete_collection("source_documents")
        self.collection = self.client.get_or_create_collection(
            name="source_documents",
            metadata={"description": "Trusted source documents for fact verification"}
        )
        print("Collection cleared.")


# Example Usage
if __name__ == "__main__":
    # Initialize engine
    engine = EmbeddingEngine()
    
    # Ingest the medical guidelines PDF
    num_chunks = engine.ingest_pdf("medical_guidelines.pdf")
    
    # Test search
    query = "What medication is prescribed for Type 2 Diabetes?"
    print(f"\nSearching for: {query}")
    results = engine.search_similar(query, top_k=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} (Score: {result['score']:.3f}) ---")
        print(f"Source: {result['metadata']['source']}, Page: {result['metadata']['page']}")
        print(f"Text: {result['text'][:200]}...")
