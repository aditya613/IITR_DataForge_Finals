import os
import sys
sys.path.insert(0, 'src')

print("1. Importing...")
from hybrid_ai_engine import HybridAIEngine

# Use Groq key from environment
groq_key = os.getenv('GROQ_API_KEY', '')
print(f'2. Groq Key set: {bool(groq_key)}')

print("3. Creating engine...")
engine = HybridAIEngine(groq_api_key=groq_key)
print(f'4. LLM enabled: {engine.llm_available}')
print(f'5. BERT enabled: {engine.bert_model is not None}')

# Test individual column mappings - USER'S EXACT TEST CASE
print("\n" + "="*60)
print("DOMAIN SIMILARITY TESTS (should all be >90%)")
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
    bert_score = engine.calculate_bert_similarity(src, tgt)
    status = "✓" if domain_score >= 0.85 else "✗"
    if domain_score >= 0.85:
        passed += 1
    print(f'{status} {src:15} -> {tgt:18} | Domain: {domain_score:.2f} | BERT: {bert_score:.2f}')

print(f"\nPassed: {passed}/{len(test_pairs)} ({100*passed/len(test_pairs):.0f}%)")

# Full schema matching test
print("\n" + "="*60)
print("FULL SCHEMA MATCHING TEST")
print("="*60)

source_schema = {'customer_info': {
    'cust_id': 'INTEGER', 
    'cust_fname': 'TEXT', 
    'cust_lname': 'TEXT',
    'cust_email': 'TEXT',
    'cust_ph': 'TEXT',
    'cust_addr': 'TEXT',
    'cust_city': 'TEXT',
    'cust_state': 'TEXT',
    'cust_zip': 'TEXT',
    'cust_type': 'TEXT',
    'cust_status': 'TEXT',
    'created_dt': 'DATETIME',
    'modified_dt': 'DATETIME'
}}

target_schema = {'customers': {
    'customer_id': 'INTEGER',
    'first_name': 'TEXT',
    'last_name': 'TEXT',
    'email_address': 'TEXT',
    'phone_number': 'TEXT',
    'street_address': 'TEXT',
    'city': 'TEXT',
    'state_code': 'TEXT',
    'postal_code': 'TEXT',
    'customer_type': 'TEXT',
    'is_active': 'BOOLEAN',
    'created_at': 'DATETIME',
    'updated_at': 'DATETIME'
}}

results, stats = engine.match_columns(source_schema, target_schema, threshold=0.5)
print(f'\nMatches found: {len(results)}')
for r in results:
    llm_display = f'{r.llm_score:.2f}' if r.llm_score > 0 else 'N/A'
    print(f'  {r.source_column:15} -> {r.target_column:18} (ensemble={r.ensemble_score:.2f}, llm={llm_display})')

