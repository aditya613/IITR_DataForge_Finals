"""
Diagnostic script for Hallucination Hunter
Run this to test the verification pipeline and see detailed debug output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.embedding_engine import EmbeddingEngine
from core.claim_verifier import ClaimVerifier
from core.ingestion import atomize_claims

def run_debug():
    print("=" * 70)
    print("HALLUCINATION HUNTER - DEBUG DIAGNOSTIC")
    print("=" * 70)
    
    # Initialize
    print("\n[1] Initializing embedding engine...")
    engine = EmbeddingEngine()
    
    # Check knowledge base
    count = engine.collection.count()
    print(f"    Knowledge base contains: {count} chunks")
    
    if count == 0:
        print("\n[!] PROBLEM: Knowledge base is EMPTY!")
        print("    You need to upload PDFs first via the UI or run:")
        print("    engine.ingest_pdf('data/climate_science.pdf')")
        return
    
    # Test claim
    test_claim = "The global average temperature has increased by approximately 1.1 degrees Celsius since the pre-industrial era."
    
    print(f"\n[2] Testing claim: \"{test_claim[:60]}...\"")
    
    # Search for similar content
    print("\n[3] Searching for evidence...")
    results = engine.search_similar(test_claim, top_k=3)
    
    if not results:
        print("    [!] PROBLEM: No search results returned!")
        return
    
    print(f"    Found {len(results)} evidence chunks:")
    for i, r in enumerate(results):
        print(f"\n    Evidence {i+1}:")
        print(f"      Score: {r['score']:.4f}")
        print(f"      Source: {r['metadata']['source']}")
        print(f"      Text: {r['text'][:150]}...")
    
    # Test NLI
    print("\n[4] Running NLI verification...")
    verifier = ClaimVerifier()
    
    for i, evidence in enumerate(results):
        premise = evidence['text']
        hypothesis = test_claim
        
        label, confidence = verifier._run_nli(premise, hypothesis)
        
        print(f"\n    Evidence {i+1} NLI Result:")
        print(f"      Label: {label}")
        print(f"      Confidence: {confidence:.4f}")
        
        # Show thresholds
        print(f"      Entailment threshold: 0.7")
        print(f"      Would pass: {'YES' if label == 'entailment' and confidence >= 0.7 else 'NO'}")
    
    # Full verification
    print("\n[5] Full verification result:")
    result = verifier.verify_claim(test_claim)
    print(f"    Status: {result['status']}")
    print(f"    Confidence: {result['confidence']:.4f}")
    print(f"    Explanation: {result['explanation']}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    
    if result['status'] == 'unverifiable':
        print("\n[!] ISSUE: Claim is being marked as UNVERIFIABLE")
        print("\nPossible causes:")
        print("  1. NLI confidence is below 0.7 threshold")
        print("  2. Evidence retrieval score is too low")
        print("  3. Evidence text doesn't match claim semantically")
        print("\nRecommended fixes:")
        print("  - Lower ENTAILMENT_THRESHOLD in claim_verifier.py")
        print("  - Ensure PDFs are properly ingested")


if __name__ == "__main__":
    run_debug()
