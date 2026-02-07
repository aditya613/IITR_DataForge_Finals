"""
Claim Verifier for Hallucination Hunter
Uses NLI (Natural Language Inference) to verify claims against retrieved evidence.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict, Tuple
from embedding_engine import EmbeddingEngine


class ClaimVerifier:
    """Verifies factual claims using NLI and RAG retrieval."""
    
    # Label mappings for NLI model
    LABEL_MAP = {
        0: "contradiction",
        1: "neutral", 
        2: "entailment"
    }
    
    def __init__(self, nli_model_name: str = "roberta-large-mnli"):
        """
        Initialize the claim verifier.
        
        Args:
            nli_model_name: Name of the NLI model to use
        """
        print(f"Loading NLI model: {nli_model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(nli_model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(nli_model_name)
        self.model.eval()  # Set to evaluation mode
        
        # Initialize embedding engine for RAG
        self.embedding_engine = EmbeddingEngine()
        
        print("Claim verifier initialized.")
    
    def verify_claim(self, claim: str, top_k: int = 5) -> Dict:
        """
        Verify a single claim against the source documents.
        
        Args:
            claim: The claim to verify
            top_k: Number of evidence passages to retrieve
            
        Returns:
            Dictionary with verification results
        """
        # Step 1: Retrieve relevant passages using RAG
        evidence_chunks = self.embedding_engine.search_similar(claim, top_k=top_k)
        
        if not evidence_chunks:
            return {
                "claim": claim,
                "status": "unverifiable",
                "confidence": 0.0,
                "evidence": [],
                "explanation": "No relevant evidence found in source documents."
            }
        
        # Step 2: Run NLI on each evidence chunk
        nli_results = []
        
        for chunk in evidence_chunks:
            premise = chunk['text']  # The evidence
            hypothesis = claim  # The claim to verify
            
            # Run NLI model
            label, confidence = self._run_nli(premise, hypothesis)
            
            nli_results.append({
                "text": premise,
                "source": chunk['metadata']['source'],
                "page": chunk['metadata']['page'],
                "nli_label": label,
                "confidence": confidence,
                "retrieval_score": chunk['score']
            })
        
        # Step 3: Aggregate results to determine overall status
        final_status, explanation, best_evidence = self._aggregate_nli_results(
            claim, nli_results
        )
        
        return {
            "claim": claim,
            "status": final_status,
            "confidence": best_evidence['confidence'] if best_evidence else 0.0,
            "evidence": best_evidence,
            "all_evidence": nli_results[:3],  # Top 3 for review
            "explanation": explanation
        }
    
    def _run_nli(self, premise: str, hypothesis: str) -> Tuple[str, float]:
        """
        Run NLI model on premise-hypothesis pair.
        
        Args:
            premise: The evidence text (from source)
            hypothesis: The claim to verify
            
        Returns:
            (label, confidence) tuple
        """
        # Tokenize input
        inputs = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0]
        
        # Get prediction
        predicted_label = torch.argmax(probs).item()
        confidence = probs[predicted_label].item()
        label = self.LABEL_MAP.get(predicted_label, "unknown")
        
        return label, confidence
    
    def _aggregate_nli_results(self, claim: str, nli_results: List[Dict]) -> Tuple[str, str, Dict]:
        """
        Aggregate NLI results to determine final status.
        
        Priority:
        1. If any ENTAILMENT with high confidence → SUPPORTED
        2. If any CONTRADICTION with high confidence → CONTRADICTED
        3. Check for implicit contradictions (neutral with high retrieval) → CONTRADICTED
        4. Otherwise → UNVERIFIABLE
        
        Args:
            claim: The original claim
            nli_results: List of NLI results from different evidence chunks
            
        Returns:
            (status, explanation, best_evidence) tuple
        """
        ENTAILMENT_THRESHOLD = 0.7
        CONTRADICTION_THRESHOLD = 0.5  # Lower threshold to catch subtle hallucinations
        IMPLICIT_CONTRADICTION_RETRIEVAL_THRESHOLD = -0.1  # Allow negative scores for keyword matches
        
        # Find best entailment
        entailments = [r for r in nli_results if r['nli_label'] == 'entailment']
        if entailments:
            best_entailment = max(entailments, key=lambda x: x['confidence'])
            if best_entailment['confidence'] >= ENTAILMENT_THRESHOLD:
                explanation = (
                    f"Claim is SUPPORTED by evidence on page {best_entailment['page']}. "
                    f"Confidence: {best_entailment['confidence']:.2%}"
                )
                return "supported", explanation, best_entailment
        
        # Find best contradiction
        contradictions = [r for r in nli_results if r['nli_label'] == 'contradiction']
        if contradictions:
            best_contradiction = max(contradictions, key=lambda x: x['confidence'])
            if best_contradiction['confidence'] >= CONTRADICTION_THRESHOLD:
                explanation = (
                    f"Claim CONTRADICTS evidence on page {best_contradiction['page']}. "
                    f"Confidence: {best_contradiction['confidence']:.2%}"
                )
                return "contradicted", explanation, best_contradiction
        
        # Check for implicit contradictions: 
        # If the claim is about contraindications/avoiding something, and we found highly relevant
        # evidence about contraindications but NLI says neutral, it's likely an implicit contradiction
        # (e.g., claim says "liver disease" but source says "kidney disease")
        claim_lower = claim.lower()
        is_contraindication_claim = any(word in claim_lower for word in 
            ['avoid', 'contraindication', 'should not', 'must not', 'do not', 'don\'t'])
        
        if is_contraindication_claim:
            neutrals = [r for r in nli_results if r['nli_label'] == 'neutral']
            for result in neutrals:
                evidence_lower = result['text'].lower()
                # Check if evidence is about contraindications too
                is_contraindication_evidence = any(word in evidence_lower for word in
                    ['contraindication', 'avoid', 'should not', 'must not'])
                
                if is_contraindication_evidence and result['retrieval_score'] >= IMPLICIT_CONTRADICTION_RETRIEVAL_THRESHOLD:
                    explanation = (
                        f"Claim appears to CONTRADICT evidence on page {result['page']}. "
                        f"The source mentions different contraindications than the claim."
                    )
                    result['implicit_contradiction'] = True
                    return "contradicted", explanation, result
        
        # Default to unverifiable
        best_result = max(nli_results, key=lambda x: x['confidence']) if nli_results else None
        explanation = (
            "Claim cannot be verified with high confidence. "
            "Evidence is either insufficient or neutral."
        )
        
        return "unverifiable", explanation, best_result
    
    def verify_document(self, claims: List[str]) -> Dict:
        """
        Verify all claims in a document.
        
        Args:
            claims: List of atomic claims to verify
            
        Returns:
            Dictionary with overall verification results
        """
        results = []
        
        print(f"Verifying {len(claims)} claims...")
        for i, claim in enumerate(claims, 1):
            print(f"[{i}/{len(claims)}] Verifying: {claim[:60]}...")
            result = self.verify_claim(claim)
            results.append(result)
        
        # Calculate overall statistics
        supported = sum(1 for r in results if r['status'] == 'supported')
        contradicted = sum(1 for r in results if r['status'] == 'contradicted')
        unverifiable = sum(1 for r in results if r['status'] == 'unverifiable')
        
        # Calculate trust score
        total = len(results)
        trust_score = supported / total if total > 0 else 0.0
        
        # Penalize contradictions heavily
        trust_score -= (contradicted / total) * 0.5 if total > 0 else 0.0
        trust_score = max(0.0, min(1.0, trust_score))  # Clamp to [0, 1]
        
        return {
            "claims": results,
            "statistics": {
                "total": total,
                "supported": supported,
                "contradicted": contradicted,
                "unverifiable": unverifiable
            },
            "trust_score": trust_score
        }


# Example Usage
if __name__ == "__main__":
    from ingestion import atomize_claims
    
    # Initialize verifier
    verifier = ClaimVerifier()
    
    # Ensure we have source documents ingested
    print("\nIngesting source document...")
    verifier.embedding_engine.ingest_pdf("medical_guidelines.pdf")
    
    # Test with a sample LLM output
    llm_output = """
    The patient has Type 2 Diabetes and was prescribed Metformin. 
    The recommended starting dose is 500mg twice daily. 
    Metformin can cause vitamin B12 deficiency with long-term use.
    The patient should avoid taking Metformin if they have severe liver disease.
    """
    
    # Atomize into claims
    claims = atomize_claims(llm_output)
    print(f"\nExtracted {len(claims)} claims:")
    for i, claim in enumerate(claims, 1):
        print(f"  {i}. {claim}")
    
    # Verify all claims
    print("\n" + "="*60)
    verification_results = verifier.verify_document(claims)
    
    # Display results
    print("\n" + "="*60)
    print("VERIFICATION RESULTS")
    print("="*60)
    
    for i, result in enumerate(verification_results['claims'], 1):
        status_color = {
            'supported': '✓',
            'contradicted': '✗',
            'unverifiable': '?'
        }
        
        print(f"\n[{status_color[result['status']]}] Claim {i}: {result['claim']}")
        print(f"    Status: {result['status'].upper()}")
        print(f"    {result['explanation']}")
        
        if result['evidence']:
            print(f"    Evidence: {result['evidence']['text'][:100]}...")
    
    print("\n" + "="*60)
    print("OVERALL STATISTICS")
    print("="*60)
    stats = verification_results['statistics']
    print(f"Total Claims: {stats['total']}")
    print(f"Supported: {stats['supported']} ({stats['supported']/stats['total']*100:.1f}%)")
    print(f"Contradicted: {stats['contradicted']} ({stats['contradicted']/stats['total']*100:.1f}%)")
    print(f"Unverifiable: {stats['unverifiable']} ({stats['unverifiable']/stats['total']*100:.1f}%)")
    print(f"\nTrust Score: {verification_results['trust_score']:.2%}")
