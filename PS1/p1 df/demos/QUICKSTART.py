"""
QUICK START GUIDE - Hallucination Hunter
=========================================

This guide will help you run the Hallucination Hunter model step-by-step.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║           HALLUCINATION HUNTER - Quick Start Guide                   ║
╔══════════════════════════════════════════════════════════════════════╗

STEP 1: Make sure dependencies are installed
---------------------------------------------
Run this command:
    pip install --only-binary :all: sentence-transformers chromadb transformers torch

Or use the setup script:
    setup.bat


STEP 2: Run the complete pipeline
----------------------------------
Option A - Simple CLI Interface:
    python pipeline.py

    This will:
    1. Ask if you want to ingest a PDF (press Enter for default)
    2. Wait for you to paste LLM text to verify
    3. Generate results in verification_results.json
    4. Create annotated_output.html (open in browser!)


Option B - Python Script:
""")

print("""
from pipeline import HallucinationHunter

# Initialize
hunter = HallucinationHunter()

# Ingest source documents
hunter.ingest_source_documents(["medical_guidelines.pdf"])

# Verify LLM output
llm_text = \"\"\"
The patient has Type 2 Diabetes and was prescribed Metformin.
\"\"\"

results = hunter.verify_llm_output(llm_text)
hunter.print_summary(results)
""")

print("""

STEP 3: Start the API Server (Optional)
----------------------------------------
    python api.py
    
Then open: http://localhost:8000/docs


OUTPUT FILES:
-------------
- verification_results.json  - Complete results
- annotated_output.html      - Color-coded visualization (OPEN THIS!)
- chroma_db/                 - Vector database


EXAMPLE RUN:
------------
> python pipeline.py

Do you want to ingest source documents? (y/n): y
Enter PDF path: medical_guidelines.pdf

Enter LLM-generated text to verify:
The patient has Type 2 Diabetes and was prescribed Metformin.
[Press Enter on empty line]

[Processing...]

Trust Score: 100.0% ⭐
Total Claims: 2
  ✓ Supported: 2 (100.0%)

Done! Open annotated_output.html in your browser.


TROUBLESHOOTING:
----------------
1. If dependencies fail to install:
   - Use: pip install --only-binary :all: [package_name]
   - Or install one at a time

2. If models don't download:
   - Check internet connection
   - Models auto-download on first run (~500MB)

3. If you get import errors:
   - Run: python test_system.py
   - This will verify all components

""")

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("Ready to run? Choose an option:")
    print("="*70)
    print("1. Run complete pipeline (python pipeline.py)")
    print("2. Run test suite (python test_system.py)")
    print("3. Start API server (python api.py)")
    print("\nPress Ctrl+C to exit, or just run one of the commands above!")
    print("="*70)
