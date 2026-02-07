
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / "PS2" / "src"))

from hybrid_ai_engine import HybridAIEngine, create_engine

print("Initializing Engine...")
try:
    # Use the same key as in api.py
    engine = create_engine(gemini_api_key="YOUR_GEMINI_API_KEY_HERE")
    print(f"Engine initialized. Model: {engine.gemini_model.model_name}")
except Exception as e:
    print(f"Failed to init engine: {e}")
    sys.exit(1)

print("\nRunning Test Analysis...")
try:
    # Mock data simulating what api.py passes
    source_cols = ["cust_id", "fname", "email"]
    target_cols = ["customer_id", "first_name", "email_address"]
    
    # Simple strings/types
    src_types = {"cust_id": "INTEGER", "fname": "TEXT", "email": "TEXT"}
    tgt_types = {"customer_id": "INTEGER", "first_name": "TEXT", "email_address": "TEXT"}
    
    # Samples as lists of strings/ints
    src_samples = {"cust_id": [1, 2, 3], "fname": ["John", "Jane"], "email": ["a@b.com"]}
    tgt_samples = {"customer_id": [10, 20], "first_name": ["Alice"], "email_address": ["x@y.com"]}

    result = engine.get_gemini_analysis(
        source_columns=source_cols,
        target_columns=target_cols,
        source_table="cust_info",
        target_table="customers",
        source_types=src_types,
        target_types=tgt_types,
        source_samples=src_samples,  # Pass samples
        target_samples=tgt_samples
    )
    
    print("\nResult:")
    print(result)
    
    if not result:
        print("\nFAILURE: Result is empty.")
    else:
        print(f"\nSUCCESS: Got {len(result.get('mappings', []))} mappings.")

except Exception as e:
    print(f"\nCRITICAL FAILURE during analysis: {e}")
