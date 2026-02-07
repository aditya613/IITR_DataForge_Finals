"""
Quick test to verify sentence extraction works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from correction_engine import CorrectionEngine

# Initialize correction engine
engine = CorrectionEngine()

# Test case: Evidence is a multi-sentence paragraph
claim = "Employees get 20 days of annual leave per year"

evidence = {
    'text': """The employment contract specifies a 40-hour work week with flexible scheduling. 
    Full-time employees are entitled to 15 days of paid annual leave per year, which increases to 20 days after 5 years of service.
    Health insurance coverage includes dental and vision for the employee and dependents.""",
    'source': 'employment_contract.pdf',
    'page': 3,
    'confidence': 0.85
}

# Generate correction
correction = engine.suggest_correction(claim, evidence, 'contradicted')

print("="*80)
print("SENTENCE EXTRACTION TEST")
print("="*80)
print(f"\nOriginal Claim:\n  {claim}")
print(f"\nFull Evidence Paragraph:\n  {evidence['text']}")
print(f"\nExtracted Correction (should be just one sentence):\n  {correction['suggested_correction']}")
print(f"\nExplanation:\n  {correction['explanation']}")
print("="*80)

# Check if it's shorter than full evidence
if len(correction['suggested_correction']) < len(evidence['text']):
    print("✅ SUCCESS: Correction is shorter than full evidence (single sentence extracted)")
else:
    print("❌ FAILED: Correction is the same length as evidence (still using full paragraph)")
