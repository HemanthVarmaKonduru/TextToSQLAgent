"""
Visualization utilities for the Airlines Text-to-SQL Agent.
Handles data visualization and chart generation.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Optional

class DataVisualizer:
    """Static class for creating data visualizations."""
    
    @staticmethod
    def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create a bar chart."""
        fig = px.bar(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True
        )
        return fig
    
    @staticmethod
    def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create a line chart."""
        fig = px.line(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True
        )
        return fig
    
    @staticmethod
    def create_scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, color_col: str = None, title: str = None) -> go.Figure:
        """Create a scatter plot."""
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True
        )
        return fig
    
    @staticmethod
    def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str = None) -> go.Figure:
        """Create a pie chart."""
        fig = px.pie(df, names=names_col, values=values_col, title=title)
        fig.update_layout(showlegend=True)
        return fig
    
    @staticmethod
    def create_histogram(df: pd.DataFrame, x_col: str, title: str = None) -> go.Figure:
        """Create a histogram."""
        fig = px.histogram(df, x=x_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title="Count",
            showlegend=False
        )
        return fig
    
    @staticmethod
    def create_box_plot(df: pd.DataFrame, x_col: str, y_col: str, title: str = None) -> go.Figure:
        """Create a box plot."""
        fig = px.box(df, x=x_col, y=y_col, title=title)
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=False
        )
        return fig
    
    @staticmethod
    def auto_create_visualizations(df: pd.DataFrame, query: str, suggestions: List[str]) -> Dict[str, go.Figure]:
        """
        Automatically create visualizations based on data and suggestions.
        
        Args:
            df: DataFrame with data
            query: Original user query
            suggestions: List of suggested visualization types
            
        Returns:
            Dictionary of visualization names and figures
        """
        visualizations = {}
        
        if df.empty:
            return visualizations
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Create visualizations based on suggestions and data
        for suggestion in suggestions:
            suggestion = suggestion.lower().strip()
            
            try:
                if 'bar' in suggestion and len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    # Bar chart for categorical vs numeric
                    x_col = categorical_cols[0]
                    y_col = numeric_cols[0]
                    visualizations['bar_chart'] = DataVisualizer.create_bar_chart(
                        df, x_col, y_col, f"{y_col} by {x_col}"
                    )
                
                elif 'line' in suggestion and len(numeric_cols) >= 2:
                    # Line chart for numeric trends
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                    visualizations['line_chart'] = DataVisualizer.create_line_chart(
                        df, x_col, y_col, f"{y_col} vs {x_col}"
                    )
                
                elif 'scatter' in suggestion and len(numeric_cols) >= 2:
                    # Scatter plot for numeric relationships
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                    color_col = categorical_cols[0] if categorical_cols else None
                    visualizations['scatter_plot'] = DataVisualizer.create_scatter_plot(
                        df, x_col, y_col, color_col, f"{y_col} vs {x_col}"
                    )
                
                elif 'pie' in suggestion and len(categorical_cols) > 0:
                    # Pie chart for categorical distribution
                    names_col = categorical_cols[0]
                    # Create value counts for pie chart
                    value_counts = df[names_col].value_counts().reset_index()
                    value_counts.columns = [names_col, 'count']
                    visualizations['pie_chart'] = DataVisualizer.create_pie_chart(
                        value_counts, names_col, 'count', f"Distribution of {names_col}"
                    )
                
                elif 'histogram' in suggestion and len(numeric_cols) > 0:
                    # Histogram for numeric distribution
                    x_col = numeric_cols[0]
                    visualizations['histogram'] = DataVisualizer.create_histogram(
                        df, x_col, f"Distribution of {x_col}"
                    )
                
                elif 'box' in suggestion and len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    # Box plot for categorical vs numeric
                    x_col = categorical_cols[0]
                    y_col = numeric_cols[0]
                    visualizations['box_plot'] = DataVisualizer.create_box_plot(
                        df, x_col, y_col, f"{y_col} by {x_col}"
                    )
                
            except Exception as e:
                print(f"Error creating {suggestion} visualization: {e}")
                continue
        
        # If no visualizations were created, create some default ones
        if not visualizations:
            if len(numeric_cols) > 0:
                # Create histogram of first numeric column
                visualizations['histogram'] = DataVisualizer.create_histogram(
                    df, numeric_cols[0], f"Distribution of {numeric_cols[0]}"
                )
            
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                # Create bar chart
                visualizations['bar_chart'] = DataVisualizer.create_bar_chart(
                    df, categorical_cols[0], numeric_cols[0], f"{numeric_cols[0]} by {categorical_cols[0]}"
                )
        
        return visualizations 