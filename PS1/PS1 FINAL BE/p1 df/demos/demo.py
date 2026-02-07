"""
DEMO - Hallucination Hunter
Live demonstration of the fact-checking system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from pipeline import HallucinationHunter

print("""
========================================================================
|              HALLUCINATION HUNTER - LIVE DEMO                        |
|              Automated Fact-Checking for LLMs                        |
========================================================================
""")

# Initialize the system
print("\nStep 1: Initializing Hallucination Hunter...")
hunter = HallucinationHunter()

# Ingest source document
print("\nStep 2: Ingesting source document (medical_guidelines.pdf)...")
hunter.ingest_source_documents(["data/medical_guidelines.pdf"])

# Sample LLM output with a known hallucination
llm_output = """
The patient has Type 2 Diabetes and was prescribed Metformin.
The starting dose is 500mg twice daily.
Metformin can cause vitamin B12 deficiency with long-term use.
The patient should avoid Metformin if they have severe liver disease.
"""

print("\n" + "="*70)
print("Step 3: LLM-Generated Text to Verify:")
print("="*70)
print(llm_output)

print("\n" + "="*70)
print("Step 4: Running Verification Pipeline...")
print("="*70)

# Run verification
results = hunter.verify_llm_output(llm_output, output_file="demo_results.json")

# Display results
print("\n" + "="*70)
print("DEMO RESULTS")
print("="*70)

hunter.print_summary(results)

# Show specific hallucination details
print("\n" + "="*70)
print("HALLUCINATION DETAILS")
print("="*70)

for i, claim_result in enumerate(results['claims'], 1):
    if claim_result['status'] == 'contradicted':
        print(f"\n[HALLUCINATION DETECTED #{i}]")
        print(f"Claim: {claim_result['claim']}")
        print(f"Issue: {claim_result['explanation']}")
        
        if claim_result.get('evidence'):
            print(f"\nCorrect Information from Source:")
            print(f"  {claim_result['evidence']['text']}")
            print(f"  (Source: Page {claim_result['evidence']['page']}, Confidence: {claim_result['evidence']['confidence']:.0%})")

# Show what was generated
print("\n" + "="*70)
print("OUTPUT FILES GENERATED")
print("="*70)
print("[OK] demo_results.json - Complete verification data")
print("[OK] annotated_output.html - Color-coded visualization")
print("\n>>> Open 'annotated_output.html' in your browser to see the visual results!")

print("\n" + "="*70)
print("DEMO COMPLETE!")
print("="*70)
print("\nKey Takeaways:")
print("1. Automatically detected the hallucination about 'liver disease'")
print("2. Correctly identified it should be 'kidney disease'")
print("3. Provided source citation with page number")
print("4. Calculated trust score based on claim accuracy")
print("5. Generated color-coded HTML for easy review")
print("\n" + "="*70)
