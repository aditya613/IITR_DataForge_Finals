"""
Hybrid AI Engine with Google Gemini API Integration
Combines BERT embeddings, Gemini LLM, TF-IDF, and Domain knowledge
for intelligent column matching with explainability
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Gemini API
import google.generativeai as genai

# Local models
try:
    from sentence_transformers import SentenceTransformer
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("Warning: sentence-transformers not installed. BERT matching disabled.")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MatchResult:
    """Result of column matching with scores from all models"""
    source_column: str
    target_column: str
    source_table: str
    target_table: str
    bert_score: float
    gemini_score: float
    tfidf_score: float
    domain_score: float
    ensemble_score: float
    confidence_level: str  # high, medium, low
    mapping_type: str  # 1:1, 1:Many, Many:1
    transformation: Optional[str] = None
    explanation: str = ""
    why_mapped: str = ""
    why_not_others: str = ""
    data_type_source: str = ""
    data_type_target: str = ""


@dataclass 
class ValidationResult:
    """Result of data validation"""
    source_count: int
    target_count: int
    null_checks: Dict[str, int]
    duplicate_checks: Dict[str, int]
    failed_records: List[Dict]
    referential_integrity: List[Dict]
    is_valid: bool
    summary: str


class HybridAIEngine:
    """
    Hybrid AI Engine combining multiple models for intelligent column matching.
    
    Models and Weights:
    - BERT: Semantic similarity (35%)
    - Gemini: LLM contextual understanding (30%)  
    - TF-IDF: Character pattern matching (15%)
    - Domain: Abbreviation knowledge (20%)
    """
    
    # Common database abbreviations
    ABBREVIATIONS = {
        # Customer/Person
        'cust': 'customer', 'cust_id': 'customer_id', 'cid': 'customer_id',
        'fname': 'first_name', 'lname': 'last_name', 'mname': 'middle_name',
        'dob': 'date_of_birth', 'bday': 'birthday', 'bd': 'birth_date',
        'ssn': 'social_security_number',
        
        # Contact
        'ph': 'phone', 'tel': 'telephone', 'mob': 'mobile', 'cell': 'cellphone',
        'addr': 'address', 'addr1': 'address_line1', 'addr2': 'address_line2',
        'zip': 'zip_code', 'postal': 'postal_code', 'pcode': 'postal_code',
        
        # Location
        'ctry': 'country', 'cntry': 'country', 'cnt': 'country',
        'prov': 'province', 'reg': 'region', 'st': 'state',
        'lat': 'latitude', 'lng': 'longitude', 'lon': 'longitude',
        
        # Order/Transaction  
        'ord': 'order', 'ord_id': 'order_id', 'oid': 'order_id',
        'txn': 'transaction', 'trans': 'transaction',
        'inv': 'invoice', 'inv_no': 'invoice_number',
        'qty': 'quantity', 'amt': 'amount', 'tot': 'total',
        'disc': 'discount', 'pct': 'percent',
        
        # Product
        'prod': 'product', 'prod_id': 'product_id', 'pid': 'product_id',
        'sku': 'stock_keeping_unit', 'cat': 'category',
        'desc': 'description', 'descr': 'description',
        
        # Financial
        'acct': 'account', 'acc': 'account', 'acct_no': 'account_number',
        'bal': 'balance', 'curr': 'currency', 'ccy': 'currency',
        'cr': 'credit', 'dr': 'debit', 'pmt': 'payment',
        
        # Date/Time
        'dt': 'date', 'tm': 'time', 'ts': 'timestamp',
        'yr': 'year', 'mo': 'month', 'dy': 'day',
        'created_dt': 'created_date', 'updated_dt': 'updated_date',
        
        # Status
        'sts': 'status', 'stat': 'status', 'flg': 'flag',
        'actv': 'active', 'inactv': 'inactive',
        
        # Employee
        'emp': 'employee', 'emp_id': 'employee_id', 'eid': 'employee_id',
        'mgr': 'manager', 'dept': 'department', 'sal': 'salary',
        
        # Technical
        'id': 'identifier', 'pk': 'primary_key', 'fk': 'foreign_key',
        'seq': 'sequence', 'num': 'number', 'no': 'number',
        'src': 'source', 'tgt': 'target', 'dest': 'destination',
        'ref': 'reference', 'cfg': 'configuration',
    }
    
    # Semantic equivalents
    SEMANTIC_GROUPS = {
        'name': ['name', 'title', 'label', 'designation'],
        'identifier': ['id', 'code', 'key', 'number', 'identifier'],
        'description': ['description', 'desc', 'details', 'notes', 'comments'],
        'date': ['date', 'datetime', 'timestamp', 'time', 'when'],
        'amount': ['amount', 'total', 'sum', 'value', 'price', 'cost'],
        'status': ['status', 'state', 'condition', 'flag'],
        'email': ['email', 'mail', 'email_address', 'e_mail'],
        'phone': ['phone', 'telephone', 'mobile', 'cell', 'contact_number'],
        'address': ['address', 'location', 'street', 'addr'],
    }
    
    def __init__(self, gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-1.5-flash"):
        """Initialize the hybrid AI engine"""
        
        # Initialize BERT
        self.bert_model = None
        if BERT_AVAILABLE:
            try:
                self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ BERT model loaded successfully")
            except Exception as e:
                print(f"✗ Could not load BERT model: {e}")
        
        # Initialize Gemini
        self.gemini_model = None
        self.gemini_api_key = gemini_api_key or os.environ.get('GEMINI_API_KEY', '')
        
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(gemini_model)
                print(f"✓ Gemini model ({gemini_model}) initialized")
            except Exception as e:
                print(f"✗ Could not initialize Gemini: {e}")
        else:
            print("ℹ Gemini API key not provided - using local models only")
        
        # Initialize TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            lowercase=True
        )
        
        # Model weights - Gemini has higher weight when available
        self.weights = {'bert': 0.30, 'gemini': 0.40, 'tfidf': 0.10, 'domain': 0.20}
        
        # Embedding cache
        self._embedding_cache: Dict[str, np.ndarray] = {}
    
    def _normalize_column_name(self, name: str) -> str:
        """Normalize column name for comparison"""
        name = name.lower()
        name = re.sub(r'[_\-\.]', ' ', name)
        words = name.split()
        expanded = [self.ABBREVIATIONS.get(w, w) for w in words]
        return ' '.join(expanded)
    
    def _get_bert_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get BERT embedding with caching"""
        if not self.bert_model:
            return None
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        normalized = self._normalize_column_name(text)
        embedding = self.bert_model.encode(normalized, convert_to_numpy=True)
        self._embedding_cache[text] = embedding
        return embedding
    
    def calculate_bert_similarity(self, source: str, target: str) -> float:
        """Calculate BERT-based semantic similarity"""
        if not self.bert_model:
            return 0.0
        source_emb = self._get_bert_embedding(source)
        target_emb = self._get_bert_embedding(target)
        if source_emb is None or target_emb is None:
            return 0.0
        similarity = cosine_similarity([source_emb], [target_emb])[0][0]
        return float(max(0, min(1, similarity)))
    
    def calculate_tfidf_similarity(self, source: str, target: str) -> float:
        """Calculate TF-IDF based similarity"""
        source_norm = self._normalize_column_name(source)
        target_norm = self._normalize_column_name(target)
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([source_norm, target_norm])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(max(0, min(1, similarity)))
        except:
            return 0.0
    
    def calculate_domain_similarity(self, source: str, target: str) -> float:
        """Calculate domain-aware similarity"""
        source_norm = self._normalize_column_name(source)
        target_norm = self._normalize_column_name(target)
        
        if source_norm == target_norm:
            return 1.0
        
        # Check semantic groups
        for terms in self.SEMANTIC_GROUPS.values():
            source_words = set(source_norm.split())
            target_words = set(target_norm.split())
            if (source_words & set(terms)) and (target_words & set(terms)):
                return 0.85
        
        # Word overlap
        source_words = set(source_norm.split())
        target_words = set(target_norm.split())
        overlap = len(source_words & target_words)
        total = len(source_words | target_words)
        return overlap / total if total > 0 else 0.0
    
    def get_gemini_analysis(self, source_columns: List[str], target_columns: List[str],
                           source_table: str = "", target_table: str = "",
                           source_types: Dict[str, str] = None, 
                           target_types: Dict[str, str] = None) -> Dict[str, Any]:
        """Use Gemini to analyze column mappings with detailed explanations"""
        if not self.gemini_model:
            return {}
        
        source_info = json.dumps({
            col: source_types.get(col, "unknown") if source_types else "unknown"
            for col in source_columns
        }, indent=2)
        
        target_info = json.dumps({
            col: target_types.get(col, "unknown") if target_types else "unknown"
            for col in target_columns
        }, indent=2)
        
        prompt = f"""You are an expert database migration analyst. Analyze these schemas and provide detailed mapping recommendations.

SOURCE TABLE: {source_table or 'source_db'}
Source Columns (with data types):
{source_info}

TARGET TABLE: {target_table or 'target_db'}  
Target Columns (with data types):
{target_info}

For EACH source column, provide:
1. Best matching target column (or null if no good match)
2. Confidence score (0.0 to 1.0)
3. WHY this mapping makes sense (explain for non-technical stakeholders)
4. What transformation is needed (if any)
5. Why other potential matches were rejected

Respond ONLY with valid JSON (no markdown):
{{
  "mappings": [
    {{
      "source": "column_name",
      "target": "matched_column_or_null",
      "confidence": 0.95,
      "why_mapped": "Clear explanation a business user can understand",
      "transformation": "none OR description of required transformation",
      "why_not_others": "Why similar columns were not chosen",
      "mapping_type": "1:1 or 1:Many or Many:1"
    }}
  ],
  "unmapped_targets": ["list of target columns with no source"],
  "unmapped_explanation": "Why these target columns have no source mapping",
  "data_quality_concerns": ["potential issues to watch for"],
  "overall_quality": "assessment of mapping completeness"
}}"""
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )
            
            text = response.text.strip()
            # Clean up response
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            text = text.strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return {}
    
    def match_columns(self, source_schema: Dict[str, Dict], 
                     target_schema: Dict[str, Dict],
                     threshold: float = 0.6) -> Tuple[List[MatchResult], Dict]:
        """
        Match columns between source and target schemas.
        
        Args:
            source_schema: {table_name: {column_name: data_type, ...}}
            target_schema: {table_name: {column_name: data_type, ...}}
            threshold: Minimum score for a valid match
        
        Returns:
            Tuple of (List[MatchResult], stats_dict)
        """
        results = []
        gemini_cache = {}
        
        # Flatten schemas
        source_flat = {}
        target_flat = {}
        source_types = {}
        target_types = {}
        
        for table, columns in source_schema.items():
            for col, dtype in columns.items():
                key = f"{table}.{col}"
                source_flat[key] = col
                source_types[col] = dtype
                
        for table, columns in target_schema.items():
            for col, dtype in columns.items():
                key = f"{table}.{col}"
                target_flat[key] = col
                target_types[col] = dtype
        
        # Get Gemini analysis
        if self.gemini_model:
            for src_table in source_schema:
                for tgt_table in target_schema:
                    key = f"{src_table}_{tgt_table}"
                    src_cols = list(source_schema[src_table].keys())
                    tgt_cols = list(target_schema[tgt_table].keys())
                    gemini_cache[key] = self.get_gemini_analysis(
                        src_cols, tgt_cols, src_table, tgt_table,
                        source_types, target_types
                    )
        
        # Match each source column
        for src_table, src_columns in source_schema.items():
            for src_col, src_type in src_columns.items():
                best_match = None
                best_score = 0.0
                
                for tgt_table, tgt_columns in target_schema.items():
                    gemini_key = f"{src_table}_{tgt_table}"
                    gemini_data = gemini_cache.get(gemini_key, {})
                    gemini_mappings = {
                        m['source']: m for m in gemini_data.get('mappings', [])
                    }
                    
                    for tgt_col, tgt_type in tgt_columns.items():
                        # Calculate scores
                        bert_score = self.calculate_bert_similarity(src_col, tgt_col)
                        tfidf_score = self.calculate_tfidf_similarity(src_col, tgt_col)
                        domain_score = self.calculate_domain_similarity(src_col, tgt_col)
                        
                        # Get Gemini score
                        gemini_score = 0.0
                        gemini_info = gemini_mappings.get(src_col, {})
                        if gemini_info.get('target') == tgt_col:
                            gemini_score = gemini_info.get('confidence', 0.0)
                        
                        # Ensemble score with boost for Gemini matches
                        if self.gemini_model:
                            base_ensemble = (
                                self.weights['bert'] * bert_score +
                                self.weights['gemini'] * gemini_score +
                                self.weights['tfidf'] * tfidf_score +
                                self.weights['domain'] * domain_score
                            )
                            # Boost score when Gemini confirms the match with high confidence
                            if gemini_score >= 0.8:
                                # Gemini is confident - boost ensemble toward Gemini's score
                                ensemble = base_ensemble * 0.3 + gemini_score * 0.7
                            elif gemini_score >= 0.5:
                                # Gemini moderately confident
                                ensemble = base_ensemble * 0.5 + gemini_score * 0.5
                            else:
                                ensemble = base_ensemble
                        else:
                            ensemble = (
                                0.50 * bert_score +
                                0.21 * tfidf_score +
                                0.29 * domain_score
                            )
                        
                        if ensemble > best_score:
                            best_score = ensemble
                            best_match = {
                                'target': tgt_col,
                                'target_table': tgt_table,
                                'bert': bert_score,
                                'gemini': gemini_score,
                                'tfidf': tfidf_score,
                                'domain': domain_score,
                                'gemini_info': gemini_info,
                                'target_type': tgt_type
                            }
                
                if best_match and best_score >= threshold:
                    confidence = 'high' if best_score >= 0.85 else 'medium' if best_score >= 0.65 else 'low'
                    
                    gemini_info = best_match.get('gemini_info', {})
                    why_mapped = gemini_info.get('why_mapped', 
                        self._generate_explanation(src_col, best_match['target'], best_match))
                    
                    results.append(MatchResult(
                        source_column=src_col,
                        target_column=best_match['target'],
                        source_table=src_table,
                        target_table=best_match['target_table'],
                        bert_score=best_match['bert'],
                        gemini_score=best_match['gemini'],
                        tfidf_score=best_match['tfidf'],
                        domain_score=best_match['domain'],
                        ensemble_score=best_score,
                        confidence_level=confidence,
                        mapping_type=gemini_info.get('mapping_type', '1:1'),
                        transformation=gemini_info.get('transformation', 'none'),
                        explanation=why_mapped,
                        why_mapped=why_mapped,
                        why_not_others=gemini_info.get('why_not_others', ''),
                        data_type_source=src_type,
                        data_type_target=best_match['target_type']
                    ))
        
        # Calculate statistics
        stats = {
            'total_mappings': len(results),
            'high_confidence': sum(1 for r in results if r.confidence_level == 'high'),
            'medium_confidence': sum(1 for r in results if r.confidence_level == 'medium'),
            'low_confidence': sum(1 for r in results if r.confidence_level == 'low'),
            'average_score': np.mean([r.ensemble_score for r in results]) if results else 0,
            'gemini_enabled': self.gemini_model is not None,
            'bert_enabled': self.bert_model is not None
        }
        
        return results, stats
    
    def _generate_explanation(self, source: str, target: str, scores: Dict) -> str:
        """Generate human-readable explanation"""
        if scores['domain'] > 0.8:
            return f"'{source}' is a common abbreviation for '{target}' in database systems"
        elif scores['bert'] > 0.8:
            return f"'{source}' and '{target}' have very similar semantic meanings"
        elif scores['tfidf'] > 0.7:
            return f"'{source}' and '{target}' share similar naming patterns"
        else:
            return f"Multiple factors suggest '{source}' corresponds to '{target}'"
    
    def get_unmapped_columns(self, source_schema: Dict, target_schema: Dict,
                            mappings: List[MatchResult]) -> Dict[str, List[Dict]]:
        """Get unmapped columns with explanations"""
        mapped_sources = {(m.source_table, m.source_column) for m in mappings}
        mapped_targets = {(m.target_table, m.target_column) for m in mappings}
        
        unmapped = {'source': [], 'target': []}
        
        for table, columns in source_schema.items():
            for col in columns:
                if (table, col) not in mapped_sources:
                    unmapped['source'].append({
                        'table': table,
                        'column': col,
                        'reason': self._explain_unmapped_source(col)
                    })
        
        for table, columns in target_schema.items():
            for col in columns:
                if (table, col) not in mapped_targets:
                    unmapped['target'].append({
                        'table': table,
                        'column': col,
                        'reason': self._explain_unmapped_target(col)
                    })
        
        return unmapped
    
    def _explain_unmapped_source(self, col: str) -> str:
        """Explain why source column wasn't mapped"""
        col_lower = col.lower()
        if any(p in col_lower for p in ['created', 'updated', 'modified', '_at', '_by']):
            return "This appears to be an audit/tracking column not present in target schema"
        if any(p in col_lower for p in ['old_', 'legacy_', 'deprecated']):
            return "This appears to be a legacy column that has been retired"
        if any(p in col_lower for p in ['temp_', 'tmp_', 'backup_']):
            return "This appears to be a temporary/backup column not needed in target"
        return "No sufficiently similar column found in target schema"
    
    def _explain_unmapped_target(self, col: str) -> str:
        """Explain why target column has no source"""
        col_lower = col.lower()
        if any(p in col_lower for p in ['created', 'updated', 'modified', '_at']):
            return "This is likely an auto-generated audit column"
        if 'id' in col_lower and col_lower.endswith('id'):
            return "This appears to be a new identifier that will be auto-generated"
        return "This is a new column in the target schema - may need default value or manual mapping"


def create_engine(gemini_api_key: str = None) -> HybridAIEngine:
    """Create hybrid AI engine with optional Gemini API"""
    return HybridAIEngine(gemini_api_key=gemini_api_key)
