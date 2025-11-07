# chatbot/visualizer.py
"""
Professional Business Analytics Visualization Engine
Supports all major chart types for business data analysis
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Tuple, Optional, List

class AutoVisualizer:
    """Intelligent visualization suite with comprehensive chart type support."""

    def __init__(self):
        self.color_schemes = {
            'teal': px.colors.sequential.Teal,
            'blue': px.colors.sequential.Blues,
            'green': px.colors.sequential.Greens,
            'orange': px.colors.sequential.Oranges,
            'purple': px.colors.sequential.Purples,
            'viridis': px.colors.sequential.Viridis,
        }
        print("✓ Professional Business Visualizer is ready.")

    def create_chart(
        self,
        data: pd.DataFrame,
        question: str,
        intent: str,
        domain: str = 'general'
    ) -> Tuple[Optional[go.Figure], str]:
        """
        Intelligently select and create the best visualization for business analytics.
        """
        if data is None or data.empty:
            return None, "none"

        question_lower = question.lower()
        
        # Data structure analysis
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
        bool_cols = data.select_dtypes(include=['bool']).columns.tolist()

        if not numeric_cols:
            return self._create_table(data, domain), "table"

        # --- PRIORITIZE EXPLICIT USER REQUEST ---
        # Check for explicit chart type requests FIRST (before any automatic selection)
        pie_keywords = ['pie chart', 'piechart', 'pie', 'as a pie']
        donut_keywords = ['donut chart', 'donutchart', 'donut']
        bar_keywords = ['bar chart', 'barchart', 'bar graph']
        line_keywords = ['line chart', 'linegraph', 'line graph']
        area_keywords = ['area chart', 'areachart', 'area graph']
        
        # CRITICAL: Check for pie chart request FIRST and handle it specially
        if any(keyword in question_lower for keyword in pie_keywords):
            print(f"[Visualizer] User explicitly requested PIE chart. Forcing pie chart generation...")
            # For pie charts, we need categorical labels and numeric values
            # If we have date columns, we can aggregate by time period
            pie_result = None
            
            if date_cols and numeric_cols:
                # Aggregate time-series data for pie chart
                try:
                    # Try to aggregate by month or year
                    data_copy = data.copy()
                    date_col = date_cols[0]
                    numeric_col = numeric_cols[0]
                    
                    # Convert date column if needed
                    if not pd.api.types.is_datetime64_any_dtype(data_copy[date_col]):
                        data_copy[date_col] = pd.to_datetime(data_copy[date_col], errors='coerce')
                    
                    # Remove rows where date conversion failed
                    data_copy = data_copy.dropna(subset=[date_col])
                    
                    if len(data_copy) > 0:
                        # Aggregate by year
                        data_copy['year'] = data_copy[date_col].dt.year
                        aggregated = data_copy.groupby('year')[numeric_col].sum().reset_index()
                        aggregated.columns = ['category', 'value']
                        
                        if len(aggregated) > 0:
                            print(f"[Visualizer] Created pie chart from time-series data by aggregating by year")
                            pie_result = self._create_pie_chart(aggregated, 'category', 'value', 'teal'), "pie"
                except Exception as e:
                    print(f"[Visualizer] Error aggregating for pie chart: {e}")
                    import traceback
                    traceback.print_exc()
            
            # If we have categorical columns, use them directly
            if pie_result is None and categorical_cols and numeric_cols:
                try:
                    print(f"[Visualizer] User requested PIE chart. Using categorical columns...")
                    pie_result = self._create_pie_chart(data, categorical_cols[0], numeric_cols[0], 'teal'), "pie"
                except Exception as e:
                    print(f"[Visualizer] Error creating pie chart with categorical columns: {e}")
            
            # If we only have numeric columns, try to create categories from the data
            if pie_result is None and numeric_cols and len(data) > 0:
                try:
                    # Create a pie chart using the first numeric column as values
                    # and row indices or a generated category column as labels
                    data_copy = data.copy()
                    numeric_col = numeric_cols[0]
                    
                    # If we have multiple rows, aggregate or use top N
                    if len(data_copy) > 10:
                        # Take top 10 by value
                        data_copy = data_copy.nlargest(10, numeric_col)
                    
                    # Create labels from index or first column
                    if len(data_copy.columns) > 1:
                        # Use first non-numeric column as labels
                        label_col = [c for c in data_copy.columns if c != numeric_col][0]
                        data_copy['category'] = data_copy[label_col].astype(str)
                    else:
                        # Use index as labels
                        data_copy['category'] = data_copy.index.astype(str)
                    
                    print(f"[Visualizer] User requested PIE chart. Created from numeric data...")
                    pie_result = self._create_pie_chart(data_copy, 'category', numeric_col, 'teal'), "pie"
                except Exception as e:
                    print(f"[Visualizer] Error creating pie chart from numeric data: {e}")
                    import traceback
                    traceback.print_exc()
            
            # If we successfully created a pie chart, return it
            if pie_result is not None:
                return pie_result
            else:
                # If all attempts failed, log warning but still try to create something
                print(f"[Visualizer] WARNING: Failed to create pie chart as requested. Falling back to automatic selection.")
        
        chart_type_map = {
            'donut chart': ('donut', self._create_donut_chart),
            'donutchart': ('donut', self._create_donut_chart),
            'bar chart': ('bar', self._create_bar_chart),
            'barchart': ('bar', self._create_bar_chart),
            'horizontal bar': ('bar', lambda d, x, y, c, dom: self._create_bar_chart(d, x, y, c, dom, horizontal=True)),
            'line chart': ('line', self._create_line_chart),
            'line graph': ('line', self._create_line_chart),
            'area chart': ('area', self._create_area_chart),
            'areachart': ('area', self._create_area_chart),
            'scatter plot': ('scatter', self._create_scatter),
            'scatterplot': ('scatter', self._create_scatter),
            'heatmap': ('heatmap', self._create_heatmap),
            'treemap': ('treemap', self._create_treemap),
            'waterfall': ('waterfall', self._create_waterfall),
            'box plot': ('box', self._create_box_plot),
            'boxplot': ('box', self._create_box_plot),
            'violin plot': ('violin', self._create_violin_plot),
            'funnel': ('funnel', self._create_funnel_chart),
            'gauge': ('gauge', self._create_gauge_chart),
        }

        for keyword, (chart_type, chart_func) in chart_type_map.items():
            if keyword in question_lower:
                if chart_type == 'donut' and categorical_cols and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, categorical_cols[0], numeric_cols[0], 'teal'), chart_type
                elif chart_type == 'bar' and categorical_cols and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    horizontal = 'horizontal' in question_lower
                    return chart_func(data, categorical_cols[0], numeric_cols[0], 'teal', domain, horizontal), chart_type
                elif chart_type == 'line' and (date_cols or categorical_cols) and numeric_cols:
                    x_col = date_cols[0] if date_cols else categorical_cols[0]
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, x_col, numeric_cols[0], 'teal', domain), chart_type
                elif chart_type == 'area' and (date_cols or categorical_cols) and numeric_cols:
                    x_col = date_cols[0] if date_cols else categorical_cols[0]
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, x_col, numeric_cols[0], 'teal', domain), chart_type
                elif chart_type == 'scatter' and len(numeric_cols) >= 2:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, numeric_cols[0], numeric_cols[1], 'viridis'), chart_type
                elif chart_type == 'heatmap' and len(categorical_cols) >= 2 and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, categorical_cols[0], categorical_cols[1], numeric_cols[0]), chart_type
                elif chart_type == 'treemap' and categorical_cols and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, categorical_cols[0], numeric_cols[0]), chart_type
                elif chart_type == 'box' and categorical_cols and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, categorical_cols[0], numeric_cols[0]), chart_type
                elif chart_type == 'violin' and categorical_cols and numeric_cols:
                    print(f"[Visualizer] User requested {chart_type} chart. Generating...")
                    return chart_func(data, categorical_cols[0], numeric_cols[0]), chart_type

        # --- AUTOMATIC SELECTION BASED ON DATA AND INTENT ---
        print("[Visualizer] Automatically selecting the best chart type...")

        # 1. Time series / Trends
        if date_cols and numeric_cols:
            if 'trend' in question_lower or 'over time' in question_lower:
                if len(numeric_cols) == 1:
                    return self._create_line_chart(data, date_cols[0], numeric_cols[0], 'teal', domain), "line"
                else:
                    return self._create_multi_line_chart(data, date_cols[0], numeric_cols, 'teal'), "line"
            elif 'cumulative' in question_lower or 'total' in question_lower:
                return self._create_area_chart(data, date_cols[0], numeric_cols[0], 'teal', domain), "area"
            else:
                return self._create_line_chart(data, date_cols[0], numeric_cols[0], 'teal', domain), "line"
        
        # 2. Composition / Distribution (few categories)
        if any(word in question_lower for word in ['share', 'percentage', 'proportion', 'distribution', 'breakdown']):
            if len(data) <= 15:
                if 'donut' in question_lower:
                    return self._create_donut_chart(data, categorical_cols[0], numeric_cols[0], 'teal'), "donut"
                return self._create_pie_chart(data, categorical_cols[0], numeric_cols[0], 'teal'), "pie"
            elif len(data) <= 50:
                return self._create_treemap(data, categorical_cols[0], numeric_cols[0]), "treemap"
        
        # 3. Correlation / Relationship
        if len(numeric_cols) >= 2 and len(data) > 10:
            if 'correlation' in question_lower or 'relationship' in question_lower:
                return self._create_scatter(data, numeric_cols[0], numeric_cols[1], 'viridis'), "scatter"
        
        # 4. Comparison / Ranking
        if categorical_cols and numeric_cols:
            data_len = len(data)
            if data_len <= 20:
                # Bar chart for comparison
                if 'top' in question_lower or 'best' in question_lower or 'highest' in question_lower:
                    return self._create_bar_chart(data, categorical_cols[0], numeric_cols[0], 'teal', domain), "bar"
                elif 'bottom' in question_lower or 'worst' in question_lower or 'lowest' in question_lower:
                    return self._create_bar_chart(data, categorical_cols[0], numeric_cols[0], 'teal', domain), "bar"
                else:
                    return self._create_bar_chart(data, categorical_cols[0], numeric_cols[0], 'teal', domain), "bar"
            elif data_len > 20 and data_len <= 100:
                # Treemap for many categories
                return self._create_treemap(data, categorical_cols[0], numeric_cols[0]), "treemap"
            else:
                # Heatmap for very large datasets
                if len(categorical_cols) >= 2:
                    return self._create_heatmap(data, categorical_cols[0], categorical_cols[1], numeric_cols[0]), "heatmap"
        
        # 5. Statistical distribution
        if categorical_cols and numeric_cols and len(data) > 30:
            if 'distribution' in question_lower or 'spread' in question_lower:
                return self._create_box_plot(data, categorical_cols[0], numeric_cols[0]), "box"
        
        # 6. Default: Bar chart
        if categorical_cols and numeric_cols:
            return self._create_bar_chart(data, categorical_cols[0], numeric_cols[0], 'teal', domain), "bar"
        
        # 7. Final fallback: Table
        return self._create_table(data, domain), "table"

    # === CHART IMPLEMENTATIONS ===

    def _create_bar_chart(self, data: pd.DataFrame, x_col: str, y_col: str, color_scheme: str, domain: str, horizontal: bool = False) -> go.Figure:
        """Create a professional bar chart."""
        data_sorted = data.nlargest(30, y_col) if len(data) > 30 else data
        if horizontal:
            fig = px.bar(
                data_sorted, 
                x=y_col, 
                y=x_col, 
                orientation='h',
                title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                color=y_col,
                color_continuous_scale=self.color_schemes.get(color_scheme, self.color_schemes['teal']),
                text_auto=True
            )
        else:
            fig = px.bar(
                data_sorted, 
                x=x_col, 
                y=y_col,
                title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                color=y_col,
                color_continuous_scale=self.color_schemes.get(color_scheme, self.color_schemes['teal']),
                text_auto=True
            )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-45 if not horizontal else 0,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_pie_chart(self, data: pd.DataFrame, labels_col: str, values_col: str, color_scheme: str) -> go.Figure:
        """Create a pie chart."""
        if len(data) > 10:
            top_data = data.nlargest(9, values_col)
            others_sum = data.nsmallest(len(data) - 9, values_col)[values_col].sum()
            others_row = pd.DataFrame({labels_col: ['Others'], values_col: [others_sum]})
            data = pd.concat([top_data, others_row], ignore_index=True)
        
        fig = px.pie(
            data, 
            names=labels_col, 
            values=values_col,
            title=f"{values_col.replace('_', ' ').title()} Distribution",
            color_discrete_sequence=self.color_schemes.get(color_scheme, self.color_schemes['teal'])
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_donut_chart(self, data: pd.DataFrame, labels_col: str, values_col: str, color_scheme: str) -> go.Figure:
        """Create a donut chart."""
        if len(data) > 10:
            top_data = data.nlargest(9, values_col)
            others_sum = data.nsmallest(len(data) - 9, values_col)[values_col].sum()
            others_row = pd.DataFrame({labels_col: ['Others'], values_col: [others_sum]})
            data = pd.concat([top_data, others_row], ignore_index=True)
        
        fig = px.pie(
            data,
            names=labels_col,
            values=values_col,
            title=f"{values_col.replace('_', ' ').title()} Distribution",
            hole=0.4,  # Creates donut effect
            color_discrete_sequence=self.color_schemes.get(color_scheme, self.color_schemes['teal'])
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_line_chart(self, data: pd.DataFrame, x_col: str, y_col: str, color_scheme: str, domain: str) -> go.Figure:
        """Create a line chart for trends."""
        data_sorted = data.sort_values(by=x_col)
        fig = px.line(
            data_sorted,
            x=x_col,
            y=y_col,
            title=f"{y_col.replace('_', ' ').title()} Trend Over Time",
            markers=True,
            line_shape='spline'
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            xaxis_tickangle=-45,
            height=500
        )
        return fig

    def _create_area_chart(self, data: pd.DataFrame, x_col: str, y_col: str, color_scheme: str, domain: str) -> go.Figure:
        """Create an area chart for cumulative trends."""
        data_sorted = data.sort_values(by=x_col)
        fig = px.area(
            data_sorted,
            x=x_col,
            y=y_col,
            title=f"{y_col.replace('_', ' ').title()} Over Time",
            color_discrete_sequence=self.color_schemes.get(color_scheme, self.color_schemes['teal'])
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            xaxis_tickangle=-45,
            height=500
        )
        return fig

    def _create_multi_line_chart(self, data: pd.DataFrame, x_col: str, y_cols: List[str], color_scheme: str) -> go.Figure:
        """Create a multi-line chart for comparing multiple metrics."""
        data_sorted = data.sort_values(by=x_col)
        fig = go.Figure()
        for col in y_cols[:5]:  # Limit to 5 series
            fig.add_trace(go.Scatter(
                x=data_sorted[x_col],
                y=data_sorted[col],
                mode='lines+markers',
                name=col.replace('_', ' ').title(),
                line=dict(width=2)
            ))
        fig.update_layout(
            title="Multiple Metrics Comparison",
            xaxis_title=x_col.replace('_', ' ').title(),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500,
            hovermode='x unified'
        )
        return fig

    def _create_scatter(self, data: pd.DataFrame, x_col: str, y_col: str, color_scheme: str, size_col: Optional[str] = None) -> go.Figure:
        """Create a scatter plot for correlation analysis."""
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            size=size_col,
            title=f"Relationship between {y_col.replace('_', ' ').title()} and {x_col.replace('_', ' ').title()}",
            color=y_col,
            color_continuous_scale=self.color_schemes.get(color_scheme, self.color_schemes['viridis']),
            trendline="ols"
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_heatmap(self, data: pd.DataFrame, x_col: str, y_col: str, values_col: str) -> go.Figure:
        """Create a heatmap for two-dimensional data."""
        pivot_data = data.pivot_table(values=values_col, index=y_col, columns=x_col, aggfunc='sum', fill_value=0)
        fig = px.imshow(
            pivot_data,
            labels=dict(x=x_col.replace('_', ' ').title(), y=y_col.replace('_', ' ').title(), color=values_col.replace('_', ' ').title()),
            title=f"Heatmap: {values_col.replace('_', ' ').title()}",
            color_continuous_scale='Viridis',
            aspect='auto'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_treemap(self, data: pd.DataFrame, labels_col: str, values_col: str) -> go.Figure:
        """Create a treemap for hierarchical data."""
        if len(data) > 50:
            data = data.nlargest(50, values_col)
        fig = px.treemap(
            data,
            path=[labels_col],
            values=values_col,
            title=f"{values_col.replace('_', ' ').title()} Treemap",
            color=values_col,
            color_continuous_scale='Teal'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_waterfall(self, data: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Create a waterfall chart for cumulative changes."""
        data_sorted = data.sort_values(by=x_col)
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute"] + ["relative"] * (len(data_sorted) - 2) + ["total"],
            x=data_sorted[x_col],
            textposition="outside",
            text=data_sorted[y_col],
            y=data_sorted[y_col],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        fig.update_layout(
            title=f"Waterfall Chart: {y_col.replace('_', ' ').title()}",
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_box_plot(self, data: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Create a box plot for distribution analysis."""
        fig = px.box(
            data,
            x=x_col,
            y=y_col,
            title=f"Distribution of {y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
            color_discrete_sequence=self.color_schemes['teal']
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            xaxis_tickangle=-45,
            height=500
        )
        return fig

    def _create_violin_plot(self, data: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Create a violin plot for distribution analysis."""
        fig = px.violin(
            data,
            x=x_col,
            y=y_col,
            title=f"Distribution Analysis: {y_col.replace('_', ' ').title()}",
            color_discrete_sequence=self.color_schemes['teal']
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            xaxis_tickangle=-45,
            height=500
        )
        return fig

    def _create_funnel_chart(self, data: pd.DataFrame, labels_col: str, values_col: str) -> go.Figure:
        """Create a funnel chart for process analysis."""
        data_sorted = data.sort_values(by=values_col, ascending=False)
        fig = go.Figure(go.Funnel(
            y=data_sorted[labels_col],
            x=data_sorted[values_col],
            textposition="inside",
            textinfo="value+percent initial"
        ))
        fig.update_layout(
            title=f"Funnel Analysis: {values_col.replace('_', ' ').title()}",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            height=500
        )
        return fig

    def _create_gauge_chart(self, data: pd.DataFrame, labels_col: str, values_col: str) -> go.Figure:
        """Create a gauge chart for KPI visualization."""
        if len(data) == 1:
            value = data[values_col].iloc[0]
            max_val = value * 1.5  # Set max to 150% of current value
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': data[labels_col].iloc[0] if labels_col else "Metric"},
                delta={'reference': max_val * 0.8},
                gauge={
                    'axis': {'range': [None, max_val]},
                    'bar': {'color': "teal"},
                    'steps': [
                        {'range': [0, max_val * 0.5], 'color': "lightgray"},
                        {'range': [max_val * 0.5, max_val * 0.8], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_val * 0.9
                    }
                }
            ))
            fig.update_layout(height=400)
            return fig
        else:
            # If multiple values, create a bar chart instead
            return self._create_bar_chart(data, labels_col, values_col, 'teal', 'general')

    def _create_table(self, data: pd.DataFrame, domain: str) -> go.Figure:
        """Create a table visualization."""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(data.columns),
                fill_color='#0d9488',
                align='left',
                font=dict(color='white', size=12),
                height=40
            ),
            cells=dict(
                values=[data[col].astype(str) for col in data.columns],
                fill_color=['white', '#f0fdfa'],
                align='left',
                font=dict(size=11),
                height=30
            )
        )])
        fig.update_layout(
            title=f"Data Table ({domain.title()} Domain)",
            height=min(600, len(data) * 30 + 150),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        return fig
