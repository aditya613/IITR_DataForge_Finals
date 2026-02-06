# 🔄 AI-Powered Intelligent Data Migration Platform

> **Track 2 Solution - DataForge Finals 2024, IIT Roorkee**

A comprehensive, AI-powered data migration platform that intelligently maps database schemas using local machine learning models, provides interactive visualizations, and ensures data integrity throughout the migration process.

---

## 🎯 Problem Statement Coverage

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| AI-based column matching | ✅ Complete | `semantic_matcher.py` - Local embeddings |
| Support different naming conventions | ✅ Complete | 50+ abbreviation mappings + semantic similarity |
| 1:1, 1:N, N:1 mappings | ✅ Complete | `migration_executor.py` - AdvancedMigrationExecutor |
| Data type transformations | ✅ Complete | `type_mapper.py` - TypeTransformation class |
| Validation & integrity checks | ✅ Complete | `validation_engine.py` - Comprehensive checks |
| Failed records with reasons | ✅ Complete | `migration_executor.py` - FailedRecord tracking |
| Visual representation (Sankey) | ✅ Complete | `visualization.py` - Interactive Plotly charts |
| Explainability (non-technical) | ✅ Complete | `simple_explainer.py` - Plain English explanations |
| No external API dependency | ✅ Complete | All models run locally |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT WEB UI (app.py)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Visualizations│ │  Mappings   │ │ Validations │ │ Execution │ │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                         CORE MODULES                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ schema_extractor │→│ semantic_matcher  │→│  type_mapper  │ │
│  │   (DB Schema)    │  │ (AI Matching)     │  │ (Transform)   │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │validation_engine │  │  visualization   │  │explainability │ │
│  │  (Data Quality)  │  │(Sankey Diagrams) │  │(Why/How)      │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │migration_executor│  │ simple_explainer │                    │
│  │(Execute + Track) │  │(Business Users)  │                    │
│  └──────────────────┘  └──────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│              LOCAL AI MODEL (sentence-transformers)             │
│              Model: all-MiniLM-L6-v2 (22M params)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd PS2
pip install -r requirements.txt
```

### 2. Create Sample Databases

```bash
python create_sample_data.py
```

### 3. Launch the Platform

```bash
streamlit run app.py
```

### 4. Open in Browser

Navigate to `http://localhost:8501`

---

## 📁 Project Structure

```
PS2/
├── app.py                      # 🎨 Streamlit Web UI
├── main.py                     # 🔧 CLI Orchestrator
├── create_sample_data.py       # 📊 Sample Database Generator
├── requirements.txt            # 📦 Dependencies
├── README.md                   # 📖 This file
│
├── src/
│   ├── schema_extractor.py     # 🔍 Database schema extraction
│   ├── semantic_matcher.py     # 🧠 AI-powered column matching
│   ├── type_mapper.py          # 🔄 Data type transformations
│   ├── validation_engine.py    # ✅ Data integrity validation
│   ├── visualization.py        # 📊 Sankey diagrams & charts
│   ├── explainability.py       # 💡 Technical explanations
│   ├── migration_executor.py   # ⚡ Safe migration execution
│   └── simple_explainer.py     # 📋 Non-technical explanations
│
└── data/
    ├── source_legacy_crm.db    # 📁 Source database (sample)
    └── target_modern_crm.db    # 📁 Target database (sample)
```

---

## 🧠 AI/ML Approach

### Local Embedding Model

We use **sentence-transformers** with the `all-MiniLM-L6-v2` model:
- 🔒 **100% Local** - No API calls, no internet required
- ⚡ **Fast** - 22M parameters, runs on CPU
- 📐 **384-dimensional** embeddings

### Matching Algorithm

```
Overall Score = (0.50 × Semantic) + (0.30 × Syntactic) + (0.20 × Type)
```

| Component | Method | Purpose |
|-----------|--------|---------|
| **Semantic** | Cosine similarity of embeddings | Meaning-based matching |
| **Syntactic** | RapidFuzz ratio | Character-level similarity |
| **Type** | Compatibility matrix | Data type alignment |

### Abbreviation Expansion

Built-in mapping of 50+ common abbreviations:
- `cust` → `customer`
- `addr` → `address`
- `qty` → `quantity`
- `amt` → `amount`
- And many more...

---

## 🎨 Features

### 1. Interactive Visualizations

- **Sankey Diagrams**: Show data flow from source to target
- **Confidence Distribution**: Histogram of match confidence scores
- **Relationship Types**: Bar chart of 1:1, 1:N, N:1 mappings
- **Complete Dashboard**: Overview of all migration metrics

### 2. Validation Engine

Pre-migration checks:
- ✅ Null value analysis
- ✅ Duplicate detection
- ✅ Orphan record detection
- ✅ Type compatibility
- ✅ Foreign key integrity

### 3. Explainability

Two modes:
- **Technical**: Detailed scores, algorithms used
- **Non-Technical**: Plain English for business users

Example non-technical explanation:
> "The column 'cust_id' from the old system will become 'customer_identifier' 
> in the new system. We're 92% confident this is correct because they both 
> represent the unique customer number."

### 4. Failed Records Tracking

Every failed record is captured with:
- Record ID
- Error type
- Error message
- Original data
- Suggested fix

---

## 📊 UI Screenshots

The Streamlit app provides 7 tabs:

1. **📊 Visualizations** - Interactive Sankey diagrams
2. **🔗 Column Mappings** - Detailed match information
3. **✅ Validation Results** - Data quality checks
4. **📝 Migration SQL** - Generated SQL statements
5. **🚀 Execute Migration** - Run migration with progress
6. **📋 Simple Explanations** - Business-friendly reports
7. **📄 Report** - Full technical documentation

---

## 🔧 Configuration

### Matching Threshold

Adjust in the sidebar (default: 0.4):
- **Higher** (0.7+): Only very confident matches
- **Lower** (0.3): More matches, may need review

### Batch Size

For migration execution (default: 100):
- Smaller batches = Better error tracking
- Larger batches = Faster migration

---

## 🧪 Testing

Run the sample workflow:

```bash
# Create sample databases
python create_sample_data.py

# Run CLI analysis
python main.py

# Or launch the web UI
streamlit run app.py
```

---

## 📈 Sample Databases

The sample data simulates a CRM migration:

### Source (Legacy CRM)
- `customers` table with abbreviations (`cust_id`, `fname`, `lname`)
- `orders` table with legacy naming
- `order_items` with old conventions

### Target (Modern CRM)
- `customers` with full names (`customer_id`, `first_name`)
- `orders` with modern naming
- `order_items` with new conventions

---

## 🏆 Judging Criteria Alignment

| Criteria | Our Solution |
|----------|--------------|
| **Innovation** | Local AI embeddings without external APIs |
| **Technical Complexity** | Multi-signal matching, batch migration |
| **Completeness** | All PS2 requirements covered |
| **UI/UX** | Modern Streamlit interface with 7 tabs |
| **Explainability** | Dual-mode (technical + business) |
| **Visualization** | Interactive Plotly Sankey diagrams |

---

## 👥 Team

**DataForge Finals 2024 - IIT Roorkee**

---

## 📝 License

MIT License - Built for DataForge Finals 2024
