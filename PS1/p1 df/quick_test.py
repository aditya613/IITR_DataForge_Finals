import sys
sys.path.insert(0, 'core')

from embedding_engine import EmbeddingEngine
from claim_verifier import ClaimVerifier

engine = EmbeddingEngine()
print(f'Knowledge base: {engine.collection.count()} chunks')

claim = 'GPT-4 was released in March 2023 by OpenAI and represents a major advancement in AI.'
print(f'\nClaim: {claim}')

# Search for evidence
results = engine.search_similar(claim, top_k=3)
print(f'\nEvidence found: {len(results)} chunks')
for i, r in enumerate(results):
    score = r["score"]
    source = r["metadata"]["source"]
    text = r["text"][:120]
    print(f'  {i+1}. Score: {score:.4f}')
    print(f'     Source: {source}')
    print(f'     Text: {text}...')

# Verify
verifier = ClaimVerifier()
result = verifier.verify_claim(claim)
print(f'\n=== RESULT ===')
print(f'Status: {result["status"].upper()}')
print(f'Confidence: {result["confidence"]:.2%}')
print(f'Explanation: {result["explanation"]}')
