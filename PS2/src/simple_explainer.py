"""
=============================================================================
MODULE 8: SIMPLE EXPLAINER (Non-Technical Language)
=============================================================================
Purpose: Generate explanations understandable by non-technical stakeholders
Features:
    - Plain English explanations
    - Business-friendly reports
    - Visual indicators
    - Executive summaries
=============================================================================
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json


@dataclass
class SimpleExplanation:
    """A simple, non-technical explanation"""
    title: str
    what_happened: str           # Plain English description
    why_it_happened: str         # Reason in simple terms
    what_it_means: str           # Business impact
    action_needed: Optional[str] = None
    confidence_level: str = "High"  # High, Medium, Low
    icon: str = "ℹ️"  # Visual indicator
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "what_happened": self.what_happened,
            "why_it_happened": self.why_it_happened,
            "what_it_means": self.what_it_means,
            "action_needed": self.action_needed,
            "confidence_level": self.confidence_level,
            "icon": self.icon
        }


class SimpleExplainer:
    """
    Generates non-technical explanations for migration decisions
    """
    
    def __init__(self):
        self.explanations: List[SimpleExplanation] = []
    
    def explain_column_mapping(self,
                               source_col: str,
                               target_col: str,
                               confidence: float,
                               source_type: str,
                               target_type: str,
                               semantic_score: float,
                               syntactic_score: float) -> SimpleExplanation:
        """
        Generate a simple explanation for why a column was mapped
        """
        # Determine confidence level
        if confidence >= 0.85:
            conf_level = "High"
            icon = "✅"
        elif confidence >= 0.60:
            conf_level = "Medium"
            icon = "⚠️"
        else:
            conf_level = "Low"
            icon = "❓"
        
        # Build what happened
        what_happened = f"The system matched '{source_col}' from the old database to '{target_col}' in the new database."
        
        # Build why (based on scores)
        reasons = []
        
        if syntactic_score >= 0.8:
            reasons.append("the names are very similar")
        elif syntactic_score >= 0.5:
            reasons.append("the names are somewhat similar")
        
        if semantic_score >= 0.8:
            reasons.append("they appear to mean the same thing")
        elif semantic_score >= 0.5:
            reasons.append("they seem to represent similar data")
        
        if source_type.upper() == target_type.upper():
            reasons.append("they store the same type of data")
        
        if reasons:
            why_it_happened = "This match was made because " + ", and ".join(reasons) + "."
        else:
            why_it_happened = "This match was made based on overall pattern analysis."
        
        # Build business meaning
        if confidence >= 0.85:
            what_it_means = "This is a reliable match. Data will transfer correctly without any issues."
        elif confidence >= 0.60:
            what_it_means = "This match is likely correct, but someone should verify it before the full migration."
        else:
            what_it_means = "This match needs manual review. The system is not confident about this pairing."
        
        # Action needed
        if confidence >= 0.85:
            action_needed = None
        elif confidence >= 0.60:
            action_needed = "Please review this mapping before migration."
        else:
            action_needed = "⚠️ Manual verification required before proceeding."
        
        explanation = SimpleExplanation(
            title=f"{source_col} → {target_col}",
            what_happened=what_happened,
            why_it_happened=why_it_happened,
            what_it_means=what_it_means,
            action_needed=action_needed,
            confidence_level=conf_level,
            icon=icon
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def explain_unmapped_column(self,
                               column: str,
                               table: str,
                               is_source: bool) -> SimpleExplanation:
        """
        Explain why a column was not mapped
        """
        if is_source:
            what_happened = f"The column '{column}' in the old database table '{table}' was not matched to any column in the new database."
            why_it_happened = "The system could not find a column in the new database that is similar enough to this one."
            what_it_means = "Data in this column will NOT be migrated unless you manually specify where it should go."
            action_needed = "Decide if this data needs to be migrated. If yes, manually map it to a target column."
        else:
            what_happened = f"The column '{column}' in the new database table '{table}' was not matched to any column in the old database."
            why_it_happened = "There doesn't appear to be equivalent data in the old system."
            what_it_means = "This column will remain empty (or use default values) after migration."
            action_needed = "Verify if this column should receive data from the old system."
        
        return SimpleExplanation(
            title=f"Unmapped: {column}",
            what_happened=what_happened,
            why_it_happened=why_it_happened,
            what_it_means=what_it_means,
            action_needed=action_needed,
            confidence_level="N/A",
            icon="🚫"
        )
    
    def explain_transformation(self,
                              source_col: str,
                              target_col: str,
                              transform_type: str) -> SimpleExplanation:
        """
        Explain a data transformation in simple terms
        """
        transform_explanations = {
            "direct": ("No changes needed", "The data formats are identical."),
            "cast_int": ("Convert to whole number", "The new system expects whole numbers only."),
            "cast_float": ("Convert to decimal number", "The new system uses decimal numbers."),
            "cast_str": ("Convert to text", "The new system stores this as text."),
            "uppercase": ("Convert to UPPERCASE", "The new system requires uppercase text."),
            "lowercase": ("Convert to lowercase", "The new system requires lowercase text."),
            "trim": ("Remove extra spaces", "Extra spaces at the start/end will be removed."),
            "date_format": ("Change date format", "The date will be reformatted to match the new system."),
            "split": ("Split into multiple fields", "One field becomes multiple fields in the new system."),
            "merge": ("Combine multiple fields", "Multiple fields become one in the new system."),
        }
        
        title, reason = transform_explanations.get(
            transform_type, 
            ("Data conversion", "The data needs to be adjusted for the new system.")
        )
        
        return SimpleExplanation(
            title=f"Transform: {source_col}",
            what_happened=f"Data from '{source_col}' will be converted before going into '{target_col}'.",
            why_it_happened=reason,
            what_it_means=f"Your data will be automatically adjusted: {title}.",
            action_needed="Review a sample to ensure the conversion looks correct.",
            confidence_level="High",
            icon="🔄"
        )
    
    def explain_failed_record(self,
                             record_id: Any,
                             error_type: str,
                             error_message: str) -> SimpleExplanation:
        """
        Explain why a record failed to migrate
        """
        # Simplify common errors
        if "null" in error_message.lower() or "not null" in error_message.lower():
            simple_error = "Missing required data"
            meaning = "The new system requires this field to have a value, but the old record was empty."
            action = "Fill in the missing data or update the new system to allow empty values."
        elif "constraint" in error_message.lower() or "foreign key" in error_message.lower():
            simple_error = "Related data not found"
            meaning = "This record references other data that doesn't exist in the new system yet."
            action = "Ensure related records are migrated first, or remove the reference."
        elif "unique" in error_message.lower() or "duplicate" in error_message.lower():
            simple_error = "Duplicate entry"
            meaning = "A record with the same key already exists in the new system."
            action = "Decide whether to skip, update, or merge this record."
        elif "type" in error_message.lower() or "cast" in error_message.lower():
            simple_error = "Data format issue"
            meaning = "The data couldn't be converted to the format required by the new system."
            action = "Review and fix the data format in the source, or adjust the conversion rules."
        else:
            simple_error = "Migration error"
            meaning = "An unexpected issue occurred while moving this record."
            action = "Review the technical details and consult with your data team."
        
        return SimpleExplanation(
            title=f"Failed Record #{record_id}",
            what_happened=f"Record #{record_id} could not be migrated: {simple_error}.",
            why_it_happened=meaning,
            what_it_means="This specific record was NOT moved to the new system.",
            action_needed=action,
            confidence_level="N/A",
            icon="❌"
        )
    
    def explain_validation_result(self,
                                  check_name: str,
                                  passed: bool,
                                  details: Dict) -> SimpleExplanation:
        """
        Explain a validation check result
        """
        if "row count" in check_name.lower():
            if passed:
                return SimpleExplanation(
                    title="Row Count Check",
                    what_happened="All records were successfully migrated.",
                    why_it_happened="The number of records in the new system matches the old system.",
                    what_it_means="✅ No data was lost during migration.",
                    confidence_level="High",
                    icon="✅"
                )
            else:
                src = details.get('source_count', '?')
                tgt = details.get('target_count', '?')
                return SimpleExplanation(
                    title="Row Count Mismatch",
                    what_happened=f"The old system had {src} records, but the new system has {tgt}.",
                    why_it_happened="Some records may have failed to migrate, or there were duplicates/filters.",
                    what_it_means="⚠️ Not all data was transferred. Investigation needed.",
                    action_needed="Check the failed records report to see what was missed.",
                    confidence_level="Low",
                    icon="❌"
                )
        
        elif "null" in check_name.lower():
            if passed:
                return SimpleExplanation(
                    title="Data Completeness Check",
                    what_happened="All required fields have values.",
                    why_it_happened="No empty values were found in mandatory fields.",
                    what_it_means="✅ Data is complete and ready for use.",
                    confidence_level="High",
                    icon="✅"
                )
            else:
                return SimpleExplanation(
                    title="Missing Data Found",
                    what_happened=f"Some fields have empty values that shouldn't be empty.",
                    why_it_happened="The source data had gaps, or the mapping created empty values.",
                    what_it_means="⚠️ Some records may be incomplete in the new system.",
                    action_needed="Review which fields are empty and decide if they need default values.",
                    confidence_level="Medium",
                    icon="⚠️"
                )
        
        elif "duplicate" in check_name.lower():
            if passed:
                return SimpleExplanation(
                    title="Duplicate Check",
                    what_happened="No duplicate records were found.",
                    why_it_happened="Each record has a unique identifier as expected.",
                    what_it_means="✅ Data integrity is maintained.",
                    confidence_level="High",
                    icon="✅"
                )
            else:
                return SimpleExplanation(
                    title="Duplicates Found",
                    what_happened="The same record appears multiple times.",
                    why_it_happened="The migration may have run twice, or source data had duplicates.",
                    what_it_means="⚠️ You may have redundant data that needs cleanup.",
                    action_needed="Identify and remove duplicate records.",
                    confidence_level="Low",
                    icon="❌"
                )
        
        # Generic
        return SimpleExplanation(
            title=check_name,
            what_happened="A validation check was performed.",
            why_it_happened="This ensures data quality after migration.",
            what_it_means="✅ Check passed." if passed else "⚠️ Check requires attention.",
            action_needed=None if passed else "Review the details and address any issues.",
            confidence_level="High" if passed else "Medium",
            icon="✅" if passed else "⚠️"
        )
    
    def generate_executive_summary(self,
                                  total_tables: int,
                                  records_migrated: int,
                                  records_failed: int,
                                  high_confidence_mappings: int,
                                  low_confidence_mappings: int,
                                  validation_passed: int,
                                  validation_failed: int) -> str:
        """
        Generate an executive summary in plain language
        """
        success_rate = (records_migrated / (records_migrated + records_failed) * 100) if (records_migrated + records_failed) > 0 else 0
        
        summary = f"""
# Migration Summary Report

## Overall Status: {"✅ SUCCESS" if records_failed == 0 and validation_failed == 0 else "⚠️ ATTENTION NEEDED" if success_rate > 95 else "❌ ISSUES DETECTED"}

### What We Did
We analyzed {total_tables} tables and automatically matched columns between your old and new databases.

### Key Numbers
- **{records_migrated:,}** records were successfully moved to the new system
- **{records_failed:,}** records could not be migrated (see details below)
- **{success_rate:.1f}%** overall success rate

### Confidence in Our Mappings
- ✅ **{high_confidence_mappings}** column matches we're confident about
- ⚠️ **{low_confidence_mappings}** column matches that need your review

### Data Quality Checks
- ✅ **{validation_passed}** checks passed
- {"❌" if validation_failed > 0 else "✅"} **{validation_failed}** checks need attention

### What This Means for You
"""
        
        if records_failed == 0 and validation_failed == 0:
            summary += """
✅ **Great news!** The migration completed successfully. All your data has been 
transferred to the new system without any issues. You can proceed with confidence.
"""
        elif success_rate > 99:
            summary += f"""
⚠️ **Almost there!** {success_rate:.1f}% of your data migrated successfully. 
A small number of records ({records_failed:,}) need manual attention. 
Review the "Failed Records" section below to resolve these issues.
"""
        elif success_rate > 95:
            summary += f"""
⚠️ **Needs Review.** Most data ({success_rate:.1f}%) transferred correctly, but 
{records_failed:,} records require investigation. We recommend reviewing the 
failures before going live with the new system.
"""
        else:
            summary += f"""
❌ **Action Required.** A significant portion of your data ({records_failed:,} records) 
did not migrate successfully. Please review the detailed report below and work with 
your technical team to resolve these issues before proceeding.
"""
        
        return summary
    
    def generate_simple_report(self) -> str:
        """
        Generate a simple, non-technical report
        """
        report = "# Data Migration Explanation Report\n\n"
        report += f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n"
        report += "---\n\n"
        
        for exp in self.explanations:
            report += f"## {exp.icon} {exp.title}\n\n"
            report += f"**What happened:** {exp.what_happened}\n\n"
            report += f"**Why:** {exp.why_it_happened}\n\n"
            report += f"**What this means:** {exp.what_it_means}\n\n"
            
            if exp.action_needed:
                report += f"**⚡ Action needed:** {exp.action_needed}\n\n"
            
            report += f"*Confidence: {exp.confidence_level}*\n\n"
            report += "---\n\n"
        
        return report
    
    def clear(self):
        """Clear all explanations"""
        self.explanations = []


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Simple Explainer Module Loaded")
    
    explainer = SimpleExplainer()
    
    # Demo explanation
    exp = explainer.explain_column_mapping(
        source_col="cust_id",
        target_col="customer_id",
        confidence=0.92,
        source_type="INTEGER",
        target_type="INTEGER",
        semantic_score=0.95,
        syntactic_score=0.88
    )
    
    print("\nSample Simple Explanation:")
    print(f"Title: {exp.title}")
    print(f"What happened: {exp.what_happened}")
    print(f"Why: {exp.why_it_happened}")
    print(f"What it means: {exp.what_it_means}")
