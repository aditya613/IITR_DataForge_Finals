"""
Citation Linker for Hallucination Hunter
Links verified claims to exact source passages with character-level precision.
"""

from typing import List, Dict, Tuple
import re


class CitationLinker:
    """Creates citations linking claims to source document passages."""
    
    def __init__(self):
        """Initialize citation linker."""
        self.citation_counter = 0
    
    def create_citation(self, claim: str, evidence: Dict, claim_index: int) -> Dict:
        """
        Create a citation for a verified claim.
        
        Args:
            claim: The verified claim text
            evidence: Evidence dictionary from verifier
            claim_index: Index of this claim in the document
            
        Returns:
            Citation dictionary with formatting info
        """
        self.citation_counter += 1
        
        citation = {
            "id": f"cite_{self.citation_counter}",
            "claim_index": claim_index,
            "claim_text": claim,
            "source_file": evidence['source'],
            "source_page": evidence['page'],
            "evidence_text": evidence['text'],
            "confidence": evidence['confidence'],
            "citation_number": self.citation_counter
        }
        
        return citation
    
    def generate_citation_footnote(self, citation: Dict) -> str:
        """
        Generate a formatted footnote for a citation.
        
        Args:
            citation: Citation dictionary
            
        Returns:
            Formatted footnote string
        """
        footnote = (
            f"[{citation['citation_number']}] "
            f"{citation['source_file']}, Page {citation['source_page']}: "
            f"\"{citation['evidence_text'][:100]}...\" "
            f"(Confidence: {citation['confidence']:.0%})"
        )
        
        return footnote
    
    def annotate_text_with_citations(self, original_text: str, verification_results: List[Dict]) -> Dict:
        """
        Annotate original text with citation markers and color coding.
        
        Args:
            original_text: The original LLM-generated text
            verification_results: List of claim verification results
            
        Returns:
            Dictionary with annotated text and citation data
        """
        annotations = []
        citations = []
        
        for idx, result in enumerate(verification_results):
            claim_text = result['claim']
            status = result['status']
            
            # Find claim position in original text
            positions = self._find_claim_positions(original_text, claim_text)
            
            for start, end in positions:
                # Create annotation
                annotation = {
                    "start": start,
                    "end": end,
                    "status": status,
                    "confidence": result['confidence'],
                    "explanation": result['explanation'],
                    "claim_index": idx
                }
                
                # Create citation if supported
                if status == "supported" and result.get('evidence'):
                    citation = self.create_citation(claim_text, result['evidence'], idx)
                    citations.append(citation)
                    annotation["citation_id"] = citation['id']
                    annotation["citation_number"] = citation['citation_number']
                
                annotations.append(annotation)
        
        # Sort annotations by start position
        annotations.sort(key=lambda x: x['start'])
        
        return {
            "original_text": original_text,
            "annotations": annotations,
            "citations": citations,
            "citation_footnotes": [self.generate_citation_footnote(c) for c in citations]
        }
    
    def _find_claim_positions(self, text: str, claim: str) -> List[Tuple[int, int]]:
        """
        Find all positions where claim appears in text.
        
        Args:
            text: Text to search in
            claim: Claim to find
            
        Returns:
            List of (start, end) tuples
        """
        positions = []
        
        # Try exact match first
        pattern = re.escape(claim)
        for match in re.finditer(pattern, text, re.IGNORECASE):
            positions.append((match.start(), match.end()))
        
        # If no exact match, try fuzzy matching (find key phrases)
        if not positions:
            # Extract key phrases (5+ words)
            words = claim.split()
            if len(words) >= 5:
                key_phrase = ' '.join(words[:5])
                pattern = re.escape(key_phrase)
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Extend to sentence boundary
                    start = match.start()
                    end = text.find('.', match.end()) + 1
                    if end == 0:  # No period found
                        end = min(match.end() + 100, len(text))
                    positions.append((start, end))
        
        return positions
    
    def generate_html_annotated_text(self, annotated_data: Dict) -> str:
        """
        Generate HTML with color-coded annotations and inline citations.
        
        Args:
            annotated_data: Output from annotate_text_with_citations
            
        Returns:
            HTML string
        """
        text = annotated_data['original_text']
        annotations = annotated_data['annotations']
        
        # Color mapping
        colors = {
            "supported": "#d4edda",  # Green
            "contradicted": "#f8d7da",  # Red
            "unverifiable": "#fff3cd"  # Yellow
        }
        
        # Build HTML with spans
        html_parts = []
        last_pos = 0
        
        for ann in annotations:
            # Add text before annotation
            if ann['start'] > last_pos:
                html_parts.append(text[last_pos:ann['start']])
            
            # Add annotated span
            color = colors.get(ann['status'], "#ffffff")
            citation_marker = f"<sup>[{ann['citation_number']}]</sup>" if 'citation_number' in ann else ""
            
            html_parts.append(
                f'<span class="claim {ann["status"]}" '
                f'style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" '
                f'data-claim-index="{ann["claim_index"]}" '
                f'data-confidence="{ann["confidence"]:.2f}" '
                f'title="{ann["explanation"]}">'
                f'{text[ann["start"]:ann["end"]]}{citation_marker}</span>'
            )
            
            last_pos = ann['end']
        
        # Add remaining text
        if last_pos < len(text):
            html_parts.append(text[last_pos:])
        
        return ''.join(html_parts)


# Example Usage
if __name__ == "__main__":
    linker = CitationLinker()
    
    # Sample verification results
    verification_results = [
        {
            "claim": "The patient has Type 2 Diabetes",
            "status": "supported",
            "confidence": 0.95,
            "evidence": {
                "text": "Patient diagnosed with Type 2 Diabetes mellitus",
                "source": "medical_guidelines.pdf",
                "page": 4,
                "confidence": 0.95
            },
            "explanation": "Supported by evidence on page 4"
        },
        {
            "claim": "was prescribed Metformin",
            "status": "supported",
            "confidence": 0.92,
            "evidence": {
                "text": "First-line medication: Metformin is recommended",
                "source": "medical_guidelines.pdf",
                "page": 4,
                "confidence": 0.92
            },
            "explanation": "Supported by evidence on page 4"
        },
        {
            "claim": "patient should avoid if they have severe liver disease",
            "status": "contradicted",
            "confidence": 0.88,
            "evidence": {
                "text": "Contraindicated in severe kidney disease, not liver disease",
                "source": "medical_guidelines.pdf",
                "page": 4,
                "confidence": 0.88
            },
            "explanation": "Contradicts evidence - should be kidney, not liver"
        }
    ]
    
    original_text = """
    The patient has Type 2 Diabetes and was prescribed Metformin.
    The patient should avoid taking Metformin if they have severe liver disease.
    """
    
    # Generate annotations
    annotated_data = linker.annotate_text_with_citations(original_text, verification_results)
    
    print("=== ANNOTATIONS ===")
    print(f"Found {len(annotated_data['annotations'])} annotations")
    print(f"Generated {len(annotated_data['citations'])} citations\n")
    
    print("=== CITATIONS ===")
    for footnote in annotated_data['citation_footnotes']:
        print(footnote)
    
    print("\n=== HTML OUTPUT ===")
    html = linker.generate_html_annotated_text(annotated_data)
    print(html)
