import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
import json
import tempfile
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.schema_extractor import SchemaExtractor, DatabaseSchema
from src.semantic_matcher import SemanticMatcher
from src.type_mapper import DataTypeMapper
from src.validation_engine import ValidationEngine
from src.visualization import VisualizationEngine
from src.explainability import ExplainabilityEngine
from src.migration_executor import MigrationExecutor, MigrationResult
from src.simple_explainer import SimpleExplainer

st.set_page_config(
    page_title="AI Data Migration Platform",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .simple-explanation {
        background-color: #1a1a2e;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .confidence-high { color: #2ecc71; font-weight: bold; }
    .confidence-medium { color: #f1c40f; font-weight: bold; }
    .confidence-low { color: #e74c3c; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


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
if 'migration_result' not in st.session_state:
    st.session_state.migration_result = None
if 'source_path' not in st.session_state:
    st.session_state.source_path = None
if 'target_path' not in st.session_state:
    st.session_state.target_path = None


def main():
    st.markdown('<h1 class="main-header">🔄 AI-Powered Data Migration Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #888;">Intelligent Schema Mapping • Data Validation • Visual Migration Flow</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📁 Database Selection")
        data_source = st.radio(
            "Data Source",
            ["Use Sample Databases", "Upload Databases"]
        )
        
        if data_source == "Use Sample Databases":
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
        st.header("⚙️ Settings")
        threshold = st.slider(
            "Matching Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Minimum confidence score for column matches"
        )
        
        explanation_mode = st.selectbox(
            "Explanation Mode",
            ["Technical", "Non-Technical (Business)"],
            help="Choose how explanations are presented"
        )
        st.session_state.explanation_mode = explanation_mode
        
        st.divider()
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if data_source == "Use Sample Databases":
                source_path = "data/source_legacy_crm.db"
                target_path = "data/target_modern_crm.db"
            
            if source_path and target_path and os.path.exists(source_path) and os.path.exists(target_path):
                st.session_state.source_path = source_path
                st.session_state.target_path = target_path
                run_analysis(source_path, target_path, threshold)
            else:
                st.error("Please select valid databases first!")
    
    if st.session_state.analysis_complete:
        display_results()
    else:
        display_welcome()


def display_welcome():
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
    progress = st.progress(0, text="Starting analysis...")
    
    try:
        progress.progress(10, text="Extracting source schema...")
        source_extractor = SchemaExtractor(source_path)
        st.session_state.source_schema = source_extractor.extract_schema()
        
        progress.progress(20, text="Extracting target schema...")
        target_extractor = SchemaExtractor(target_path)
        st.session_state.target_schema = target_extractor.extract_schema()
        progress.progress(30, text="Loading AI model for semantic matching...")
        matcher = SemanticMatcher()
        progress.progress(50, text="Running AI-powered column matching...")
        st.session_state.mappings = matcher.match_schemas(
            st.session_state.source_schema,
            st.session_state.target_schema,
            threshold=threshold
        )
        progress.progress(70, text="Running data validation...")
        validation_engine = ValidationEngine(source_path, target_path)
        
        all_validations = []
        for table in st.session_state.source_schema.tables:
            report = validation_engine.validate_pre_migration(table.name)
            all_validations.extend([r.to_dict() for r in report.results])
        
        st.session_state.validation_results = all_validations
        progress.progress(100, text="Analysis complete!")
        st.session_state.analysis_complete = True
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_results():
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Visualizations",
        "🔗 Column Mappings", 
        "✅ Validation Results",
        "📝 Migration SQL",
        "🚀 Execute Migration",
        "📋 Simple Explanations",
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
        display_migration_executor()
    
    with tab6:
        display_simple_explanations()
    
    with tab7:
        display_report()


def display_visualizations():
    st.subheader("🔀 Data Flow Visualization")
    
    viz_engine = VisualizationEngine()
    viz_mode = st.selectbox(
        "Select Visualization",
        ["Sankey Diagram (Data Flow)", "Confidence Distribution", "Mapping Relationship Types", "Complete Dashboard"]
    )
    
    if viz_mode == "Sankey Diagram (Data Flow)":
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
    
    elif viz_mode == "Confidence Distribution":
        all_mappings = []
        for matches in st.session_state.mappings.values():
            all_mappings.extend([m.to_dict() for m in matches])
        
        if all_mappings:
            conf_viz = viz_engine.create_confidence_distribution(all_mappings)
            st.components.v1.html(conf_viz.html, height=450, scrolling=True)
        else:
            st.info("No mappings available for visualization")
    
    elif viz_mode == "Mapping Relationship Types":
        all_mappings = []
        for matches in st.session_state.mappings.values():
            all_mappings.extend([m.to_dict() for m in matches])
        mapped_source = set()
        mapped_target = set()
        for matches in st.session_state.mappings.values():
            for m in matches:
                mapped_source.add(m.source_column)
                mapped_target.add(m.target_column)
        
        unmapped_source = []
        for table in st.session_state.source_schema.tables:
            for col in table.columns:
                if col.name not in mapped_source:
                    unmapped_source.append(col.name)
        
        unmapped_target = []
        for table in st.session_state.target_schema.tables:
            for col in table.columns:
                if col.name not in mapped_target:
                    unmapped_target.append(col.name)
        
        rel_viz = viz_engine.create_mapping_relationship_diagram(
            all_mappings, unmapped_source, unmapped_target
        )
        st.components.v1.html(rel_viz.html, height=450, scrolling=True)
    
    elif viz_mode == "Complete Dashboard":
        all_mappings = []
        for matches in st.session_state.mappings.values():
            all_mappings.extend([m.to_dict() for m in matches])
        
        migration_stats = st.session_state.migration_result or {
            'records_migrated': 0,
            'records_failed': 0
        }
        
        dashboard = viz_engine.create_complete_dashboard(
            all_mappings,
            st.session_state.validation_results,
            migration_stats
        )
        st.components.v1.html(dashboard.html, height=750, scrolling=True)


def display_mappings():
    st.subheader("🔗 Column Mapping Details")
    
    for key, matches in st.session_state.mappings.items():
        if matches:
            with st.expander(f"📋 {key}", expanded=True):
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
                warnings = [w for m in matches for w in m.warnings if m.warnings]
                if warnings:
                    st.warning("⚠️ **Warnings:**\n" + "\n".join(f"- {w}" for w in warnings))


def display_validations():
    st.subheader("✅ Validation Results")
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
    st.subheader("📄 Migration Report")
    explainer = ExplainabilityEngine()
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


def display_migration_executor():
    st.subheader("🚀 Migration Execution")
    st.warning("⚠️ **CAUTION**: This will actually migrate data from source to target database!")
    if not st.session_state.source_path or not st.session_state.target_path:
        st.error("Please run analysis first!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Migration Settings")
        batch_size = st.number_input("Batch Size", min_value=10, max_value=10000, value=100)
        use_transaction = st.checkbox("Use Transactions (Recommended)", value=True)
        stop_on_error = st.checkbox("Stop on First Error", value=False)
    
    with col2:
        st.markdown("### Rollback Options")
        create_backup = st.checkbox("Create Backup Before Migration", value=True)
        
    if st.button("⚡ Execute Migration", type="primary"):
        execute_migration(batch_size, use_transaction, stop_on_error)
    if st.session_state.migration_result:
        result = st.session_state.migration_result
        
        st.divider()
        st.markdown("### 📊 Migration Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Records Migrated", result.get('records_migrated', 0))
        with col2:
            st.metric("❌ Records Failed", result.get('records_failed', 0))
        with col3:
            total = result.get('records_migrated', 0) + result.get('records_failed', 0)
            success_rate = (result.get('records_migrated', 0) / total * 100) if total > 0 else 0
            st.metric("📈 Success Rate", f"{success_rate:.1f}%")
        with col4:
            st.metric("⏱️ Duration", f"{result.get('duration', 0):.2f}s")
        if result.get('failed_records'):
            st.markdown("### ❌ Failed Records")
            
            simple_explainer = SimpleExplainer()
            
            for record in result.get('failed_records', [])[:10]:
                with st.expander(f"Record ID: {record.get('record_id', 'Unknown')}"):
                    st.error(f"**Error**: {record.get('error_message', 'Unknown error')}")
                    explanation = simple_explainer.explain_failed_record(
                        record_id=str(record.get('record_id', 'Unknown')),
                        error_type=record.get('error_type', 'Unknown'),
                        error_message=record.get('error_message', ''),
                        source_table=record.get('source_table', ''),
                        source_data=record.get('original_data', {})
                    )
                    
                    st.markdown(f"<div class='simple-explanation'>{explanation.plain_english}</div>", 
                               unsafe_allow_html=True)
                    
                    if record.get('original_data'):
                        st.json(record.get('original_data'))
            
            if len(result.get('failed_records', [])) > 10:
                st.info(f"Showing first 10 of {len(result.get('failed_records', []))} failed records")


def execute_migration(batch_size: int, use_transaction: bool, stop_on_error: bool):
    progress = st.progress(0, text="Preparing migration...")
    
    try:
        executor = MigrationExecutor(
            st.session_state.source_path,
            st.session_state.target_path
        )
        
        total_migrated = 0
        total_failed = 0
        all_failed_records = []
        start_time = datetime.now()
        
        mapping_keys = list(st.session_state.mappings.keys())
        
        for idx, key in enumerate(mapping_keys):
            matches = st.session_state.mappings[key]
            if not matches:
                continue
            
            progress_pct = int((idx + 1) / len(mapping_keys) * 100)
            progress.progress(progress_pct, text=f"Migrating {key}...")
            
            src_table = matches[0].source_table
            tgt_table = matches[0].target_table
            column_mappings = {m.source_column: m.target_column for m in matches}
            
            result = executor.migrate_table(
                source_table=src_table,
                target_table=tgt_table,
                column_mappings=column_mappings,
                batch_size=batch_size,
                use_transaction=use_transaction
            )
            
            total_migrated += result.records_migrated
            total_failed += result.records_failed
            all_failed_records.extend([fr.to_dict() for fr in result.failed_records])
        
        duration = (datetime.now() - start_time).total_seconds()
        
        st.session_state.migration_result = {
            'records_migrated': total_migrated,
            'records_failed': total_failed,
            'failed_records': all_failed_records,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        progress.progress(100, text="Migration complete!")
        
        if total_failed == 0:
            st.success(f"✅ Migration completed successfully! {total_migrated} records migrated.")
        else:
            st.warning(f"⚠️ Migration completed with issues. {total_migrated} migrated, {total_failed} failed.")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Migration error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())


def display_simple_explanations():
    st.subheader("📋 Simple Explanations (For Non-Technical Users)")
    
    st.markdown("""
    This section explains the data migration in plain English, suitable for 
    business stakeholders who may not have a technical background.
    """)
    
    simple_explainer = SimpleExplainer()
    st.markdown("### 📊 Executive Summary")
    
    total_mappings = sum(len(m) for m in st.session_state.mappings.values())
    high_conf = sum(
        1 for matches in st.session_state.mappings.values()
        for m in matches if m.overall_score >= 0.85
    )
    med_conf = sum(
        1 for matches in st.session_state.mappings.values()
        for m in matches if 0.6 <= m.overall_score < 0.85
    )
    low_conf = sum(
        1 for matches in st.session_state.mappings.values()
        for m in matches if m.overall_score < 0.6
    )
    
    summary = simple_explainer.generate_executive_summary(
        total_columns_mapped=total_mappings,
        high_confidence_mappings=high_conf,
        medium_confidence_mappings=med_conf,
        low_confidence_mappings=low_conf,
        total_source_tables=len(st.session_state.source_schema.tables),
        total_target_tables=len(st.session_state.target_schema.tables)
    )
    
    st.markdown(f"""
    <div class='simple-explanation'>
        <h4>{summary.heading}</h4>
        <p>{summary.plain_english}</p>
        {"<p><strong>Details:</strong> " + summary.details + "</p>" if summary.details else ""}
    </div>
    """, unsafe_allow_html=True    )
    st.markdown("### 🔗 Column Mapping Explanations")
    
    for key, matches in st.session_state.mappings.items():
        if matches:
            with st.expander(f"📋 {key}", expanded=False):
                for m in matches:
                    explanation = simple_explainer.explain_column_mapping(
                        source_col=m.source_column,
                        target_col=m.target_column,
                        confidence=m.overall_score,
                        source_type=m.source_column,  # Would need actual type
                        target_type=m.target_column,
                        transformation_needed="Type conversion" if m.type_score < 1.0 else None
                    )
                    
                    conf_class = "confidence-high" if m.overall_score >= 0.85 else \
                                "confidence-medium" if m.overall_score >= 0.6 else "confidence-low"
                    
                    st.markdown(f"""
                    <div class='simple-explanation'>
                        <strong>{explanation.heading}</strong><br>
                        <span class='{conf_class}'>{m.overall_score:.0%} Confidence</span><br>
                        <p>{explanation.plain_english}</p>
                        <small>💡 {explanation.analogy}</small>
                    </div>
                    """, unsafe_allow_html=True)
    st.markdown("### ⚠️ Items Needing Attention")
    mapped_source_cols = set()
    for matches in st.session_state.mappings.values():
        for m in matches:
            mapped_source_cols.add(f"{m.source_table}.{m.source_column}")
    
    has_unmapped = False
    for table in st.session_state.source_schema.tables:
        for col in table.columns:
            full_name = f"{table.name}.{col.name}"
            if full_name not in mapped_source_cols:
                has_unmapped = True
                explanation = simple_explainer.explain_unmapped_column(
                    column_name=col.name,
                    table_name=table.name,
                    column_type=col.data_type,
                    is_source=True,
                    suggested_action="Review if this data needs to be migrated"
                )
                st.warning(f"🔸 {explanation.plain_english}")
    
    if not has_unmapped:
        st.success("✅ All source columns have been successfully mapped!")
    st.divider()
    if st.button("📥 Download Business Summary Report"):
        report = f"""
# Data Migration Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary
{summary.plain_english}

## Key Statistics
- Total column mappings identified: {total_mappings}
- High confidence (automatic): {high_conf}
- Medium confidence (review recommended): {med_conf}
- Low confidence (manual review required): {low_conf}

## What This Means for Your Business
Our AI system has analyzed your source database and identified how each piece of data 
should be transferred to the new system. The higher the confidence score, the more 
certain we are that the mapping is correct.

## Recommendations
1. Review any mappings with less than 60% confidence before proceeding
2. Verify that all critical business data has been mapped
3. Test the migration on a small sample before full execution

## Next Steps
- Approve the proposed mappings
- Schedule migration during off-peak hours
- Have a rollback plan ready
        """
        
        st.download_button(
            "📥 Download Report",
            report,
            file_name="business_migration_summary.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
