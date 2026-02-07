"""
Complete End-to-End Pipeline for Hallucination Hunter
Integrates all components into a single verification system.
"""

import sys
from ingestion import atomize_claims, ingest_pdf
from embedding_engine import EmbeddingEngine
from claim_verifier import ClaimVerifier
from citation_linker import CitationLinker
from correction_engine import CorrectionEngine
import json


class HallucinationHunter:
    """Main pipeline orchestrator for the Hallucination Hunter system."""
    
    def __init__(self):
        """Initialize all components."""
        print("="*70)
        print("HALLUCINATION HUNTER - Initializing...")
        print("="*70)
        
        print("\n[1/4] Loading embedding engine...")
        self.embedding_engine = EmbeddingEngine()
        
        print("\n[2/4] Loading NLI verifier...")
        self.claim_verifier = ClaimVerifier()
        
        print("\n[3/4] Initializing citation linker...")
        self.citation_linker = CitationLinker()
        
        print("\n[4/4] Initializing correction engine...")
        self.correction_engine = CorrectionEngine()
        
        print("\n" + "="*70)
        print("HALLUCINATION HUNTER - Ready!")
        print("="*70 + "\n")
    
    def ingest_source_documents(self, pdf_paths: list):
        """
        Ingest source documents into the knowledge base.
        
        Args:
            pdf_paths: List of paths to PDF files
        """
        print(f"\nIngesting {len(pdf_paths)} source document(s)...")
        for pdf_path in pdf_paths:
            self.embedding_engine.ingest_pdf(pdf_path)
    
    def verify_llm_output(self, llm_text: str, output_file: str = None) -> dict:
        """
        Complete verification pipeline for LLM-generated text.
        
        Args:
            llm_text: The LLM-generated text to verify
            output_file: Optional path to save results as JSON
            
        Returns:
            Complete verification results
        """
        print("\n" + "="*70)
        print("VERIFICATION PIPELINE - Starting")
        print("="*70)
        
        # Step 1: Atomize claims
        print("\n[Step 1/5] Atomizing claims...")
        claims = atomize_claims(llm_text)
        print(f"  -> Extracted {len(claims)} atomic claims")
        
        # Step 2: Verify claims
        print("\n[Step 2/5] Verifying claims against source documents...")
        verification_results = self.claim_verifier.verify_document(claims)
        
        # Step 3: Generate citations
        print("\n[Step 3/5] Generating citations...")
        annotated_data = self.citation_linker.annotate_text_with_citations(
            llm_text,
            verification_results['claims']
        )
        print(f"  -> Generated {len(annotated_data['citations'])} citation(s)")
        
        # Step 4: Generate corrections
        print("\n[Step 4/5] Generating corrections...")
        correction_report = self.correction_engine.generate_correction_report(
            verification_results['claims']
        )
        print(f"  -> Found {correction_report['total_contradictions']} contradiction(s)")
        
        # Step 5: Generate annotated HTML
        print("\n[Step 5/5] Generating annotated HTML...")
        annotated_html = self.citation_linker.generate_html_annotated_text(annotated_data)
        
        # Compile results
        results = {
            "original_text": llm_text,
            "claims": verification_results['claims'],
            "statistics": verification_results['statistics'],
            "trust_score": verification_results['trust_score'],
            "annotations": annotated_data['annotations'],
            "citations": annotated_data['citations'],
            "citation_footnotes": annotated_data['citation_footnotes'],
            "corrections": correction_report['corrections'],
            "annotated_html": annotated_html
        }
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Exclude HTML for JSON serialization
                json_results = {k: v for k, v in results.items() if k != 'annotated_html'}
                json.dump(json_results, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Results saved to: {output_file}")
        
        print("\n" + "="*70)
        print("VERIFICATION PIPELINE - Complete")
        print("="*70)
        
        return results
    
    def print_summary(self, results: dict):
        """Print a human-readable summary of verification results."""
        stats = results['statistics']
        
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        
        print(f"\nTrust Score: {results['trust_score']:.1%} *")
        print(f"\nTotal Claims: {stats['total']}")
        print(f"  [OK] Supported: {stats['supported']} ({stats['supported']/stats['total']*100:.1f}%)")
        print(f"  [X] Contradicted: {stats['contradicted']} ({stats['contradicted']/stats['total']*100:.1f}%)")
        print(f"  ? Unverifiable: {stats['unverifiable']} ({stats['unverifiable']/stats['total']*100:.1f}%)")
        
        # Show contradictions
        if stats['contradicted'] > 0:
            print("\n" + "="*70)
            print("HALLUCINATIONS DETECTED")
            print("="*70)
            
            for i, claim_result in enumerate(results['claims']):
                if claim_result['status'] == 'contradicted':
                    print(f"\n[X] Claim: {claim_result['claim']}")
                    print(f"  Issue: {claim_result['explanation']}")
                    if claim_result.get('evidence'):
                        print(f"  Evidence: {claim_result['evidence']['text'][:100]}...")
        
        # Show citations
        if results['citations']:
            print("\n" + "="*70)
            print("CITATIONS")
            print("="*70)
            for footnote in results['citation_footnotes'][:5]:  # Show first 5
                print(f"\n{footnote}")
        
        print("\n" + "="*70)


# Main execution
def main():
    """Main function for command-line usage."""
    
    # Initialize the system
    hunter = HallucinationHunter()
    
    # Ingest source documents
    print("\nDo you want to ingest source documents? (y/n): ", end='')
    if input().lower() == 'y':
        print("Enter PDF path (or press Enter to use default 'medical_guidelines.pdf'): ", end='')
        pdf_path = input().strip() or "medical_guidelines.pdf"
        hunter.ingest_source_documents([pdf_path])
    
    # Get LLM output to verify
    print("\n" + "="*70)
    print("Enter LLM-generated text to verify (end with empty line):")
    print("="*70)
    
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    
    llm_text = '\n'.join(lines)
    
    if not llm_text.strip():
        # Use example text
        llm_text = """
        The patient has Type 2 Diabetes and was prescribed Metformin.
        The starting dose is 500mg twice daily.
        Metformin can cause vitamin B12 deficiency with long-term use.
        The patient should avoid Metformin if they have severe liver disease.
        """
        print(f"\nUsing example text:\n{llm_text}")
    
    # Run verification
    results = hunter.verify_llm_output(llm_text, output_file="verification_results.json")
    
    # Print summary
    hunter.print_summary(results)
    
    # Save HTML
    with open("annotated_output.html", "w", encoding="utf-8") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Hallucination Hunter - Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .supported {{ background-color: #d4edda; padding: 2px 4px; border-radius: 3px; }}
        .contradicted {{ background-color: #f8d7da; padding: 2px 4px; border-radius: 3px; }}
        .unverifiable {{ background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }}
        .legend {{ margin: 20px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        .legend span {{ margin-right: 20px; padding: 5px 10px; border-radius: 3px; }}
        sup {{ color: #007bff; cursor: pointer; }}
    </style>
</head>
<body>
    <h1>Hallucination Hunter - Verification Results</h1>
    <div class="legend">
        <strong>Legend:</strong>
        <span class="supported">Supported</span>
        <span class="contradicted">Contradicted</span>
        <span class="unverifiable">Unverifiable</span>
    </div>
    <div class="content">
        {results['annotated_html']}
    </div>
    <h2>Trust Score: {results['trust_score']:.1%}</h2>
    <h3>Citations</h3>
    <ol>
        {"".join(f"<li>{footnote}</li>" for footnote in results['citation_footnotes'])}
    </ol>
</body>
</html>
        """)
    
    print("\n[OK] Annotated HTML saved to: annotated_output.html")
    print("\nOpen 'annotated_output.html' in your browser to see the results!")


if __name__ == "__main__":
    main()
