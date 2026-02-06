"""
=============================================================================
MODULE 5: VISUALIZATION ENGINE
=============================================================================
Purpose: Create visual representations of schema mappings and migrations
Features:
    - Sankey diagrams (source → target flow)
    - ER diagrams (entity relationships)
    - Mapping matrices (column-to-column)
    - Interactive hover details
=============================================================================
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class MappingVisualization:
    """Container for visualization data"""
    html: str
    json_data: Dict
    type: str  # "sankey", "er", "matrix", "heatmap"


class VisualizationEngine:
    """
    Create beautiful visualizations for data migration
    """
    
    # Color schemes
    COLORS = {
        "high_confidence": "#2ECC71",    # Green
        "medium_confidence": "#F1C40F",  # Yellow
        "low_confidence": "#E74C3C",     # Red
        "source": "#3498DB",             # Blue
        "target": "#9B59B6",             # Purple
        "connection": "#95A5A6",         # Gray
        "primary_key": "#E74C3C",        # Red
        "foreign_key": "#F39C12",        # Orange
    }
    
    def __init__(self):
        pass
    
    def create_sankey_diagram(self,
                             source_tables: List[str],
                             target_tables: List[str],
                             mappings: List[Dict],
                             title: str = "Data Migration Flow") -> MappingVisualization:
        """
        Create a Sankey diagram showing data flow from source to target
        
        Args:
            source_tables: List of source table names
            target_tables: List of target table names
            mappings: List of dicts with 'source', 'target', 'confidence'
        
        Returns:
            MappingVisualization with HTML and data
        """
        # Build nodes list: source tables + target tables
        all_nodes = source_tables + target_tables
        node_colors = (
            [self.COLORS["source"]] * len(source_tables) + 
            [self.COLORS["target"]] * len(target_tables)
        )
        
        # Build links
        source_indices = []
        target_indices = []
        values = []
        link_colors = []
        hover_texts = []
        
        for mapping in mappings:
            src_name = mapping.get("source_table", mapping.get("source", "").split(".")[0])
            tgt_name = mapping.get("target_table", mapping.get("target", "").split(".")[0])
            confidence = mapping.get("confidence", mapping.get("overall_score", 0.5))
            
            if src_name in source_tables and tgt_name in target_tables:
                source_indices.append(source_tables.index(src_name))
                target_indices.append(len(source_tables) + target_tables.index(tgt_name))
                values.append(max(1, int(confidence * 100)))
                
                # Color based on confidence
                if confidence >= 0.85:
                    link_colors.append(f"rgba(46, 204, 113, 0.6)")  # Green
                elif confidence >= 0.60:
                    link_colors.append(f"rgba(241, 196, 15, 0.6)")  # Yellow
                else:
                    link_colors.append(f"rgba(231, 76, 60, 0.6)")   # Red
                
                hover_texts.append(
                    f"{src_name} → {tgt_name}<br>Confidence: {confidence:.1%}"
                )
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=node_colors,
                hovertemplate='%{label}<extra></extra>'
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=link_colors,
                hovertemplate='%{customdata}<extra></extra>',
                customdata=hover_texts
            )
        )])
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20)),
            font=dict(size=12),
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
        
        return MappingVisualization(
            html=fig.to_html(include_plotlyjs=True, full_html=False),
            json_data={"nodes": all_nodes, "mappings": mappings},
            type="sankey"
        )
    
    def create_column_sankey(self,
                            source_columns: List[Dict],
                            target_columns: List[Dict],
                            column_mappings: List[Dict],
                            source_table: str = "Source",
                            target_table: str = "Target") -> MappingVisualization:
        """
        Create a Sankey diagram for column-level mappings
        
        Args:
            source_columns: List of dicts with 'name', 'type'
            target_columns: List of dicts with 'name', 'type'
            column_mappings: List of dicts with 'source_column', 'target_column', 'overall_score'
        """
        # Build nodes with column info
        src_labels = [f"{c['name']}\n({c.get('type', 'unknown')})" for c in source_columns]
        tgt_labels = [f"{c['name']}\n({c.get('type', 'unknown')})" for c in target_columns]
        
        all_nodes = src_labels + tgt_labels
        
        # Color code: PKs red, FKs orange, others blue/purple
        node_colors = []
        for c in source_columns:
            if c.get('is_primary_key'):
                node_colors.append(self.COLORS["primary_key"])
            elif c.get('is_foreign_key'):
                node_colors.append(self.COLORS["foreign_key"])
            else:
                node_colors.append(self.COLORS["source"])
        
        for c in target_columns:
            if c.get('is_primary_key'):
                node_colors.append(self.COLORS["primary_key"])
            elif c.get('is_foreign_key'):
                node_colors.append(self.COLORS["foreign_key"])
            else:
                node_colors.append(self.COLORS["target"])
        
        # Build links
        source_indices = []
        target_indices = []
        values = []
        link_colors = []
        hover_texts = []
        
        src_names = [c['name'] for c in source_columns]
        tgt_names = [c['name'] for c in target_columns]
        
        for mapping in column_mappings:
            src_col = mapping.get('source_column', '')
            tgt_col = mapping.get('target_column', '')
            score = mapping.get('overall_score', 0.5)
            
            if src_col in src_names and tgt_col in tgt_names:
                source_indices.append(src_names.index(src_col))
                target_indices.append(len(source_columns) + tgt_names.index(tgt_col))
                values.append(max(1, int(score * 100)))
                
                # Color based on score
                if score >= 0.85:
                    link_colors.append("rgba(46, 204, 113, 0.7)")
                elif score >= 0.60:
                    link_colors.append("rgba(241, 196, 15, 0.7)")
                else:
                    link_colors.append("rgba(231, 76, 60, 0.7)")
                
                explanation = mapping.get('explanation', '')
                hover_texts.append(
                    f"<b>{src_col}</b> → <b>{tgt_col}</b><br>"
                    f"Score: {score:.1%}<br>"
                    f"{explanation[:100]}"
                )
        
        fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            node=dict(
                pad=20,
                thickness=25,
                line=dict(color="black", width=0.5),
                label=all_nodes,
                color=node_colors,
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=values,
                color=link_colors,
                customdata=hover_texts,
                hovertemplate='%{customdata}<extra></extra>'
            )
        )])
        
        fig.update_layout(
            title=dict(
                text=f"Column Mapping: {source_table} → {target_table}",
                font=dict(size=18)
            ),
            font=dict(size=10),
            height=max(400, len(all_nodes) * 40),
            paper_bgcolor='white'
        )
        
        # Add legend
        fig.add_annotation(
            x=0, y=-0.1,
            xref='paper', yref='paper',
            text="🟢 High Confidence (>85%) | 🟡 Medium (60-85%) | 🔴 Low (<60%)",
            showarrow=False,
            font=dict(size=10)
        )
        
        return MappingVisualization(
            html=fig.to_html(include_plotlyjs=True, full_html=False),
            json_data={
                "source_columns": source_columns,
                "target_columns": target_columns,
                "mappings": column_mappings
            },
            type="sankey"
        )
    
    def create_mapping_heatmap(self,
                               source_columns: List[str],
                               target_columns: List[str],
                               similarity_matrix: List[List[float]],
                               title: str = "Column Similarity Matrix") -> MappingVisualization:
        """
        Create a heatmap showing similarity scores between all column pairs
        """
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=target_columns,
            y=source_columns,
            colorscale=[
                [0, '#E74C3C'],     # Red for low
                [0.5, '#F1C40F'],   # Yellow for medium
                [1, '#2ECC71']      # Green for high
            ],
            hovertemplate=(
                "Source: %{y}<br>"
                "Target: %{x}<br>"
                "Similarity: %{z:.2%}<extra></extra>"
            ),
            showscale=True,
            colorbar=dict(title="Similarity")
        ))
        
        fig.update_layout(
            title=title,
            xaxis=dict(title="Target Columns", tickangle=45),
            yaxis=dict(title="Source Columns"),
            height=max(400, len(source_columns) * 30 + 100),
            width=max(600, len(target_columns) * 30 + 100),
        )
        
        return MappingVisualization(
            html=fig.to_html(include_plotlyjs=True, full_html=False),
            json_data={
                "source_columns": source_columns,
                "target_columns": target_columns,
                "matrix": similarity_matrix
            },
            type="heatmap"
        )
    
    def create_er_diagram(self,
                         tables: List[Dict],
                         relationships: List[Dict]) -> MappingVisualization:
        """
        Create an ER diagram using NetworkX and Plotly
        
        Args:
            tables: List of dicts with 'name', 'columns'
            relationships: List of dicts with 'from_table', 'to_table', 'from_col', 'to_col'
        """
        G = nx.DiGraph()
        
        # Add nodes for tables
        for table in tables:
            G.add_node(table['name'], type='table')
        
        # Add edges for relationships
        for rel in relationships:
            G.add_edge(
                rel['from_table'],
                rel['to_table'],
                label=f"{rel.get('from_col', '')} → {rel.get('to_col', '')}"
            )
        
        # Calculate positions
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create edge traces
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create node traces
        node_x = []
        node_y = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # Get table info for hover
            table_info = next((t for t in tables if t['name'] == node), None)
            if table_info:
                cols = table_info.get('columns', [])
                col_text = "<br>".join([f"• {c['name']}: {c.get('type', 'unknown')}" 
                                       for c in cols[:10]])
                if len(cols) > 10:
                    col_text += f"<br>... and {len(cols) - 10} more"
                node_text.append(f"<b>{node}</b><br>{col_text}")
            else:
                node_text.append(node)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            hovertext=node_text,
            text=list(G.nodes()),
            textposition="bottom center",
            marker=dict(
                size=40,
                color=self.COLORS["source"],
                line=dict(width=2, color='white')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Entity Relationship Diagram",
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        return MappingVisualization(
            html=fig.to_html(include_plotlyjs=True, full_html=False),
            json_data={"tables": tables, "relationships": relationships},
            type="er"
        )
    
    def create_validation_dashboard(self,
                                   validation_results: List[Dict]) -> MappingVisualization:
        """
        Create a dashboard showing validation results
        """
        # Count by status
        status_counts = {}
        for r in validation_results:
            status = r.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Create pie chart for status
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "pie"}, {"type": "table"}]],
            column_widths=[0.4, 0.6]
        )
        
        colors = {
            'passed': '#2ECC71',
            'failed': '#E74C3C',
            'warning': '#F1C40F',
            'skipped': '#95A5A6'
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(status_counts.keys()),
                values=list(status_counts.values()),
                marker=dict(colors=[colors.get(s, '#888') for s in status_counts.keys()]),
                hole=0.4
            ),
            row=1, col=1
        )
        
        # Add table with details
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Check', 'Status', 'Severity', 'Message'],
                    fill_color='#3498DB',
                    font=dict(color='white'),
                    align='left'
                ),
                cells=dict(
                    values=[
                        [r.get('check_name', '') for r in validation_results],
                        [r.get('status', '') for r in validation_results],
                        [r.get('severity', '') for r in validation_results],
                        [r.get('message', '')[:50] for r in validation_results]
                    ],
                    align='left'
                )
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Validation Results Dashboard",
            height=500
        )
        
        return MappingVisualization(
            html=fig.to_html(include_plotlyjs=True, full_html=False),
            json_data={"results": validation_results, "summary": status_counts},
            type="dashboard"
        )


# =============================================================================
# TESTING / DEMO
# =============================================================================
if __name__ == "__main__":
    print("Visualization Engine Module Loaded")
    print("\nUsage:")
    print("  viz = VisualizationEngine()")
    print("  sankey = viz.create_sankey_diagram(source_tables, target_tables, mappings)")
    print("  # Save HTML: open('viz.html', 'w').write(sankey.html)")
