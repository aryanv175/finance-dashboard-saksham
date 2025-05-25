import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json
from plotly.utils import PlotlyJSONEncoder

class ChartGenerator:
    """Service for generating charts and visualizations"""
    
    def __init__(self):
        self.color_palette = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B', 
            '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
        ]
    
    def generate_all_charts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all charts for the dashboard"""
        charts = []
        
        # Extract data
        cases = data.get("cases", [])
        criteria = data.get("eligibility_criteria", [])
        
        if not cases:
            return charts
        
        # 1. Overall Score Distribution
        charts.append(self._create_score_distribution_chart(cases))
        
        # 2. Metrics Comparison Chart
        charts.append(self._create_metrics_comparison_chart(cases, criteria))
        
        # 3. Risk Level Distribution
        charts.append(self._create_risk_distribution_chart(cases))
        
        # 4. Top Performers Chart
        charts.append(self._create_top_performers_chart(cases))
        
        # 5. Metrics Radar Chart
        charts.append(self._create_radar_chart(cases, criteria))
        
        # 6. Trend Analysis (if time-based data exists)
        trend_chart = self._create_trend_chart(cases)
        if trend_chart:
            charts.append(trend_chart)
        
        return charts
    
    def _create_score_distribution_chart(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create overall score distribution histogram"""
        scores = []
        case_names = []
        
        for case in cases:
            if "overall_score" in case:
                scores.append(case["overall_score"])
                case_names.append(case.get("case_name", case.get("case_id", "Unknown")))
        
        fig = go.Figure()
        
        # Histogram
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=10,
            name="Score Distribution",
            marker_color=self.color_palette[0],
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Overall Score Distribution",
            xaxis_title="Score",
            yaxis_title="Number of Cases",
            template="plotly_white",
            height=400
        )
        
        return {
            "chart_type": "histogram",
            "title": "Overall Score Distribution",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _create_metrics_comparison_chart(self, cases: List[Dict[str, Any]], criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create metrics comparison bar chart"""
        if not cases or not criteria:
            return self._create_empty_chart("Metrics Comparison")
        
        # Get metric names from criteria
        metric_names = [c["metric_name"] for c in criteria]
        
        # Prepare data
        case_names = []
        metric_data = {metric: [] for metric in metric_names}
        
        for case in cases:
            case_name = case.get("case_name", case.get("case_id", "Unknown"))
            case_names.append(case_name)
            
            case_metrics = case.get("metrics", {})
            for metric in metric_names:
                # Find matching metric value
                value = self._find_metric_value(metric, case_metrics)
                metric_data[metric].append(value if value is not None else 0)
        
        fig = go.Figure()
        
        # Add bars for each metric
        for i, metric in enumerate(metric_names[:5]):  # Limit to 5 metrics for readability
            fig.add_trace(go.Bar(
                name=metric.title(),
                x=case_names,
                y=metric_data[metric],
                marker_color=self.color_palette[i % len(self.color_palette)]
            ))
        
        fig.update_layout(
            title="Metrics Comparison Across Cases",
            xaxis_title="Cases",
            yaxis_title="Values",
            barmode='group',
            template="plotly_white",
            height=500,
            xaxis_tickangle=-45
        )
        
        return {
            "chart_type": "bar",
            "title": "Metrics Comparison",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _create_risk_distribution_chart(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create risk level distribution pie chart"""
        risk_counts = {"Low": 0, "Medium": 0, "High": 0}
        
        for case in cases:
            risk_level = case.get("risk_level", "Medium")
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(risk_counts.keys()),
            values=list(risk_counts.values()),
            marker_colors=['#10B981', '#F59E0B', '#EF4444'],
            hole=0.4
        )])
        
        fig.update_layout(
            title="Risk Level Distribution",
            template="plotly_white",
            height=400
        )
        
        return {
            "chart_type": "pie",
            "title": "Risk Distribution",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _create_top_performers_chart(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create top performers horizontal bar chart"""
        # Sort cases by overall score
        sorted_cases = sorted(cases, key=lambda x: x.get("overall_score", 0), reverse=True)
        top_cases = sorted_cases[:10]  # Top 10
        
        case_names = [case.get("case_name", case.get("case_id", "Unknown")) for case in top_cases]
        scores = [case.get("overall_score", 0) for case in top_cases]
        grades = [case.get("grade", "F") for case in top_cases]
        
        # Color based on grade
        colors = []
        for grade in grades:
            if grade in ['A+', 'A']:
                colors.append('#10B981')  # Green
            elif grade in ['B+', 'B']:
                colors.append('#3B82F6')  # Blue
            elif grade in ['C+', 'C']:
                colors.append('#F59E0B')  # Yellow
            else:
                colors.append('#EF4444')  # Red
        
        fig = go.Figure(go.Bar(
            x=scores,
            y=case_names,
            orientation='h',
            marker_color=colors,
            text=[f"{score:.1f} ({grade})" for score, grade in zip(scores, grades)],
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Top Performing Cases",
            xaxis_title="Overall Score",
            yaxis_title="Cases",
            template="plotly_white",
            height=500
        )
        
        return {
            "chart_type": "horizontal_bar",
            "title": "Top Performers",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _create_radar_chart(self, cases: List[Dict[str, Any]], criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create radar chart for top 3 cases"""
        if not cases or not criteria:
            return self._create_empty_chart("Performance Radar")
        
        # Get top 3 cases
        sorted_cases = sorted(cases, key=lambda x: x.get("overall_score", 0), reverse=True)
        top_cases = sorted_cases[:3]
        
        # Get metric names
        metric_names = [c["metric_name"] for c in criteria[:6]]  # Limit to 6 metrics
        
        fig = go.Figure()
        
        for i, case in enumerate(top_cases):
            case_name = case.get("case_name", case.get("case_id", "Unknown"))
            
            # Get metric scores
            metric_scores = []
            for metric in metric_names:
                # Find metric score from case data
                score = 50  # Default
                if "metric_scores" in case:
                    for ms in case["metric_scores"]:
                        if ms["metric_name"].lower() == metric.lower():
                            score = ms["score"]
                            break
                metric_scores.append(score)
            
            fig.add_trace(go.Scatterpolar(
                r=metric_scores,
                theta=metric_names,
                fill='toself',
                name=case_name,
                line_color=self.color_palette[i]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Performance Comparison - Top 3 Cases",
            template="plotly_white",
            height=500
        )
        
        return {
            "chart_type": "radar",
            "title": "Performance Radar",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _create_trend_chart(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create trend chart if time-based data exists"""
        # Look for time-based metrics
        time_metrics = []
        for case in cases:
            metrics = case.get("metrics", {})
            for key in metrics.keys():
                if any(time_word in str(key).lower() for time_word in ['year', 'month', 'date', 'time']):
                    time_metrics.append(key)
                    break
        
        if not time_metrics:
            return None
        
        # Simple trend chart (placeholder)
        fig = go.Figure()
        
        # Add sample trend line
        years = [2021, 2022, 2023]
        avg_scores = [65, 72, 78]  # Sample data
        
        fig.add_trace(go.Scatter(
            x=years,
            y=avg_scores,
            mode='lines+markers',
            name='Average Score Trend',
            line=dict(color=self.color_palette[0], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Score Trend Over Time",
            xaxis_title="Year",
            yaxis_title="Average Score",
            template="plotly_white",
            height=400
        )
        
        return {
            "chart_type": "line",
            "title": "Trend Analysis",
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        }
    
    def _find_metric_value(self, metric_name: str, case_metrics: Dict[str, Any]) -> Any:
        """Find metric value in case data"""
        metric_lower = metric_name.lower()
        
        # Direct match
        if metric_lower in case_metrics:
            return case_metrics[metric_lower]
        
        # Fuzzy matching
        for key, value in case_metrics.items():
            if metric_lower in str(key).lower() or str(key).lower() in metric_lower:
                return value
        
        return None
    
    def _create_empty_chart(self, title: str) -> Dict[str, Any]:
        """Create empty chart placeholder"""
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=400,
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
        
        return {
            "chart_type": "empty",
            "title": title,
            "data": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
        } 