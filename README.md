# 🔄 AI-Powered Data Migration Platform

**Track 2: Intelligent Data Migration Intelligence**  
*DataForge Finals - IIT Roorkee*

---

## 🎯 Problem Statement

Migrating data between databases is error-prone due to different schemas, renamed columns, changed data types, and complex constraints. Traditional methods rely on hard-coded scripts and manual schema comparison, which are difficult to audit.

## ✨ Our Solution

An **AI-powered system** that:
- Understands schema meaning using semantic embeddings (NO external APIs!)
- Suggests intelligent column mappings
- Validates data integrity
- Visualizes the migration process with interactive Sankey diagrams
- Explains every decision for full transparency

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA MIGRATION PLATFORM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   SOURCE     │    │   MAPPING    │    │   TARGET     │       │
│  │   DATABASE   │───▶│   ENGINE     │───▶│   DATABASE   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   SCHEMA     │    │   AI/ML      │    │  VALIDATION  │       │
│  │   EXTRACTOR  │    │   MATCHER    │    │   ENGINE     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                             │                                    │
│                             ▼                                    │
│         ┌──────────────────────────────────────┐                │
│         │   VISUALIZATION + EXPLAINABILITY     │                │
│         └──────────────────────────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Sample Databases

```bash
python create_sample_data.py
```

### 3. Launch the UI

```bash
streamlit run app.py
```

### 4. Or use CLI

```bash
python main.py data/source_legacy_crm.db data/target_modern_crm.db
```

---

## 📁 Project Structure

```
DataForge_Finals/
├── app.py                    # 🎨 Streamlit UI
├── main.py                   # 🎯 Main orchestrator
├── create_sample_data.py     # 📦 Sample database creator
├── requirements.txt          # 📋 Dependencies
├── README.md                 # 📖 Documentation
│
├── src/                      # 🔧 Core modules
│   ├── __init__.py
│   ├── schema_extractor.py   # Extract DB schemas
│   ├── semantic_matcher.py   # AI column matching
│   ├── type_mapper.py        # Data type transformations
│   ├── validation_engine.py  # Data integrity checks
│   ├── visualization.py      # Sankey diagrams
│   └── explainability.py     # Human-readable explanations
│
├── data/                     # 📂 Database files
│   ├── source_legacy_crm.db
│   └── target_modern_crm.db
│
└── output/                   # 📊 Generated outputs
    ├── table_sankey.html
    ├── report.md
    └── migration.sql
```

---

## 🧠 AI/ML Components (100% Custom - No APIs!)

### Semantic Matching

We use **local sentence-transformers** for semantic similarity:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')  # Runs locally!

# Embed column names
source_embedding = model.encode("customer_id")
target_embedding = model.encode("cust_id")

# Compute similarity
similarity = cosine_similarity(source_embedding, target_embedding)
```

### Multi-Signal Matching

Our matching combines three signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| **Semantic** | 50% | Embedding similarity (meaning) |
| **Syntactic** | 30% | Fuzzy string matching (spelling) |
| **Type** | 20% | Data type compatibility |

### Abbreviation Expansion

Built-in dictionary for common database abbreviations:

```python
ABBREVIATIONS = {
    "cust": "customer",
    "prod": "product", 
    "qty": "quantity",
    "amt": "amount",
    "dt": "date",
    "ts": "timestamp",
    # ... 50+ more
}
```

---

## 📊 Features

### 1. Schema Extraction
- Automatic table/column discovery
- Primary key & foreign key detection
- Sample value extraction
- Row count statistics

### 2. Intelligent Mapping
- Semantic similarity using embeddings
- Handles abbreviations and synonyms
- Data type compatibility checks
- Confidence scoring (0-100%)

### 3. Validation Engine
- Row count verification
- Null value detection
- Duplicate detection
- Referential integrity checks
- Pre/post migration comparison

### 4. Visualization (MANDATORY)
- **Sankey Diagrams**: Show data flow source → target
- **Column Mapping View**: Detailed per-table mappings
- **Heatmap**: Similarity matrix for all column pairs
- **Validation Dashboard**: Pass/fail visualization

### 5. Explainability
- Human-readable explanations for every mapping
- "Why was Column A mapped to Column B?"
- Confidence breakdown (semantic/syntactic/type)
- Warnings for potential issues
- Recommendations for manual review

---

## 🔧 Module Details

### `schema_extractor.py`
```python
extractor = SchemaExtractor("database.db")
schema = extractor.extract_schema()

# Access tables
for table in schema.tables:
    print(f"Table: {table.name}")
    for col in table.columns:
        print(f"  - {col.name}: {col.data_type}")
```

### `semantic_matcher.py`
```python
matcher = SemanticMatcher()
matches = matcher.match_columns(source_table, target_table)

for match in matches:
    print(f"{match.source_column} → {match.target_column}")
    print(f"  Score: {match.overall_score:.1%}")
    print(f"  Explanation: {match.explanation}")
```

### `validation_engine.py`
```python
engine = ValidationEngine("source.db", "target.db")
report = engine.validate_pre_migration("customers")

for result in report.results:
    print(f"{result.status}: {result.message}")
```

### `visualization.py`
```python
viz = VisualizationEngine()
sankey = viz.create_column_sankey(
    source_columns, 
    target_columns,
    mappings
)
# Save as HTML
with open("sankey.html", "w") as f:
    f.write(sankey.html)
```

---

## 👥 Team Division (4 Members)

| Member | Modules | Time |
|--------|---------|------|
| **P1** | `schema_extractor.py` + `semantic_matcher.py` | 8-10 hrs |
| **P2** | `type_mapper.py` + `validation_engine.py` | 6-8 hrs |
| **P3** | `visualization.py` (Sankey diagrams) | 6-8 hrs |
| **P4** | `app.py` (Streamlit UI) + `explainability.py` | 8-10 hrs |

---

## 📈 Evaluation Criteria

| Criteria | How We Address It |
|----------|-------------------|
| **Intelligent Mapping** | ✅ AI embeddings + multi-signal matching |
| **Validation** | ✅ Comprehensive pre/post migration checks |
| **Visualization** | ✅ Interactive Sankey diagrams |
| **Explainability** | ✅ Human-readable explanations for every decision |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **sentence-transformers** - Local embeddings (no API!)
- **scikit-learn** - Cosine similarity
- **rapidfuzz** - Fuzzy string matching
- **Plotly** - Interactive visualizations
- **Streamlit** - Web UI
- **SQLite** - Sample databases
- **Pandas** - Data manipulation

---

## 📝 Sample Output

### Column Mapping
```
cust_id → customer_id
  ✅ Score: 92%
  ✅ Semantic: 95% (names have similar meanings)
  ✅ Syntactic: 85% (abbreviation detected: cust → customer)
  ✅ Type: 100% (INTEGER → INTEGER)
```

### Validation Report
```
✅ Row Count Check: 5 rows
⚠️ Null Value Check: 1 column has NULLs
✅ Duplicate Check: No duplicates found
✅ Referential Integrity: All FKs valid
```

---

## 🏆 Why This Solution Wins

1. **No External APIs** - 100% local, works offline
2. **Comprehensive** - Covers all deliverables
3. **Beautiful UI** - Impressive demo
4. **Explainable** - Every decision is justified
5. **Production Ready** - Clean, modular code

---

## 📜 License

MIT License - Built for DataForge Finals @ IIT Roorkee

---

**Good luck with the hackathon! 🚀**