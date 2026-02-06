"""
=============================================================================
STREAMLIT UI: DATA MIGRATION PLATFORM
=============================================================================
Beautiful, interactive UI for the data migration platform.
Run with: streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
import json
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.schema_extractor import SchemaExtractor, DatabaseSchema
from src.semantic_matcher import SemanticMatcher
from src.type_mapper import DataTypeMapper
from src.validation_engine import ValidationEngine
from src.visualization import VisualizationEngine
from src.explainability import ExplainabilityEngine

# Page config
st.set_page_config(
    page_title="AI Data Migration Platform",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #2d4a6f;
    }
    .success-box {
        background-color: #0d3320;
        border: 1px solid #2ecc71;
        padding: 1rem;
        border-radius: 8px;
    }
    .warning-box {
        background-color: #3d2e0a;
        border: 1px solid #f39c12;
        padding: 1rem;
        border-radius: 8px;
    }
    .error-box {
        background-color: #3d0a0a;
        border: 1px solid #e74c3c;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if 'source_schema' not in st.session_state:
    st.session_state.source_schema = None
if 'target_schema' not in st.session_state:
    st.session_state.target_schema = None
if 'mappings' not in st.session_state:
    st.session_state.mappings = {}
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False


def main():
    # Header
    st.markdown('<h1 class="main-header">🔄 AI-Powered Data Migration Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888;">Intelligent Schema Mapping • Data Validation • Visual Migration Flow</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Database Selection")
        
        # Option to use sample data or upload
        data_source = st.radio(
            "Data Source",
            ["Use Sample Databases", "Upload Databases"]
        )
        
        if data_source == "Use Sample Databases":
            # Check if sample databases exist
            source_path = "data/source_legacy_crm.db"
            target_path = "data/target_modern_crm.db"
            
            if not os.path.exists(source_path) or not os.path.exists(target_path):
                st.warning("Sample databases not found!")
                if st.button("🔨 Create Sample Databases"):
                    from create_sample_data import create_sample_databases
                    create_sample_databases()
                    st.success("✅ Sample databases created!")
                    st.rerun()
            else:
                st.success(f"✅ Source: {source_path}")
                st.success(f"✅ Target: {target_path}")
                
        else:
            source_file = st.file_uploader("Upload Source Database", type=["db", "sqlite"])
            target_file = st.file_uploader("Upload Target Database", type=["db", "sqlite"])
            
            if source_file and target_file:
                # Save uploaded files
                os.makedirs("data/uploads", exist_ok=True)
                source_path = f"data/uploads/{source_file.name}"
                target_path = f"data/uploads/{target_file.name}"
                
                with open(source_path, "wb") as f:
                    f.write(source_file.getbuffer())
                with open(target_path, "wb") as f:
                    f.write(target_file.getbuffer())
                    
                st.success("Files uploaded!")
            else:
                source_path = None
                target_path = None
        
        st.divider()
        
        # Analysis settings
        st.header("⚙️ Settings")
        threshold = st.slider(
            "Matching Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Minimum confidence score for column matches"
        )
        
        st.divider()
        
        # Run analysis button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if data_source == "Use Sample Databases":
                source_path = "data/source_legacy_crm.db"
                target_path = "data/target_modern_crm.db"
            
            if source_path and target_path and os.path.exists(source_path) and os.path.exists(target_path):
                run_analysis(source_path, target_path, threshold)
            else:
                st.error("Please select valid databases first!")
    
    # Main content area
    if st.session_state.analysis_complete:
        display_results()
    else:
        display_welcome()


def display_welcome():
    """Display welcome screen before analysis"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🧠 AI-Powered Matching
        Uses semantic embeddings to match columns
        even with different naming conventions.
        
        `cust_id` ➡️ `customer_identifier`
        """)
    
    with col2:
        st.markdown("""
        ### ✅ Data Validation
        Comprehensive checks for data quality:
        - Null values
        - Duplicates
        - Referential integrity
        - Type compatibility
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Visual Mapping
        Interactive Sankey diagrams show
        the complete data flow from source
        to target databases.
        """)
    
    st.divider()
    
    st.markdown("""
    ### 🚀 Getting Started
    
    1. **Select databases** from the sidebar (use sample or upload your own)
    2. **Adjust threshold** for matching sensitivity
    3. **Click "Run Analysis"** to start the AI-powered migration analysis
    """)


def run_analysis(source_path: str, target_path: str, threshold: float):
    """Run the complete analysis pipeline"""
    
    progress = st.progress(0, text="Starting analysis...")
    
    try:
        # Step 1: Extract schemas
        progress.progress(10, text="Extracting source schema...")
        source_extractor = SchemaExtractor(source_path)
        st.session_state.source_schema = source_extractor.extract_schema()
        
        progress.progress(20, text="Extracting target schema...")
        target_extractor = SchemaExtractor(target_path)
        st.session_state.target_schema = target_extractor.extract_schema()
        
        # Step 2: Load AI model
        progress.progress(30, text="Loading AI model for semantic matching...")
        matcher = SemanticMatcher()
        
        # Step 3: Run matching
        progress.progress(50, text="Running AI-powered column matching...")
        st.session_state.mappings = matcher.match_schemas(
            st.session_state.source_schema,
            st.session_state.target_schema,
            threshold=threshold
        )
        
        # Step 4: Validation
        progress.progress(70, text="Running data validation...")
        validation_engine = ValidationEngine(source_path, target_path)
        
        all_validations = []
        for table in st.session_state.source_schema.tables:
            report = validation_engine.validate_pre_migration(table.name)
            all_validations.extend([r.to_dict() for r in report.results])
        
        st.session_state.validation_results = all_validations
        
        # Step 5: Complete
        progress.progress(100, text="Analysis complete!")
        st.session_state.analysis_complete = True
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_results():
    """Display analysis results"""
    
    # Summary metrics
    st.header("📊 Analysis Summary")
    
    total_mappings = sum(len(m) for m in st.session_state.mappings.values())
    high_conf = sum(
        1 for matches in st.session_state.mappings.values()
        for m in matches if m.overall_score >= 0.85
    )
    validation_passed = sum(
        1 for v in st.session_state.validation_results 
        if v.get('status') == 'passed'
    )
    validation_failed = sum(
        1 for v in st.session_state.validation_results 
        if v.get('status') == 'failed'
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Source Tables",
            len(st.session_state.source_schema.tables)
        )
    
    with col2:
        st.metric(
            "Target Tables",
            len(st.session_state.target_schema.tables)
        )
    
    with col3:
        st.metric(
            "Column Mappings",
            total_mappings,
            f"{high_conf} high confidence"
        )
    
    with col4:
        st.metric(
            "Validations",
            f"{validation_passed}✓ / {validation_failed}✗"
        )
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visualizations",
        "🔗 Column Mappings", 
        "✅ Validation Results",
        "📝 Migration SQL",
        "📄 Report"
    ])
    
    with tab1:
        display_visualizations()
    
    with tab2:
        display_mappings()
    
    with tab3:
        display_validations()
    
    with tab4:
        display_sql()
    
    with tab5:
        display_report()


def display_visualizations():
    """Display Sankey diagrams and other visualizations"""
    st.subheader("🔀 Data Flow Visualization")
    
    viz_engine = VisualizationEngine()
    
    # Create visualization for each table mapping
    for key, matches in st.session_state.mappings.items():
        if matches:
            st.markdown(f"### {key}")
            
            src_table_name = matches[0].source_table
            tgt_table_name = matches[0].target_table
            
            src_table = st.session_state.source_schema.get_table(src_table_name)
            tgt_table = st.session_state.target_schema.get_table(tgt_table_name)
            
            if src_table and tgt_table:
                source_cols = [
                    {
                        "name": c.name,
                        "type": c.data_type,
                        "is_primary_key": c.is_primary_key,
                        "is_foreign_key": c.is_foreign_key
                    }
                    for c in src_table.columns
                ]
                
                target_cols = [
                    {
                        "name": c.name,
                        "type": c.data_type,
                        "is_primary_key": c.is_primary_key,
                        "is_foreign_key": c.is_foreign_key
                    }
                    for c in tgt_table.columns
                ]
                
                sankey = viz_engine.create_column_sankey(
                    source_cols,
                    target_cols,
                    [m.to_dict() for m in matches],
                    source_table=src_table_name,
                    target_table=tgt_table_name
                )
                
                st.components.v1.html(sankey.html, height=500, scrolling=True)


def display_mappings():
    """Display column mappings in detail"""
    st.subheader("🔗 Column Mapping Details")
    
    for key, matches in st.session_state.mappings.items():
        if matches:
            with st.expander(f"📋 {key}", expanded=True):
                # Create dataframe
                df_data = []
                for m in matches:
                    confidence_color = "🟢" if m.overall_score >= 0.85 else "🟡" if m.overall_score >= 0.6 else "🔴"
                    df_data.append({
                        "Source Column": m.source_column,
                        "Target Column": m.target_column,
                        "Confidence": f"{confidence_color} {m.overall_score:.1%}",
                        "Semantic": f"{m.semantic_score:.1%}",
                        "Syntactic": f"{m.syntactic_score:.1%}",
                        "Type Match": f"{m.type_score:.1%}",
                        "Explanation": m.explanation[:50] + "..." if len(m.explanation) > 50 else m.explanation
                    })
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Warnings
                warnings = [w for m in matches for w in m.warnings if m.warnings]
                if warnings:
                    st.warning("⚠️ **Warnings:**\n" + "\n".join(f"- {w}" for w in warnings))


def display_validations():
    """Display validation results"""
    st.subheader("✅ Validation Results")
    
    # Group by status
    passed = [v for v in st.session_state.validation_results if v.get('status') == 'passed']
    failed = [v for v in st.session_state.validation_results if v.get('status') == 'failed']
    warnings = [v for v in st.session_state.validation_results if v.get('status') == 'warning']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"### ✅ Passed: {len(passed)}")
        for v in passed:
            st.markdown(f"- {v.get('check_name')}")
    
    with col2:
        st.warning(f"### ⚠️ Warnings: {len(warnings)}")
        for v in warnings:
            with st.expander(v.get('check_name')):
                st.write(v.get('message'))
                if v.get('recommendations'):
                    st.markdown("**Recommendations:**")
                    for r in v.get('recommendations', []):
                        st.markdown(f"- {r}")
    
    with col3:
        st.error(f"### ❌ Failed: {len(failed)}")
        for v in failed:
            with st.expander(v.get('check_name')):
                st.write(v.get('message'))
                st.json(v.get('details', {}))
                if v.get('recommendations'):
                    st.markdown("**Recommendations:**")
                    for r in v.get('recommendations', []):
                        st.markdown(f"- {r}")


def display_sql():
    """Display generated migration SQL"""
    st.subheader("📝 Generated Migration SQL")
    
    type_mapper = DataTypeMapper()
    
    all_sql = []
    
    for key, matches in st.session_state.mappings.items():
        if matches:
            src_table = matches[0].source_table
            tgt_table = matches[0].target_table
            
            sql = f"-- Migration: {src_table} → {tgt_table}\n"
            sql += f"INSERT INTO {tgt_table} (\n"
            sql += ",\n".join(f"    {m.target_column}" for m in matches)
            sql += "\n)\nSELECT\n"
            sql += ",\n".join(f"    {m.source_column} AS {m.target_column}" for m in matches)
            sql += f"\nFROM {src_table};\n"
            
            all_sql.append(sql)
    
    full_sql = "\n\n".join(all_sql)
    
    st.code(full_sql, language="sql")
    
    st.download_button(
        "📥 Download SQL",
        full_sql,
        file_name="migration.sql",
        mime="text/plain"
    )


def display_report():
    """Display and download full report"""
    st.subheader("📄 Migration Report")
    
    explainer = ExplainabilityEngine()
    
    # Generate explanations
    for key, matches in st.session_state.mappings.items():
        for m in matches:
            src_table = st.session_state.source_schema.get_table(m.source_table)
            tgt_table = st.session_state.target_schema.get_table(m.target_table)
            
            if src_table and tgt_table:
                src_col = next((c for c in src_table.columns if c.name == m.source_column), None)
                tgt_col = next((c for c in tgt_table.columns if c.name == m.target_column), None)
                
                if src_col and tgt_col:
                    explainer.explain_column_mapping(
                        source_col=m.source_column,
                        target_col=m.target_column,
                        semantic_score=m.semantic_score,
                        syntactic_score=m.syntactic_score,
                        type_score=m.type_score,
                        source_type=src_col.data_type,
                        target_type=tgt_col.data_type,
                        overall_score=m.overall_score
                    )
    
    report = explainer.generate_report(format="markdown")
    
    st.markdown(report)
    
    st.download_button(
        "📥 Download Report",
        report,
        file_name="migration_report.md",
        mime="text/markdown"
    )


if __name__ == "__main__":
    main()
