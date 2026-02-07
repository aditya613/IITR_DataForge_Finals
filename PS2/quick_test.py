"""Quick test for domain similarity improvements - no heavy model loading"""
import sys
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
sys.path.insert(0, src_dir)
os.chdir(script_dir)

# Import only the class, not instantiate yet
from hybrid_ai_engine import HybridAIEngine

# Test the class methods directly without model loading
print("Testing ABBREVIATIONS dict:")
abbrevs = HybridAIEngine.ABBREVIATIONS
print(f"  'fname' expands to: {abbrevs.get('fname')}")
print(f"  'cust_fname' expands to: {abbrevs.get('cust_fname')}")
print(f"  'created_dt' expands to: {abbrevs.get('created_dt')}")
print(f"  'modified_dt' expands to: {abbrevs.get('modified_dt')}")
print(f"  'cust_status' expands to: {abbrevs.get('cust_status')}")

print("\nTesting DIRECT_MAPPINGS:")
mappings = HybridAIEngine.DIRECT_MAPPINGS
for pair, score in list(mappings.items())[:5]:
    print(f"  {pair[0]} -> {pair[1]}: {score}")

print("\nTesting COMMON_PREFIXES:")
prefixes = HybridAIEngine.COMMON_PREFIXES
print(f"  Prefixes: {prefixes[:5]}...")

print("\nCreating engine (this will load BERT)...")
engine = HybridAIEngine(groq_api_key=None)
print("Engine created!")

print("\n" + "="*60)
print("DOMAIN SIMILARITY TESTS")
print("="*60)

test_pairs = [
    ('cust_id', 'customer_id'),
    ('cust_fname', 'first_name'),
    ('cust_lname', 'last_name'),
    ('cust_email', 'email_address'),
    ('cust_ph', 'phone_number'),
    ('cust_addr', 'street_address'),
    ('cust_city', 'city'),
    ('cust_state', 'state_code'),
    ('cust_zip', 'postal_code'),
    ('cust_type', 'customer_type'),
    ('cust_status', 'is_active'),
    ('created_dt', 'created_at'),
    ('modified_dt', 'updated_at'),
    ('fname', 'first_name'),
    ('lname', 'last_name'),
]

passed = 0
for src, tgt in test_pairs:
    domain_score = engine.calculate_domain_similarity(src, tgt)
    status = "✓" if domain_score >= 0.85 else "✗"
    if domain_score >= 0.85:
        passed += 1
    print(f'{status} {src:15} -> {tgt:18} | Domain: {domain_score:.2f}')

print(f"\nPassed: {passed}/{len(test_pairs)} ({100*passed/len(test_pairs):.0f}%)")
