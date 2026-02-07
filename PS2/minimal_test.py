"""Minimal test - just check dictionaries exist and test method directly"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
sys.path.insert(0, src_dir)

print("Testing class attributes...")

# Just check the class definition, don't instantiate
import hybrid_ai_engine
HybridAIEngine = hybrid_ai_engine.HybridAIEngine

print("ABBREVIATIONS check:")
print(f"  'fname' -> {HybridAIEngine.ABBREVIATIONS.get('fname', 'NOT FOUND')}")
print(f"  'cust_fname' -> {HybridAIEngine.ABBREVIATIONS.get('cust_fname', 'NOT FOUND')}")
print(f"  'created_dt' -> {HybridAIEngine.ABBREVIATIONS.get('created_dt', 'NOT FOUND')}")
print(f"  'modified_dt' -> {HybridAIEngine.ABBREVIATIONS.get('modified_dt', 'NOT FOUND')}")

print("\nDIRECT_MAPPINGS check:")
for (src, tgt), score in list(HybridAIEngine.DIRECT_MAPPINGS.items())[:5]:
    print(f"  ({src}, {tgt}) -> {score}")

print("\nCOMMON_PREFIXES check:")
print(f"  {HybridAIEngine.COMMON_PREFIXES[:3]}...")

print("\nDone with static checks!")
