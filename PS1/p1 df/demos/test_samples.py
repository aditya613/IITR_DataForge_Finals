"""
Test Samples for Hallucination Hunter
Contains LLM outputs with intentional hallucinations for testing across different domains.

USAGE:
1. Run: python demos/test_samples.py
2. This will ingest source documents and test each LLM output
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# CLIMATE SCIENCE - Test with climate_science.txt
# ============================================================================

CLIMATE_LLM_OUTPUT_1 = """
According to recent climate data, the global average temperature has increased 
by approximately 1.1 degrees Celsius since the pre-industrial era. This warming 
is primarily driven by human activities, especially the burning of fossil fuels.

Atmospheric CO2 levels have risen dramatically - from 280 ppm in pre-industrial 
times to about 420 ppm today, representing a 50% increase. However, methane has 
only 20x the warming potential of CO2 over 20 years, making it a lesser concern.

Sea levels have risen by approximately 21-24 centimeters since 1880, with the 
current rate of rise at 3.7 mm per year.
"""
# HALLUCINATION: Methane actually has 80x warming potential, not 20x

CLIMATE_LLM_OUTPUT_2 = """
The Arctic is experiencing dramatic changes due to climate change. Sea ice extent 
has declined by approximately 13% per decade since 1979, and scientists predict 
the Arctic could experience ice-free summers by 2100 under current trends.

Renewable energy is making progress - solar and wind now account for approximately 
25% of global electricity generation. The cost of solar panels has dropped by 99% 
since 1976, making them increasingly competitive with fossil fuels.
"""
# HALLUCINATIONS: 
# 1. Ice-free summers predicted by 2050, not 2100
# 2. Solar/wind account for 12% of generation, not 25%


# ============================================================================
# TECHNOLOGY - Test with tech_specs.txt
# ============================================================================

TECH_LLM_OUTPUT_1 = """
GPT-4 was released in March 2023 by OpenAI and represents a major advancement 
in AI. The model uses a transformer architecture and has an estimated 1.7 trillion 
parameters, making it one of the largest language models ever created.

In quantum computing, IBM's Condor processor achieved an impressive 1,121 qubits 
in December 2023. Google's Sycamore processor, which has 72 qubits, demonstrated 
quantum supremacy in 2019.

The NVIDIA H100 GPU is the current standard for AI training, featuring 80GB of 
HBM3 memory and delivering 3,958 TFLOPS of FP8 performance.
"""
# HALLUCINATION: Google's Sycamore has 53 qubits, not 72

TECH_LLM_OUTPUT_2 = """
Modern battery technology continues to advance rapidly. Lithium-ion batteries 
have an energy density of approximately 250-300 Wh/kg, while solid-state batteries 
promise energy densities exceeding 400 Wh/kg.

5G networks offer impressive performance with peak speeds up to 10 Gbps and 
latency as low as 1ms. Starlink satellites provide global internet coverage 
from their orbit at approximately 1,200 km altitude.

Semiconductor manufacturing has reached the 3nm process node at TSMC, using 
EUV lithography with 13.5nm wavelength light for extreme precision.
"""
# HALLUCINATIONS:
# 1. 5G offers up to 20 Gbps, not 10 Gbps
# 2. Starlink satellites orbit at 550 km, not 1,200 km


# ============================================================================
# HISTORY - Test with history_facts.txt
# ============================================================================

HISTORY_LLM_OUTPUT_1 = """
The Great Pyramid of Giza was built around 2560 BCE for Pharaoh Khufu and 
remains one of the ancient world's most impressive structures. The Roman 
Empire officially fell in 476 CE when the last emperor Romulus Augustulus 
was deposed by Germanic forces.

The Black Death was devastating, killing approximately 75-200 million people 
between 1346-1353. The Magna Carta, a foundational document for constitutional 
law, was signed in 1225 CE by King John of England.
"""
# HALLUCINATION: Magna Carta was signed in 1215, not 1225

HISTORY_LLM_OUTPUT_2 = """
World War I lasted from 1914 to 1918 and resulted in approximately 17 million 
deaths. World War II was even more devastating, lasting from 1939 to 1945 with 
70-85 million deaths. D-Day, the famous Allied invasion of Normandy, France, 
occurred on June 6, 1944.

In space exploration, the first human in space was Yuri Gagarin on April 12, 1961. 
Neil Armstrong became the first person to walk on the Moon on July 20, 1969, 
during the Apollo 13 mission which launched from Kennedy Space Center in Florida.

The Berlin Wall fell on November 9, 1989, and the Soviet Union dissolved on 
December 26, 1991.
"""
# HALLUCINATION: Apollo 11 mission, not Apollo 13


# ============================================================================
# MULTI-DOMAIN TEST - Mix of topics
# ============================================================================

MIXED_LLM_OUTPUT = """
Here are some interesting facts across different domains:

Technology: The NVIDIA H100 uses TSMC's 4nm process node and delivers impressive 
AI performance. TSMC now produces chips at the 3nm node as of 2024.

Climate: Global temperatures have risen by 1.1 degrees Celsius, and Arctic ice 
is declining at 8% per decade. Sea levels continue to rise at 3.7mm per year.

History: The first Moon landing happened on July 20, 1969 with Neil Armstrong. 
Yuri Gagarin became the first human in space on March 12, 1961.
"""
# HALLUCINATIONS:
# 1. Arctic ice declining at 13% per decade, not 8%
# 2. Yuri Gagarin's flight was April 12, not March 12


# ============================================================================
# TEST CASES
# ============================================================================

def get_all_test_cases():
    """Returns all test cases as a list of tuples (name, llm_output, source_file, expected_hallucinations)"""
    return [
        ("Climate Science 1", CLIMATE_LLM_OUTPUT_1, "data/climate_science.txt", 
         ["Methane warming potential: states 20x, should be 80x"]),
        
        ("Climate Science 2", CLIMATE_LLM_OUTPUT_2, "data/climate_science.txt",
         ["Ice-free Arctic: states 2100, should be 2050", 
          "Renewable percentage: states 25%, should be 12%"]),
        
        ("Technology 1", TECH_LLM_OUTPUT_1, "data/tech_specs.txt",
         ["Sycamore qubits: states 72, should be 53"]),
        
        ("Technology 2", TECH_LLM_OUTPUT_2, "data/tech_specs.txt",
         ["5G speed: states 10 Gbps, should be 20 Gbps",
          "Starlink altitude: states 1,200 km, should be 550 km"]),
        
        ("History 1", HISTORY_LLM_OUTPUT_1, "data/history_facts.txt",
         ["Magna Carta year: states 1225, should be 1215"]),
        
        ("History 2", HISTORY_LLM_OUTPUT_2, "data/history_facts.txt",
         ["Apollo mission: states Apollo 13, should be Apollo 11"]),
        
        ("Mixed Domain", MIXED_LLM_OUTPUT, "all",
         ["Arctic ice decline: states 8%, should be 13%",
          "Gagarin date: states March 12, should be April 12"]),
    ]


def run_verification_tests():
    """Run verification tests using the Hallucination Hunter system."""
    from core.embedding_engine import EmbeddingEngine
    from core.claim_verifier import ClaimVerifier
    from core.ingestion import atomize_claims
    
    print("=" * 70)
    print("HALLUCINATION HUNTER - AUTOMATED TEST SUITE")
    print("=" * 70)
    
    # Initialize components
    print("\n📦 Initializing components...")
    engine = EmbeddingEngine()
    verifier = ClaimVerifier()
    
    # Clear existing data for fresh test
    print("🗑️  Clearing existing knowledge base...")
    engine.clear_collection()
    
    # Ingest all source documents
    print("\n📄 Ingesting source documents...")
    source_files = [
        "data/climate_science.txt",
        "data/tech_specs.txt", 
        "data/history_facts.txt"
    ]
    
    for source in source_files:
        if os.path.exists(source):
            engine.ingest_text_file(source)
        else:
            print(f"   ⚠️  Source file not found: {source}")
    
    print(f"\n✅ Knowledge base ready with {engine.collection.count()} chunks")
    
    # Run tests
    print("\n" + "=" * 70)
    print("RUNNING VERIFICATION TESTS")
    print("=" * 70)
    
    test_cases = get_all_test_cases()
    
    for name, llm_output, source, expected_hallucinations in test_cases:
        if source == "all":
            continue  # Skip mixed domain for now
            
        print(f"\n📋 Test Case: {name}")
        print("-" * 50)
        
        # Atomize claims
        claims = atomize_claims(llm_output)
        print(f"   Claims identified: {len(claims)}")
        
        # Verify each claim
        supported = 0
        contradicted = 0
        unverifiable = 0
        
        for claim in claims:
            # Get evidence
            evidence = engine.search_similar(claim, top_k=3)
            
            if evidence and evidence[0]['score'] > 0.3:
                # Verify with NLI
                result = verifier.verify_claim(claim, evidence[0]['text'])
                
                if result['verdict'] == 'supported':
                    supported += 1
                elif result['verdict'] == 'contradicted':
                    contradicted += 1
                    print(f"   ❌ Contradicted: {claim[:60]}...")
                else:
                    unverifiable += 1
            else:
                unverifiable += 1
        
        print(f"\n   Results: ✓ {supported} supported, ✗ {contradicted} contradicted, ? {unverifiable} unverifiable")
        print(f"   Expected hallucinations: {len(expected_hallucinations)}")
        for h in expected_hallucinations:
            print(f"      → {h}")
    
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hallucination Hunter Test Suite")
    parser.add_argument("--run", action="store_true", help="Run automated verification tests")
    parser.add_argument("--list", action="store_true", help="List all test cases")
    args = parser.parse_args()
    
    if args.run:
        run_verification_tests()
    elif args.list:
        print("=" * 70)
        print("HALLUCINATION HUNTER - TEST SAMPLES")
        print("=" * 70)
        
        for name, output, source, hallucinations in get_all_test_cases():
            print(f"\n📋 Test Case: {name}")
            print(f"   Source: {source}")
            print(f"   Expected Hallucinations: {len(hallucinations)}")
            for h in hallucinations:
                print(f"      ❌ {h}")
    else:
        print("Usage:")
        print("  python demos/test_samples.py --list    # List all test cases")
        print("  python demos/test_samples.py --run     # Run verification tests")
        print("\nOr import from this module:")
        print("  from demos.test_samples import CLIMATE_LLM_OUTPUT_1, get_all_test_cases")
