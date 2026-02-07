"""
Correction Engine for Hallucination Hunter
Suggests corrections for contradicted claims based on source evidence.
"""

from typing import Dict, List, Optional
import re


class CorrectionEngine:
    """Generates correction suggestions for hallucinated claims."""
    
    def suggest_correction(self, claim: str, evidence: Dict, status: str) -> Optional[Dict]:
        """
        Generate a correction suggestion for a claim.
        
        Args:
            claim: The original claim
            evidence: Evidence from source documents
            status: Verification status
            
        Returns:
            Correction dictionary or None if not applicable
        """
        if status != "contradicted":
            return None
        
        # Extract the corrected information from evidence
        evidence_text = evidence.get('text', '')
        
        # Extract only the most relevant sentence instead of the whole paragraph
        corrected_sentence = self._extract_relevant_sentence(claim, evidence_text)
        
        correction = {
            "original_claim": claim,
            "suggested_correction": corrected_sentence,
            "source": evidence.get('source', 'Unknown'),
            "page": evidence.get('page', 'Unknown'),
            "explanation": self._generate_explanation(claim, corrected_sentence),
            "confidence": evidence.get('confidence', 0.0)
        }
        
        return correction
    
    def _extract_relevant_sentence(self, claim: str, evidence: str) -> str:
        """
        Extract the most relevant sentence from evidence text.
        
        Args:
            claim: The original claim
            evidence: Full evidence text (may be multiple sentences)
            
        Returns:
            Most relevant sentence from evidence
        """
        # Split evidence into sentences
        sentences = re.split(r'[.!?]+', evidence)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return evidence
        
        # If only one sentence, return it
        if len(sentences) == 1:
            return sentences[0]
        
        # Extract key words from claim (excluding common words)
        claim_lower = claim.lower()
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 
                       'to', 'for', 'of', 'and', 'or', 'but', 'with', 'by', 'from'}
        claim_words = set(word.strip('.,!?()[]{}') for word in claim_lower.split())
        claim_words -= common_words
        
        # Score each sentence by word overlap with claim
        best_sentence = sentences[0]
        best_score = 0
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count matching words
            score = sum(1 for word in claim_words if word in sentence_lower)
            
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        return best_sentence
    
    def _generate_explanation(self, original: str, corrected: str) -> str:
        """
        Generate a human-readable explanation of the correction.
        
        Args:
            original: Original claim text
            corrected: Corrected text from source
            
        Returns:
            Explanation string
        """
        explanation = (
            f"The claim states: \"{original[:100]}{'...' if len(original) > 100 else ''}\"\n\n"
            f"However, the source document states: \"{corrected[:100]}{'...' if len(corrected) > 100 else ''}\"\n\n"
            f"Please revise the claim to match the source document."
        )
        
        return explanation
    
    def generate_correction_report(self, verification_results: List[Dict]) -> Dict:
        """
        Generate a comprehensive correction report for all contradicted claims.
        
        Args:
            verification_results: List of claim verification results
            
        Returns:
            Correction report dictionary
        """
        corrections = []
        
        for result in verification_results:
            if result['status'] == 'contradicted' and result.get('evidence'):
                correction = self.suggest_correction(
                    result['claim'],
                    result['evidence'],
                    result['status']
                )
                if correction:
                    corrections.append(correction)
        
        report = {
            "total_contradictions": len(corrections),
            "corrections": corrections,
            "summary": self._generate_summary(corrections)
        }
        
        return report
    
    def _generate_summary(self, corrections: List[Dict]) -> str:
        """Generate a summary of all corrections."""
        if not corrections:
            return "No contradictions found. All claims are either supported or unverifiable."
        
        summary = f"Found {len(corrections)} contradicted claim(s) that require correction:\n\n"
        
        for i, corr in enumerate(corrections, 1):
            summary += (
                f"{i}. {corr['original_claim'][:80]}...\n"
                f"   Source: {corr['source']}, Page {corr['page']}\n"
                f"   Suggested correction available.\n\n"
            )
        
        return summary
    
    def generate_corrected_document(self, original_text: str, corrections: List[Dict]) -> str:
        """
        Generate a corrected version of the document.
        
        Args:
            original_text: Original text with hallucinations
            corrections: List of corrections to apply
            
        Returns:
            Corrected text
        """
        corrected_text = original_text
        
        # Sort corrections by length to avoid replacement conflicts
        sorted_corrections = sorted(corrections, key=lambda x: len(x['original_claim']), reverse=True)
        
        for correction in sorted_corrections:
            original = correction['original_claim']
            suggested = correction['suggested_correction']
            
            # Replace in text (case-insensitive)
            import re
            pattern = re.compile(re.escape(original), re.IGNORECASE)
            corrected_text = pattern.sub(suggested, corrected_text, count=1)
        
        return corrected_text


# Example Usage
if __name__ == "__main__":
    engine = CorrectionEngine()
    
    # Sample verification results
    verification_results = [
        {
            "claim": "Metformin is contraindicated in severe liver disease",
            "status": "contradicted",
            "confidence": 0.88,
            "evidence": {
                "text": "Severe kidney disease (eGFR < 30 mL/min/1.73 m²) is a contraindication for Metformin",
                "source": "medical_guidelines.pdf",
                "page": 4,
                "confidence": 0.88
            },
            "explanation": "Contradicts source evidence"
        },
        {
            "claim": "Patient has Type 2 Diabetes",
            "status": "supported",
            "confidence": 0.95,
            "evidence": {},
            "explanation": "Supported"
        }
    ]
    
    # Generate correction report
    report = engine.generate_correction_report(verification_results)
    
    print("=== CORRECTION REPORT ===")
    print(report['summary'])
    
    print("\n=== DETAILED CORRECTIONS ===")
    for i, correction in enumerate(report['corrections'], 1):
        print(f"\nCorrection {i}:")
        print(f"Original: {correction['original_claim']}")
        print(f"Suggested: {correction['suggested_correction']}")
        print(f"Source: {correction['source']}, Page {correction['page']}")
        print(f"Confidence: {correction['confidence']:.0%}")
    
    # Generate corrected document
    original_doc = "Metformin is contraindicated in severe liver disease. Patient has Type 2 Diabetes."
    corrected_doc = engine.generate_corrected_document(original_doc, report['corrections'])
    
    print("\n=== DOCUMENT COMPARISON ===")
    print(f"Original: {original_doc}")
    print(f"Corrected: {corrected_doc}")
