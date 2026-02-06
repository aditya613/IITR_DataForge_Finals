"""
=============================================================================
MODULE 2: SEMANTIC MATCHER (AI/ML CORE)
=============================================================================
Purpose: Intelligently match source columns to target columns using AI
Features:
    - Local embeddings (NO API - uses sentence-transformers)
    - Multi-signal matching (name similarity + type compatibility + semantic)
    - Confidence scoring
    - Handles abbreviations, synonyms, different naming conventions
=============================================================================
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import re
from enum import Enum

# Local ML imports (NO API NEEDED)
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Using fallback matching.")

from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

from schema_extractor import ColumnInfo, TableInfo, DatabaseSchema


class MatchConfidence(Enum):
    """Confidence levels for matches"""
    HIGH = "high"       # > 85%
    MEDIUM = "medium"   # 60-85%
    LOW = "low"         # 40-60%
    NONE = "none"       # < 40%


@dataclass
class ColumnMatch:
    """Represents a potential column mapping"""
    source_column: str
    source_table: str
    target_column: str
    target_table: str
    overall_score: float  # 0-1
    confidence: MatchConfidence
    
    # Individual scores for explainability
    semantic_score: float = 0.0
    syntactic_score: float = 0.0
    type_score: float = 0.0
    
    # Explanation components
    explanation: str = ""
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "source": f"{self.source_table}.{self.source_column}",
            "target": f"{self.target_table}.{self.target_column}",
            "overall_score": round(self.overall_score, 3),
            "confidence": self.confidence.value,
            "semantic_score": round(self.semantic_score, 3),
            "syntactic_score": round(self.syntactic_score, 3),
            "type_score": round(self.type_score, 3),
            "explanation": self.explanation,
            "warnings": self.warnings
        }


class SemanticMatcher:
    """
    AI-powered column matching using multiple signals:
    1. Semantic similarity (embeddings)
    2. Syntactic similarity (fuzzy matching)
    3. Data type compatibility
    4. Naming pattern recognition
    """
    
    # Common abbreviations in databases
    ABBREVIATIONS = {
        "cust": "customer",
        "prod": "product",
        "qty": "quantity",
        "amt": "amount",
        "dt": "date",
        "ts": "timestamp",
        "num": "number",
        "no": "number",
        "id": "identifier",
        "desc": "description",
        "addr": "address",
        "tel": "telephone",
        "ph": "phone",
        "fname": "first name",
        "lname": "last name",
        "dob": "date of birth",
        "emp": "employee",
        "dept": "department",
        "mgr": "manager",
        "org": "organization",
        "cat": "category",
        "subcat": "subcategory",
        "inv": "invoice",
        "ord": "order",
        "pmt": "payment",
        "txn": "transaction",
        "acct": "account",
        "bal": "balance",
        "curr": "currency",
        "stat": "status",
        "flg": "flag",
        "ind": "indicator",
        "cnt": "count",
        "tot": "total",
        "avg": "average",
        "min": "minimum",
        "max": "maximum",
        "src": "source",
        "tgt": "target",
        "dest": "destination",
        "msg": "message",
        "err": "error",
        "ref": "reference",
        "seq": "sequence",
        "ver": "version",
        "upd": "update",
        "crt": "create",
        "del": "delete",
        "mod": "modified"
    }
    
    # Data type compatibility matrix
    TYPE_COMPATIBILITY = {
        # source_type: [compatible_target_types]
        "INTEGER": ["INTEGER", "BIGINT", "INT", "SMALLINT", "NUMERIC", "DECIMAL", "FLOAT", "DOUBLE", "REAL"],
        "INT": ["INTEGER", "BIGINT", "INT", "SMALLINT", "NUMERIC", "DECIMAL", "FLOAT", "DOUBLE", "REAL"],
        "BIGINT": ["BIGINT", "INTEGER", "NUMERIC", "DECIMAL"],
        "FLOAT": ["FLOAT", "DOUBLE", "REAL", "NUMERIC", "DECIMAL"],
        "DOUBLE": ["DOUBLE", "FLOAT", "REAL", "NUMERIC", "DECIMAL"],
        "REAL": ["REAL", "FLOAT", "DOUBLE", "NUMERIC", "DECIMAL"],
        "TEXT": ["TEXT", "VARCHAR", "CHAR", "NVARCHAR", "NCHAR", "STRING", "CLOB"],
        "VARCHAR": ["VARCHAR", "TEXT", "CHAR", "NVARCHAR", "NCHAR", "STRING"],
        "CHAR": ["CHAR", "VARCHAR", "TEXT", "NCHAR"],
        "BLOB": ["BLOB", "BINARY", "VARBINARY", "BYTEA"],
        "DATE": ["DATE", "DATETIME", "TIMESTAMP"],
        "DATETIME": ["DATETIME", "TIMESTAMP", "DATE"],
        "TIMESTAMP": ["TIMESTAMP", "DATETIME", "DATE"],
        "BOOLEAN": ["BOOLEAN", "BIT", "TINYINT", "INTEGER"],
        "BOOL": ["BOOLEAN", "BIT", "TINYINT", "INTEGER"],
    }
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic matcher
        
        Args:
            model_name: HuggingFace model for embeddings (runs locally)
                       Options: 
                       - "all-MiniLM-L6-v2" (fast, good quality)
                       - "all-mpnet-base-v2" (slower, better quality)
                       - "paraphrase-MiniLM-L6-v2" (good for paraphrases)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        
        # Weights for combining scores
        self.weights = {
            "semantic": 0.50,   # Embedding similarity
            "syntactic": 0.30,  # Fuzzy string matching
            "type": 0.20       # Data type compatibility
        }
    
    def _load_model(self):
        """Load the sentence transformer model"""
        if EMBEDDINGS_AVAILABLE:
            try:
                print(f"Loading embedding model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                print("Model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print("Using fallback matching (no embeddings)")
    
    def _expand_abbreviations(self, name: str) -> str:
        """Expand common database abbreviations"""
        # Split by common separators
        parts = re.split(r'[_\-\s]+', name.lower())
        expanded = []
        
        for part in parts:
            if part in self.ABBREVIATIONS:
                expanded.append(self.ABBREVIATIONS[part])
            else:
                expanded.append(part)
        
        return " ".join(expanded)
    
    def _normalize_column_name(self, name: str) -> str:
        """
        Normalize column name for better matching
        - Expand abbreviations
        - Convert to lowercase
        - Replace separators with spaces
        """
        # Replace underscores and camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)  # camelCase
        name = re.sub(r'[_\-]+', ' ', name)  # underscores/dashes
        name = name.lower().strip()
        
        # Expand abbreviations
        name = self._expand_abbreviations(name)
        
        return name
    
    def _compute_semantic_score(self, source_name: str, target_name: str) -> float:
        """Compute semantic similarity using embeddings"""
        if self.model is None:
            return 0.0
        
        # Normalize names
        src_normalized = self._normalize_column_name(source_name)
        tgt_normalized = self._normalize_column_name(target_name)
        
        # Get embeddings
        embeddings = self.model.encode([src_normalized, tgt_normalized])
        
        # Compute cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        return float(max(0, similarity))  # Ensure non-negative
    
    def _compute_syntactic_score(self, source_name: str, target_name: str) -> float:
        """Compute string similarity using fuzzy matching"""
        # Normalize names
        src_normalized = self._normalize_column_name(source_name)
        tgt_normalized = self._normalize_column_name(target_name)
        
        # Multiple fuzzy matching strategies
        scores = [
            fuzz.ratio(src_normalized, tgt_normalized) / 100,
            fuzz.partial_ratio(src_normalized, tgt_normalized) / 100,
            fuzz.token_sort_ratio(src_normalized, tgt_normalized) / 100,
            fuzz.token_set_ratio(src_normalized, tgt_normalized) / 100
        ]
        
        # Return weighted average (favor token-based matching)
        return 0.2 * scores[0] + 0.2 * scores[1] + 0.3 * scores[2] + 0.3 * scores[3]
    
    def _compute_type_score(self, source_type: str, target_type: str) -> float:
        """Compute data type compatibility score"""
        source_type = source_type.upper().split('(')[0].strip()  # Remove size info
        target_type = target_type.upper().split('(')[0].strip()
        
        # Exact match
        if source_type == target_type:
            return 1.0
        
        # Check compatibility matrix
        if source_type in self.TYPE_COMPATIBILITY:
            if target_type in self.TYPE_COMPATIBILITY[source_type]:
                return 0.8  # Compatible but not exact
        
        # Check reverse compatibility
        if target_type in self.TYPE_COMPATIBILITY:
            if source_type in self.TYPE_COMPATIBILITY[target_type]:
                return 0.6  # Reverse compatible (might need conversion)
        
        # No match
        return 0.2  # Low score but not zero (might still be valid)
    
    def _determine_confidence(self, score: float) -> MatchConfidence:
        """Determine confidence level from score"""
        if score >= 0.85:
            return MatchConfidence.HIGH
        elif score >= 0.60:
            return MatchConfidence.MEDIUM
        elif score >= 0.40:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.NONE
    
    def _generate_explanation(self, match: ColumnMatch, 
                             source_col: ColumnInfo, 
                             target_col: ColumnInfo) -> str:
        """Generate human-readable explanation for the match"""
        parts = []
        
        # Semantic explanation
        if match.semantic_score > 0.8:
            parts.append(f"Strong semantic similarity ({match.semantic_score:.0%})")
        elif match.semantic_score > 0.6:
            parts.append(f"Moderate semantic similarity ({match.semantic_score:.0%})")
        
        # Syntactic explanation
        if match.syntactic_score > 0.8:
            parts.append(f"Names are very similar ({match.syntactic_score:.0%})")
        elif match.syntactic_score > 0.6:
            parts.append(f"Names are somewhat similar ({match.syntactic_score:.0%})")
        
        # Type explanation
        if match.type_score == 1.0:
            parts.append(f"Exact type match ({source_col.data_type})")
        elif match.type_score >= 0.8:
            parts.append(f"Compatible types ({source_col.data_type} → {target_col.data_type})")
        elif match.type_score < 0.6:
            match.warnings.append(f"Type mismatch: {source_col.data_type} → {target_col.data_type}")
        
        # Check for potential issues
        if source_col.is_primary_key and not target_col.is_primary_key:
            match.warnings.append("Source is PK but target is not")
        
        if not source_col.is_nullable and target_col.is_nullable:
            match.warnings.append("Source is NOT NULL but target allows NULL")
        
        return "; ".join(parts) if parts else "Matched based on overall similarity"
    
    def match_columns(self, 
                     source_table: TableInfo, 
                     target_table: TableInfo,
                     threshold: float = 0.4) -> List[ColumnMatch]:
        """
        Match columns between source and target tables
        
        Args:
            source_table: Source table info
            target_table: Target table info  
            threshold: Minimum score threshold for matches
            
        Returns:
            List of ColumnMatch objects sorted by score
        """
        matches = []
        
        for src_col in source_table.columns:
            best_match = None
            best_score = 0
            
            for tgt_col in target_table.columns:
                # Compute individual scores
                semantic = self._compute_semantic_score(src_col.name, tgt_col.name)
                syntactic = self._compute_syntactic_score(src_col.name, tgt_col.name)
                type_score = self._compute_type_score(src_col.data_type, tgt_col.data_type)
                
                # Weighted combination
                overall = (
                    self.weights["semantic"] * semantic +
                    self.weights["syntactic"] * syntactic +
                    self.weights["type"] * type_score
                )
                
                if overall > best_score and overall >= threshold:
                    best_score = overall
                    best_match = ColumnMatch(
                        source_column=src_col.name,
                        source_table=source_table.name,
                        target_column=tgt_col.name,
                        target_table=target_table.name,
                        overall_score=overall,
                        confidence=self._determine_confidence(overall),
                        semantic_score=semantic,
                        syntactic_score=syntactic,
                        type_score=type_score
                    )
            
            if best_match:
                # Generate explanation
                tgt_col = next(c for c in target_table.columns if c.name == best_match.target_column)
                best_match.explanation = self._generate_explanation(best_match, src_col, tgt_col)
                matches.append(best_match)
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches
    
    def match_schemas(self, 
                     source: DatabaseSchema, 
                     target: DatabaseSchema,
                     threshold: float = 0.4) -> Dict[str, List[ColumnMatch]]:
        """
        Match all tables and columns between source and target schemas
        
        Returns:
            Dictionary mapping "source_table->target_table" to list of column matches
        """
        all_matches = {}
        
        for src_table in source.tables:
            for tgt_table in target.tables:
                # First check if tables might be related
                table_similarity = self._compute_syntactic_score(
                    src_table.name, 
                    tgt_table.name
                )
                
                # Only match columns if tables seem related
                if table_similarity > 0.3:
                    key = f"{src_table.name} → {tgt_table.name}"
                    matches = self.match_columns(src_table, tgt_table, threshold)
                    
                    if matches:
                        all_matches[key] = matches
        
        return all_matches


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Semantic Matcher Module Loaded")
    print(f"Embeddings available: {EMBEDDINGS_AVAILABLE}")
    
    # Quick test
    matcher = SemanticMatcher()
    
    # Test abbreviation expansion
    test_names = ["cust_id", "customer_identifier", "prod_name", "product_name"]
    print("\nAbbreviation expansion test:")
    for name in test_names:
        expanded = matcher._normalize_column_name(name)
        print(f"  {name} → {expanded}")
