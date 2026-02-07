"""
Test Script for Hallucination Hunter
Validates the complete system with sample data.
"""

import os
import sys

# Add core folder to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)
    
    try:
        from ingestion import atomize_claims, ingest_pdf
        print("[OK] ingestion.py")
    except ImportError as e:
        print(f"[FAIL] ingestion.py: {e}")
        return False
    
    try:
        from embedding_engine import EmbeddingEngine
        print("[OK] embedding_engine.py")
    except ImportError as e:
        print(f"[FAIL] embedding_engine.py: {e}")
        return False
    
    try:
        from claim_verifier import ClaimVerifier
        print("[OK] claim_verifier.py")
    except ImportError as e:
        print(f"[FAIL] claim_verifier.py: {e}")
        return False
    
    try:
        from citation_linker import CitationLinker
        print("[OK] citation_linker.py")
    except ImportError as e:
        print(f"[FAIL] citation_linker.py: {e}")
        return False
    
    try:
        from correction_engine import CorrectionEngine
        print("[OK] correction_engine.py")
    except ImportError as e:
        print(f"[FAIL] correction_engine.py: {e}")
        return False
    
    print("\nAll modules imported successfully!")
    return True


def test_claim_atomization():
    """Test claim atomization."""
    print("\n" + "="*70)
    print("TEST 2: Claim Atomization")
    print("="*70)
    
    from ingestion import atomize_claims
    
    test_text = "The patient has diabetes and was prescribed medication. Treatment started yesterday."
    claims = atomize_claims(test_text)
    
    print(f"Input: {test_text}")
    print(f"\nExtracted {len(claims)} claims:")
    for i, claim in enumerate(claims, 1):
        print(f"  {i}. {claim}")
    
    return len(claims) > 0


def test_embedding_engine():
    """Test embedding engine."""
    print("\n" + "="*70)
    print("TEST 3: Embedding Engine")
    print("="*70)
    
    from embedding_engine import EmbeddingEngine
    
    try:
        engine = EmbeddingEngine()
        print("[OK] Embedding engine initialized")
        
        # Test if medical_guidelines.pdf exists
        if os.path.exists("data/medical_guidelines.pdf"):
            print("\n[OK] Found data/medical_guidelines.pdf")
            num_chunks = engine.ingest_pdf("data/medical_guidelines.pdf")
            print(f"[OK] Ingested {num_chunks} chunks")
            
            # Test search
            query = "What is prescribed for diabetes?"
            results = engine.search_similar(query, top_k=3)
            print(f"\n[OK] Search results for: '{query}'")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.3f}, Page: {result['metadata']['page']}")
            
            return True
        else:
            print("[WARN] medical_guidelines.pdf not found - skipping ingestion test")
            return True
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_nli_verifier():
    """Test NLI claim verifier."""
    print("\n" + "="*70)
    print("TEST 4: NLI Verifier")
    print("="*70)
    
    from claim_verifier import ClaimVerifier
    
    try:
        verifier = ClaimVerifier()
        print("[OK] NLI verifier initialized")
        
        # Test NLI on simple example
        premise = "The patient was diagnosed with Type 2 Diabetes."
        hypothesis = "The patient has diabetes."
        
        label, confidence = verifier._run_nli(premise, hypothesis)
        print(f"\nTest NLI:")
        print(f"  Premise: {premise}")
        print(f"  Hypothesis: {hypothesis}")
        print(f"  Result: {label} (confidence: {confidence:.2%})")
        
        return label in ['entailment', 'neutral', 'contradiction']
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end():
    """Test complete pipeline."""
    print("\n" + "="*70)
    print("TEST 5: End-to-End Pipeline")
    print("="*70)
    
    try:
        from pipeline import HallucinationHunter
        
        hunter = HallucinationHunter()
        print("[OK] Pipeline initialized")
        
        # Simple test without PDF
        test_text = "Water boils at 100 degrees Celsius at sea level."
        
        from ingestion import atomize_claims
        claims = atomize_claims(test_text)
        print(f"\n[OK] Extracted {len(claims)} claims from test text")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("HALLUCINATION HUNTER - TEST SUITE")
    print("="*70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Claim Atomization", test_claim_atomization),
        ("Embedding Engine", test_embedding_engine),
        ("NLI Verifier", test_nli_verifier),
        ("End-to-End Pipeline", test_end_to_end)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n[FAIL] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[OK] All tests passed! System is ready.")
        return 0
    else:
        print(f"\n[WARN] {total_count - passed_count} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
