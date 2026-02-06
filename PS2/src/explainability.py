"""
=============================================================================
MODULE 6: EXPLAINABILITY ENGINE
=============================================================================
Purpose: Generate human-readable explanations for all system decisions
Features:
    - Mapping explanations (why column A maps to B)
    - Transformation explanations (why conversion is needed)
    - Validation explanations (why check failed/passed)
    - Recommendation generation
    - Natural language report generation
=============================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class ExplanationType(Enum):
    """Types of explanations"""
    MAPPING = "mapping"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"


@dataclass
class Explanation:
    """A single explanation item"""
    type: ExplanationType
    title: str
    summary: str
    details: List[str] = field(default_factory=list)
    evidence: Dict = field(default_factory=dict)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "title": self.title,
            "summary": self.summary,
            "details": self.details,
            "evidence": self.evidence,
            "confidence": self.confidence
        }
    
    def to_markdown(self) -> str:
        """Generate markdown representation"""
        md = f"### {self.title}\n\n"
        md += f"**{self.summary}**\n\n"
        
        if self.details:
            md += "**Details:**\n"
            for detail in self.details:
                md += f"- {detail}\n"
            md += "\n"
        
        if self.evidence:
            md += "**Evidence:**\n"
            md += f"```json\n{json.dumps(self.evidence, indent=2)}\n```\n"
        
        return md


class ExplainabilityEngine:
    """
    Generate explanations for all system decisions
    """
    
    def __init__(self):
        self.explanations: List[Explanation] = []
    
    def explain_column_mapping(self,
                               source_col: str,
                               target_col: str,
                               semantic_score: float,
                               syntactic_score: float,
                               type_score: float,
                               source_type: str,
                               target_type: str,
                               overall_score: float) -> Explanation:
        """
        Generate explanation for why two columns were matched
        """
        details = []
        
        # Semantic explanation
        if semantic_score >= 0.8:
            details.append(
                f"✅ Strong semantic similarity ({semantic_score:.0%}): "
                f"The column names have similar meanings"
            )
        elif semantic_score >= 0.6:
            details.append(
                f"✓ Moderate semantic similarity ({semantic_score:.0%}): "
                f"The columns appear to represent related concepts"
            )
        elif semantic_score >= 0.4:
            details.append(
                f"⚠ Weak semantic similarity ({semantic_score:.0%}): "
                f"Limited semantic relationship detected"
            )
        else:
            details.append(
                f"❌ Low semantic similarity ({semantic_score:.0%}): "
                f"Names don't appear semantically related"
            )
        
        # Syntactic explanation  
        if syntactic_score >= 0.8:
            details.append(
                f"✅ Names are very similar ({syntactic_score:.0%}): "
                f"'{source_col}' closely matches '{target_col}'"
            )
        elif syntactic_score >= 0.6:
            details.append(
                f"✓ Names are somewhat similar ({syntactic_score:.0%}): "
                f"Possibly abbreviations or variations"
            )
        else:
            details.append(
                f"ℹ Names differ significantly ({syntactic_score:.0%}): "
                f"Matched primarily on meaning, not spelling"
            )
        
        # Type explanation
        if type_score >= 1.0:
            details.append(
                f"✅ Exact type match: Both are {source_type}"
            )
        elif type_score >= 0.8:
            details.append(
                f"✓ Compatible types: {source_type} → {target_type} "
                f"(safe conversion)"
            )
        elif type_score >= 0.6:
            details.append(
                f"⚠ Type conversion needed: {source_type} → {target_type} "
                f"(review recommended)"
            )
        else:
            details.append(
                f"❌ Type mismatch: {source_type} → {target_type} "
                f"(manual review required)"
            )
        
        # Overall assessment
        if overall_score >= 0.85:
            summary = f"High confidence match ({overall_score:.0%})"
            title = f"✅ {source_col} → {target_col}"
        elif overall_score >= 0.6:
            summary = f"Moderate confidence match ({overall_score:.0%}) - Review recommended"
            title = f"⚠ {source_col} → {target_col}"
        else:
            summary = f"Low confidence match ({overall_score:.0%}) - Manual verification needed"
            title = f"❓ {source_col} → {target_col}"
        
        explanation = Explanation(
            type=ExplanationType.MAPPING,
            title=title,
            summary=summary,
            details=details,
            evidence={
                "source_column": source_col,
                "target_column": target_col,
                "scores": {
                    "semantic": round(semantic_score, 3),
                    "syntactic": round(syntactic_score, 3),
                    "type_compatibility": round(type_score, 3),
                    "overall": round(overall_score, 3)
                },
                "types": {
                    "source": source_type,
                    "target": target_type
                }
            },
            confidence=overall_score
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def explain_transformation(self,
                               source_type: str,
                               target_type: str,
                               transformation_type: str,
                               is_lossy: bool) -> Explanation:
        """
        Generate explanation for data type transformation
        """
        details = []
        
        if transformation_type == "direct":
            summary = "No transformation needed - types are compatible"
            details.append(f"Source type ({source_type}) matches target type ({target_type})")
            
        elif transformation_type == "implicit":
            summary = "Safe implicit conversion will be applied"
            details.append(f"Converting {source_type} → {target_type}")
            details.append("This is a widening conversion and no data will be lost")
            
        elif transformation_type == "explicit":
            summary = "Explicit conversion required"
            details.append(f"Must explicitly convert {source_type} → {target_type}")
            details.append("A SQL CAST or transformation function will be applied")
            
        elif transformation_type == "lossy":
            summary = "⚠ Potentially lossy conversion"
            details.append(f"Converting {source_type} → {target_type} may lose data")
            if "FLOAT" in source_type and "INT" in target_type:
                details.append("Decimal values will be truncated")
            if "TEXT" in source_type and "VARCHAR" in target_type:
                details.append("Long text may be truncated")
            if "DATETIME" in source_type and "DATE" in target_type:
                details.append("Time component will be lost")
        else:
            summary = "Unknown transformation - manual review required"
            details.append(f"No predefined rule for {source_type} → {target_type}")
        
        if is_lossy:
            details.append("⚠ RECOMMENDATION: Verify sample data before migration")
        
        explanation = Explanation(
            type=ExplanationType.TRANSFORMATION,
            title=f"Transform: {source_type} → {target_type}",
            summary=summary,
            details=details,
            evidence={
                "source_type": source_type,
                "target_type": target_type,
                "transformation_type": transformation_type,
                "is_lossy": is_lossy
            }
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def explain_validation_failure(self,
                                   check_name: str,
                                   failure_reason: str,
                                   details: Dict) -> Explanation:
        """
        Generate explanation for why a validation failed
        """
        explanation_details = [failure_reason]
        recommendations = []
        
        if "null" in check_name.lower():
            explanation_details.append(
                f"Found {details.get('null_count', 'unknown')} NULL values"
            )
            recommendations.append("Consider adding default values")
            recommendations.append("Verify if NULLs are expected in target schema")
            
        elif "duplicate" in check_name.lower():
            explanation_details.append(
                f"Found {details.get('duplicate_count', 'unknown')} duplicate records"
            )
            recommendations.append("Remove or merge duplicate records")
            recommendations.append("Review primary key definition")
            
        elif "referential" in check_name.lower():
            explanation_details.append(
                f"Found {details.get('orphan_count', 'unknown')} orphaned records"
            )
            recommendations.append("Ensure parent records exist before migration")
            recommendations.append("Consider ON DELETE CASCADE settings")
            
        elif "row count" in check_name.lower():
            explanation_details.append(
                f"Source: {details.get('source_count', '?')}, "
                f"Target: {details.get('target_count', '?')}"
            )
            recommendations.append("Check migration filters")
            recommendations.append("Verify no records were skipped")
        
        explanation = Explanation(
            type=ExplanationType.VALIDATION,
            title=f"❌ {check_name} Failed",
            summary=failure_reason,
            details=explanation_details + [f"💡 {r}" for r in recommendations],
            evidence=details
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def generate_recommendations(self,
                                 mappings: List[Dict],
                                 validation_results: List[Dict]) -> List[Explanation]:
        """
        Generate overall recommendations based on analysis
        """
        recommendations = []
        
        # Check for low-confidence mappings
        low_conf_mappings = [m for m in mappings if m.get('overall_score', 1) < 0.6]
        if low_conf_mappings:
            rec = Explanation(
                type=ExplanationType.RECOMMENDATION,
                title="Review Low-Confidence Mappings",
                summary=f"Found {len(low_conf_mappings)} mapping(s) with low confidence",
                details=[
                    f"• {m.get('source_column')} → {m.get('target_column')} "
                    f"({m.get('overall_score', 0):.0%})"
                    for m in low_conf_mappings[:5]
                ],
                evidence={"count": len(low_conf_mappings)}
            )
            recommendations.append(rec)
        
        # Check for failed validations
        failed_validations = [v for v in validation_results if v.get('status') == 'failed']
        if failed_validations:
            rec = Explanation(
                type=ExplanationType.WARNING,
                title="⚠ Address Validation Failures Before Migration",
                summary=f"Found {len(failed_validations)} validation failure(s)",
                details=[
                    f"• {v.get('check_name')}: {v.get('message')}"
                    for v in failed_validations
                ],
                evidence={"failed_checks": [v.get('check_name') for v in failed_validations]}
            )
            recommendations.append(rec)
        
        # General recommendations
        if mappings:
            rec = Explanation(
                type=ExplanationType.RECOMMENDATION,
                title="Pre-Migration Checklist",
                summary="Recommended steps before executing migration",
                details=[
                    "1. Review all column mappings, especially low-confidence ones",
                    "2. Verify data type transformations won't cause data loss",
                    "3. Ensure target schema is created and matches expected structure",
                    "4. Create backup of target database",
                    "5. Test migration on subset of data first",
                    "6. Plan for rollback in case of issues"
                ]
            )
            recommendations.append(rec)
        
        self.explanations.extend(recommendations)
        return recommendations
    
    def generate_report(self, 
                       format: str = "markdown",
                       include_evidence: bool = True) -> str:
        """
        Generate a complete explanation report
        """
        if format == "markdown":
            return self._generate_markdown_report(include_evidence)
        elif format == "json":
            return json.dumps([e.to_dict() for e in self.explanations], indent=2)
        elif format == "text":
            return self._generate_text_report()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_markdown_report(self, include_evidence: bool) -> str:
        """Generate markdown format report"""
        sections = {
            ExplanationType.MAPPING: ("## Column Mappings\n\n", []),
            ExplanationType.TRANSFORMATION: ("## Data Transformations\n\n", []),
            ExplanationType.VALIDATION: ("## Validation Results\n\n", []),
            ExplanationType.RECOMMENDATION: ("## Recommendations\n\n", []),
            ExplanationType.WARNING: ("## ⚠ Warnings\n\n", [])
        }
        
        for exp in self.explanations:
            sections[exp.type][1].append(exp)
        
        report = "# Migration Analysis Report\n\n"
        
        for exp_type, (header, explanations) in sections.items():
            if explanations:
                report += header
                for exp in explanations:
                    report += f"### {exp.title}\n\n"
                    report += f"**{exp.summary}**\n\n"
                    if exp.details:
                        for detail in exp.details:
                            report += f"- {detail}\n"
                        report += "\n"
                    if include_evidence and exp.evidence:
                        report += "<details>\n<summary>Technical Details</summary>\n\n"
                        report += f"```json\n{json.dumps(exp.evidence, indent=2)}\n```\n"
                        report += "</details>\n\n"
        
        return report
    
    def _generate_text_report(self) -> str:
        """Generate plain text report"""
        lines = ["=" * 60, "MIGRATION ANALYSIS REPORT", "=" * 60, ""]
        
        for exp in self.explanations:
            lines.append(f"[{exp.type.value.upper()}] {exp.title}")
            lines.append(f"  {exp.summary}")
            for detail in exp.details:
                lines.append(f"    • {detail}")
            lines.append("")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all explanations"""
        self.explanations = []


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Explainability Engine Module Loaded")
    
    # Demo
    engine = ExplainabilityEngine()
    
    exp = engine.explain_column_mapping(
        source_col="cust_id",
        target_col="customer_id", 
        semantic_score=0.92,
        syntactic_score=0.85,
        type_score=1.0,
        source_type="INTEGER",
        target_type="INTEGER",
        overall_score=0.91
    )
    
    print("\nSample Explanation:")
    print(exp.to_markdown())
