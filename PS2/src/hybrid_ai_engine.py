"""
=============================================================================
HYBRID AI ENGINE: Multi-Model Column Matching
=============================================================================
Combines multiple AI approaches for robust column matching:
1. BERT Embeddings (Local) - Semantic understanding
2. LLM API (OpenAI/Azure/Ollama) - Contextual reasoning
3. TF-IDF + Cosine Similarity - Statistical matching
4. Custom Domain Model - Business abbreviation handling
=============================================================================
"""

import os
import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Local models
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

# For LLM API calls
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types"""
    BERT = "bert"
    LLM_API = "llm_api"
    TFIDF = "tfidf"
    DOMAIN = "domain"
    ENSEMBLE = "ensemble"


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"  # Local LLM
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    NONE = "none"  # Fallback to local only


@dataclass
class ModelConfig:
    """Configuration for hybrid AI engine"""
    # BERT config
    bert_model_name: str = "all-MiniLM-L6-v2"
    
    # LLM API config
    llm_provider: LLMProvider = LLMProvider.NONE
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""
    
    # Weights for ensemble
    bert_weight: float = 0.35
    llm_weight: float = 0.30
    tfidf_weight: float = 0.15
    domain_weight: float = 0.20
    
    # Caching
    enable_cache: bool = True
    cache_dir: str = ".cache/hybrid_ai"


@dataclass
class MatchResult:
    """Result from hybrid matching"""
    source_column: str
    target_column: str
    source_table: str = ""
    target_table: str = ""
    
    # Individual model scores
    bert_score: float = 0.0
    llm_score: float = 0.0
    tfidf_score: float = 0.0
    domain_score: float = 0.0
    
    # Ensemble score
    ensemble_score: float = 0.0
    confidence_level: str = "low"  # low, medium, high
    
    # LLM reasoning (if available)
    llm_reasoning: str = ""
    
    # Metadata
    models_used: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "source_column": self.source_column,
            "target_column": self.target_column,
            "source_table": self.source_table,
            "target_table": self.target_table,
            "bert_score": round(self.bert_score, 4),
            "llm_score": round(self.llm_score, 4),
            "tfidf_score": round(self.tfidf_score, 4),
            "domain_score": round(self.domain_score, 4),
            "ensemble_score": round(self.ensemble_score, 4),
            "confidence_level": self.confidence_level,
            "llm_reasoning": self.llm_reasoning,
            "models_used": self.models_used,
            "warnings": self.warnings
        }


class HybridAIEngine:
    """
    Hybrid AI Engine combining multiple models for column matching
    """
    
    # Comprehensive domain abbreviations
    ABBREVIATIONS = {
        # Customer related
        "cust": "customer", "cstmr": "customer", "cust_id": "customer_identifier",
        "fname": "first_name", "lname": "last_name", "mname": "middle_name",
        "dob": "date_of_birth", "bday": "birthday", "addr": "address",
        "addr1": "address_line_1", "addr2": "address_line_2",
        "phn": "phone", "tel": "telephone", "mob": "mobile", "cell": "cellphone",
        "eml": "email", "e_mail": "email", "mail": "email",
        
        # Financial
        "amt": "amount", "bal": "balance", "pmt": "payment", "pymnt": "payment",
        "inv": "invoice", "invce": "invoice", "txn": "transaction", "trans": "transaction",
        "acct": "account", "acc": "account", "curr": "currency", "ccy": "currency",
        "prc": "price", "cost": "cost", "disc": "discount", "tax": "tax",
        
        # Product/Order
        "prod": "product", "prd": "product", "itm": "item", "sku": "stock_keeping_unit",
        "qty": "quantity", "qnty": "quantity", "ord": "order", "ordr": "order",
        "shp": "shipping", "ship": "shipping", "dlvry": "delivery", "del": "delivery",
        
        # Time/Date
        "dt": "date", "dte": "date", "ts": "timestamp", "tm": "time",
        "yr": "year", "mo": "month", "dy": "day", "hr": "hour", "min": "minute",
        "crt": "created", "crtd": "created", "upd": "updated", "mod": "modified",
        
        # Status/Type
        "sts": "status", "stat": "status", "typ": "type", "cat": "category",
        "grp": "group", "lvl": "level", "flg": "flag", "ind": "indicator",
        
        # IDs and Keys
        "id": "identifier", "pk": "primary_key", "fk": "foreign_key",
        "num": "number", "no": "number", "nbr": "number", "cd": "code",
        "ref": "reference", "seq": "sequence", "idx": "index",
        
        # Descriptions
        "desc": "description", "dsc": "description", "nm": "name", "txt": "text",
        "cmt": "comment", "cmnt": "comment", "nte": "note", "rmk": "remark",
        
        # Employee/HR
        "emp": "employee", "empl": "employee", "mgr": "manager", "supv": "supervisor",
        "dept": "department", "dpt": "department", "div": "division",
        "sal": "salary", "wage": "wage", "pos": "position", "ttl": "title",
        
        # Location
        "cty": "city", "st": "state", "prov": "province", "ctry": "country",
        "zip": "zip_code", "pstl": "postal", "rgn": "region", "loc": "location",
        
        # Misc
        "src": "source", "tgt": "target", "dest": "destination",
        "cnt": "count", "tot": "total", "avg": "average", "max": "maximum", "min": "minimum",
        "pct": "percent", "perc": "percentage", "rt": "rate", "rto": "ratio"
    }
    
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        
        # Initialize models
        self._init_bert_model()
        self._init_tfidf_model()
        self._init_llm_client()
        
        # Cache
        self._embedding_cache = {}
        self._llm_cache = {}
        
        logger.info(f"HybridAIEngine initialized with provider: {self.config.llm_provider.value}")
    
    def _init_bert_model(self):
        """Initialize BERT/Sentence Transformer model"""
        try:
            self.bert_model = SentenceTransformer(self.config.bert_model_name)
            logger.info(f"BERT model loaded: {self.config.bert_model_name}")
        except Exception as e:
            logger.warning(f"Failed to load BERT model: {e}")
            self.bert_model = None
    
    def _init_tfidf_model(self):
        """Initialize TF-IDF vectorizer"""
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            lowercase=True
        )
        self.tfidf_fitted = False
    
    def _init_llm_client(self):
        """Initialize LLM API client based on provider"""
        self.llm_available = False
        
        if self.config.llm_provider == LLMProvider.NONE:
            return
        
        if self.config.llm_provider == LLMProvider.OPENAI:
            if self.config.llm_api_key or os.getenv("OPENAI_API_KEY"):
                self.llm_api_key = self.config.llm_api_key or os.getenv("OPENAI_API_KEY")
                self.llm_base_url = "https://api.openai.com/v1"
                self.llm_available = True
                
        elif self.config.llm_provider == LLMProvider.AZURE_OPENAI:
            if self.config.llm_api_key or os.getenv("AZURE_OPENAI_API_KEY"):
                self.llm_api_key = self.config.llm_api_key or os.getenv("AZURE_OPENAI_API_KEY")
                self.llm_base_url = self.config.llm_base_url or os.getenv("AZURE_OPENAI_ENDPOINT")
                self.llm_available = True
                
        elif self.config.llm_provider == LLMProvider.OLLAMA:
            # Ollama runs locally, no API key needed
            self.llm_base_url = self.config.llm_base_url or "http://localhost:11434"
            self.llm_api_key = ""
            self.llm_available = self._check_ollama_available()
            
        elif self.config.llm_provider == LLMProvider.GROQ:
            if self.config.llm_api_key or os.getenv("GROQ_API_KEY"):
                self.llm_api_key = self.config.llm_api_key or os.getenv("GROQ_API_KEY")
                self.llm_base_url = "https://api.groq.com/openai/v1"
                self.llm_available = True
        
        if self.llm_available:
            logger.info(f"LLM API available: {self.config.llm_provider.value}")
        else:
            logger.warning(f"LLM API not available, using local models only")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = requests.get(f"{self.llm_base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations in column names"""
        # Split by common delimiters
        parts = re.split(r'[_\-\s]+', text.lower())
        expanded_parts = []
        
        for part in parts:
            if part in self.ABBREVIATIONS:
                expanded_parts.append(self.ABBREVIATIONS[part])
            else:
                expanded_parts.append(part)
        
        return ' '.join(expanded_parts)
    
    def get_bert_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for text with caching"""
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        if self.bert_model is None:
            return np.zeros(384)
        
        expanded = self.expand_abbreviations(text)
        embedding = self.bert_model.encode(expanded, convert_to_numpy=True)
        
        self._embedding_cache[text] = embedding
        return embedding
    
    def calculate_bert_similarity(self, source: str, target: str) -> float:
        """Calculate semantic similarity using BERT embeddings"""
        emb1 = self.get_bert_embedding(source)
        emb2 = self.get_bert_embedding(target)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
        return float(max(0, min(1, similarity)))
    
    def calculate_tfidf_similarity(self, source: str, target: str, 
                                   all_columns: List[str]) -> float:
        """Calculate TF-IDF based similarity"""
        try:
            # Fit on all columns if not already done
            if not self.tfidf_fitted:
                expanded_columns = [self.expand_abbreviations(c) for c in all_columns]
                self.tfidf_vectorizer.fit(expanded_columns)
                self.tfidf_fitted = True
            
            # Transform source and target
            src_expanded = self.expand_abbreviations(source)
            tgt_expanded = self.expand_abbreviations(target)
            
            src_vec = self.tfidf_vectorizer.transform([src_expanded])
            tgt_vec = self.tfidf_vectorizer.transform([tgt_expanded])
            
            similarity = cosine_similarity(src_vec, tgt_vec)[0][0]
            return float(max(0, min(1, similarity)))
        except Exception as e:
            logger.warning(f"TF-IDF error: {e}")
            return 0.0
    
    def calculate_domain_similarity(self, source: str, target: str) -> float:
        """Calculate domain-aware similarity using abbreviation matching"""
        src_expanded = self.expand_abbreviations(source)
        tgt_expanded = self.expand_abbreviations(target)
        
        # Fuzzy ratio on expanded versions
        fuzzy_score = fuzz.ratio(src_expanded, tgt_expanded) / 100.0
        
        # Token set ratio for word order independence
        token_score = fuzz.token_set_ratio(src_expanded, tgt_expanded) / 100.0
        
        # Partial ratio for substring matching
        partial_score = fuzz.partial_ratio(src_expanded, tgt_expanded) / 100.0
        
        # Weighted combination
        combined = 0.4 * fuzzy_score + 0.35 * token_score + 0.25 * partial_score
        
        return float(max(0, min(1, combined)))
    
    def get_llm_matching_score(self, source_cols: List[str], target_cols: List[str],
                                source_table: str = "", target_table: str = "") -> Dict[str, Dict]:
        """Use LLM to analyze and score column mappings"""
        if not self.llm_available:
            return {}
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{source_table}:{','.join(sorted(source_cols))}:{target_table}:{','.join(sorted(target_cols))}".encode()
        ).hexdigest()
        
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]
        
        prompt = self._build_llm_prompt(source_cols, target_cols, source_table, target_table)
        
        try:
            response = self._call_llm_api(prompt)
            result = self._parse_llm_response(response, source_cols, target_cols)
            self._llm_cache[cache_key] = result
            return result
        except Exception as e:
            logger.warning(f"LLM API error: {e}")
            return {}
    
    def _build_llm_prompt(self, source_cols: List[str], target_cols: List[str],
                          source_table: str, target_table: str) -> str:
        """Build prompt for LLM column matching"""
        return f"""You are a database migration expert. Analyze and match columns between source and target tables.

SOURCE TABLE: {source_table or 'source'}
SOURCE COLUMNS: {', '.join(source_cols)}

TARGET TABLE: {target_table or 'target'}
TARGET COLUMNS: {', '.join(target_cols)}

For each source column, identify the best matching target column. Consider:
1. Semantic meaning (what the column represents)
2. Naming conventions (abbreviations like cust=customer, addr=address)
3. Data type compatibility
4. Business context

Return your analysis as JSON with this exact format:
{{
    "mappings": [
        {{
            "source": "source_column_name",
            "target": "target_column_name",
            "confidence": 0.95,
            "reasoning": "Brief explanation of why this mapping is correct"
        }}
    ]
}}

Only include mappings you are confident about (>0.5 confidence).
If a source column has no good match, omit it from the response.
"""
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call the LLM API based on provider"""
        if self.config.llm_provider == LLMProvider.OLLAMA:
            return self._call_ollama(prompt)
        else:
            return self._call_openai_compatible(prompt)
    
    def _call_openai_compatible(self, prompt: str) -> str:
        """Call OpenAI-compatible API (OpenAI, Azure, Groq)"""
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.llm_model,
            "messages": [
                {"role": "system", "content": "You are a database migration expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{self.llm_base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama API"""
        data = {
            "model": self.config.llm_model or "llama3.2",
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{self.llm_base_url}/api/generate",
            json=data,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _parse_llm_response(self, response: str, source_cols: List[str], 
                           target_cols: List[str]) -> Dict[str, Dict]:
        """Parse LLM response into structured mappings"""
        result = {}
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
                
                for mapping in data.get("mappings", []):
                    src = mapping.get("source", "")
                    tgt = mapping.get("target", "")
                    
                    # Validate columns exist
                    if src in source_cols and tgt in target_cols:
                        result[f"{src}:{tgt}"] = {
                            "score": float(mapping.get("confidence", 0.5)),
                            "reasoning": mapping.get("reasoning", "")
                        }
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
        
        return result
    
    def match_columns(self, source_columns: List[Dict], target_columns: List[Dict],
                      source_table: str = "", target_table: str = "",
                      threshold: float = 0.4) -> List[MatchResult]:
        """
        Match columns using hybrid AI approach
        
        Args:
            source_columns: List of {"name": str, "type": str, ...}
            target_columns: List of {"name": str, "type": str, ...}
            source_table: Name of source table
            target_table: Name of target table
            threshold: Minimum ensemble score to include
            
        Returns:
            List of MatchResult with scores from all models
        """
        results = []
        
        # Extract column names
        src_names = [c["name"] if isinstance(c, dict) else c for c in source_columns]
        tgt_names = [c["name"] if isinstance(c, dict) else c for c in target_columns]
        all_names = src_names + tgt_names
        
        # Get LLM scores (batch for efficiency)
        llm_scores = {}
        if self.llm_available:
            llm_scores = self.get_llm_matching_score(
                src_names, tgt_names, source_table, target_table
            )
        
        # Calculate scores for all pairs
        for src_col in source_columns:
            src_name = src_col["name"] if isinstance(src_col, dict) else src_col
            best_match = None
            best_score = 0
            
            for tgt_col in target_columns:
                tgt_name = tgt_col["name"] if isinstance(tgt_col, dict) else tgt_col
                
                # Calculate individual model scores
                bert_score = self.calculate_bert_similarity(src_name, tgt_name)
                tfidf_score = self.calculate_tfidf_similarity(src_name, tgt_name, all_names)
                domain_score = self.calculate_domain_similarity(src_name, tgt_name)
                
                # Get LLM score if available
                llm_key = f"{src_name}:{tgt_name}"
                llm_data = llm_scores.get(llm_key, {"score": 0, "reasoning": ""})
                llm_score = llm_data.get("score", 0)
                llm_reasoning = llm_data.get("reasoning", "")
                
                # Calculate ensemble score
                if self.llm_available and llm_score > 0:
                    ensemble_score = (
                        self.config.bert_weight * bert_score +
                        self.config.llm_weight * llm_score +
                        self.config.tfidf_weight * tfidf_score +
                        self.config.domain_weight * domain_score
                    )
                    models_used = ["BERT", "LLM", "TF-IDF", "Domain"]
                else:
                    # Redistribute LLM weight when not available
                    adjusted_bert = self.config.bert_weight + self.config.llm_weight * 0.5
                    adjusted_domain = self.config.domain_weight + self.config.llm_weight * 0.5
                    
                    ensemble_score = (
                        adjusted_bert * bert_score +
                        self.config.tfidf_weight * tfidf_score +
                        adjusted_domain * domain_score
                    )
                    models_used = ["BERT", "TF-IDF", "Domain"]
                
                if ensemble_score > best_score:
                    best_score = ensemble_score
                    
                    # Determine confidence level
                    if ensemble_score >= 0.85:
                        confidence_level = "high"
                    elif ensemble_score >= 0.60:
                        confidence_level = "medium"
                    else:
                        confidence_level = "low"
                    
                    best_match = MatchResult(
                        source_column=src_name,
                        target_column=tgt_name,
                        source_table=source_table,
                        target_table=target_table,
                        bert_score=bert_score,
                        llm_score=llm_score,
                        tfidf_score=tfidf_score,
                        domain_score=domain_score,
                        ensemble_score=ensemble_score,
                        confidence_level=confidence_level,
                        llm_reasoning=llm_reasoning,
                        models_used=models_used
                    )
            
            if best_match and best_match.ensemble_score >= threshold:
                results.append(best_match)
        
        # Sort by ensemble score descending
        results.sort(key=lambda x: x.ensemble_score, reverse=True)
        
        return results
    
    def explain_matching(self, result: MatchResult) -> str:
        """Generate detailed explanation of matching decision"""
        explanation = f"""
## Column Mapping Analysis

**Source:** `{result.source_column}` → **Target:** `{result.target_column}`

### Model Scores

| Model | Score | Weight | Contribution |
|-------|-------|--------|--------------|
| BERT Semantic | {result.bert_score:.2%} | {self.config.bert_weight:.0%} | {result.bert_score * self.config.bert_weight:.2%} |
| LLM Reasoning | {result.llm_score:.2%} | {self.config.llm_weight:.0%} | {result.llm_score * self.config.llm_weight:.2%} |
| TF-IDF | {result.tfidf_score:.2%} | {self.config.tfidf_weight:.0%} | {result.tfidf_score * self.config.tfidf_weight:.2%} |
| Domain | {result.domain_score:.2%} | {self.config.domain_weight:.0%} | {result.domain_score * self.config.domain_weight:.2%} |

**Ensemble Score:** {result.ensemble_score:.2%} ({result.confidence_level.upper()} confidence)

### Models Used
{', '.join(result.models_used)}
"""
        
        if result.llm_reasoning:
            explanation += f"\n### LLM Reasoning\n{result.llm_reasoning}\n"
        
        return explanation


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_hybrid_engine(
    provider: str = "none",
    api_key: str = "",
    model: str = "",
    base_url: str = ""
) -> HybridAIEngine:
    """
    Factory function to create HybridAIEngine with specified provider
    
    Args:
        provider: "openai", "azure_openai", "ollama", "groq", "none"
        api_key: API key for the provider
        model: Model name to use
        base_url: Base URL for API (required for Azure/Ollama)
    """
    provider_map = {
        "openai": LLMProvider.OPENAI,
        "azure_openai": LLMProvider.AZURE_OPENAI,
        "ollama": LLMProvider.OLLAMA,
        "groq": LLMProvider.GROQ,
        "anthropic": LLMProvider.ANTHROPIC,
        "none": LLMProvider.NONE
    }
    
    config = ModelConfig(
        llm_provider=provider_map.get(provider.lower(), LLMProvider.NONE),
        llm_api_key=api_key,
        llm_model=model or "gpt-4o-mini",
        llm_base_url=base_url
    )
    
    return HybridAIEngine(config)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("HYBRID AI ENGINE TEST")
    print("=" * 60)
    
    # Test with local models only
    engine = create_hybrid_engine(provider="none")
    
    source_cols = [
        {"name": "cust_id", "type": "INTEGER"},
        {"name": "fname", "type": "VARCHAR"},
        {"name": "lname", "type": "VARCHAR"},
        {"name": "eml", "type": "VARCHAR"},
        {"name": "phn_num", "type": "VARCHAR"}
    ]
    
    target_cols = [
        {"name": "customer_identifier", "type": "BIGINT"},
        {"name": "first_name", "type": "VARCHAR"},
        {"name": "last_name", "type": "VARCHAR"},
        {"name": "email_address", "type": "VARCHAR"},
        {"name": "phone_number", "type": "VARCHAR"}
    ]
    
    results = engine.match_columns(
        source_cols, target_cols,
        source_table="legacy_customers",
        target_table="modern_customers"
    )
    
    print("\nMatching Results:")
    print("-" * 60)
    
    for r in results:
        print(f"{r.source_column:15} → {r.target_column:20} | Score: {r.ensemble_score:.2%} | {r.confidence_level}")
        print(f"  BERT: {r.bert_score:.2%} | TF-IDF: {r.tfidf_score:.2%} | Domain: {r.domain_score:.2%}")
    
    print("\nDetailed Explanation for first match:")
    if results:
        print(engine.explain_matching(results[0]))
