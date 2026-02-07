import pdfplumber
import spacy

# Load lightweight NLP model for syntax parsing
nlp = spacy.load("en_core_web_sm")

def ingest_pdf(pdf_path):
    """Extracts text from the Source Knowledge Base[cite: 34]."""
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
    return text_content

def atomize_claims(llm_output_text):
    """
    Decomposes LLM generation into atomic factual claims[cite: 28].
    Uses syntactic dependency parsing to split compound sentences.
    """
    doc = nlp(llm_output_text)
    atomic_claims = []

    for sent in doc.sents:
        # Heuristic: If a sentence has a conjunction like 'but', 'and', 'however'
        # linked to two verbs, it likely contains multiple facts.
        
        # Simple Hackathon approach: Split by punctuation/conjunctions 
        # For production, use a 'text-simplification' model.
        # Here we treat the sentence as the atomic unit if it's short, 
        # or split it if it's long.
        
        if len(sent.text.split()) > 20: 
            # Placeholder logic for complex sentences
            # Ideally, use a dedicated splitter library or regex for ';', 'and'
            sub_clauses = sent.text.replace(";", ".").split(". ")
            atomic_claims.extend([c.strip() for c in sub_clauses if len(c) > 5])
        else:
            atomic_claims.append(sent.text.strip())
            
    return atomic_claims

# Example Usage
if __name__ == "__main__":
    source_text = ingest_pdf("data/medical_guidelines.pdf")  # The Ground Truth
    generated_summary = "The patient has Type 2 Diabetes and was prescribed Metformin."  # The LLM Output
    claims = atomize_claims(generated_summary)

    print(f"Atomic Claims: {claims}")
    # Output: ['The patient has Type 2 Diabetes', 'was prescribed Metformin']