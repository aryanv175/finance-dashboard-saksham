import numpy as np
from typing import Dict, List, Any
import pandas as pd

class VisualizationService:
    def __init__(self):
        self.color_palette = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B',
            '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'
        ]
    
    def generate_dashboard_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive dashboard data from analysis results"""
        results = analysis_results.get("results", [])
        summary = analysis_results.get("summary", {})
        
        if not results:
            return self._empty_dashboard_data()
        
        return {
            "total_cases": summary.get("total_cases", 0),
            "eligible_cases": summary.get("eligible_cases", 0),
            "average_score": summary.get("average_score", 0),
            "score_distribution": self._create_score_distribution_chart(summary.get("score_distribution", {})),
            "eligibility_breakdown": self._create_eligibility_breakdown_chart(results),
            "parameter_analysis": self._create_parameter_analysis_chart(results),
            "score_trends": self._create_score_trends_chart(results),
            "top_performers": summary.get("top_performers", [])[:5],
            "score_stats": summary.get("score_stats", {})
        }
    
    def _create_score_distribution_chart(self, score_distribution: Dict[str, int]) -> Dict[str, Any]:
        """Create score distribution chart data"""
        labels = list(score_distribution.keys())
        values = list(score_distribution.values())
        
        return {
            "type": "bar",
            "labels": labels,
            "datasets": [{
                "label": "Number of Cases",
                "data": values,
                "backgroundColor": self.color_palette[:len(labels)],
                "borderColor": self.color_palette[:len(labels)],
                "borderWidth": 1
            }]
        }
    
    def _create_eligibility_breakdown_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create eligibility status breakdown pie chart"""
        status_counts = {}
        for result in results:
            status = result.get("eligibility_status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        labels = list(status_counts.keys())
        values = list(status_counts.values())
        
        return {
            "type": "pie",
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": self.color_palette[:len(labels)],
                "borderWidth": 2,
                "borderColor": "#ffffff"
            }]
        }
    
    def _create_parameter_analysis_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create parameter-wise performance analysis"""
        if not results:
            return {"type": "bar", "labels": [], "datasets": []}
        
        # Collect all parameters
        all_parameters = set()
        for result in results:
            all_parameters.update(result.get("individual_scores", {}).keys())
        
        parameter_averages = {}
        for param in all_parameters:
            scores = []
            for result in results:
                individual_scores = result.get("individual_scores", {})
                if param in individual_scores:
                    scores.append(individual_scores[param])
            
            if scores:
                parameter_averages[param] = np.mean(scores)
        
        # Sort by average score
        sorted_params = sorted(parameter_averages.items(), key=lambda x: x[1], reverse=True)
        
        labels = [param for param, _ in sorted_params]
        values = [score for _, score in sorted_params]
        
        return {
            "type": "horizontalBar",
            "labels": labels,
            "datasets": [{
                "label": "Average Score",
                "data": values,
                "backgroundColor": self.color_palette[0],
                "borderColor": self.color_palette[0],
                "borderWidth": 1
            }]
        }
    
    def _create_score_trends_chart(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create score trends line chart"""
        # Sort results by case_id for consistent ordering
        sorted_results = sorted(results, key=lambda x: x.get("case_id", ""))
        
        labels = [result.get("case_id", f"Case {i+1}") for i, result in enumerate(sorted_results)]
        scores = [result.get("percentage", 0) for result in sorted_results]
        
        return {
            "type": "line",
            "labels": labels,
            "datasets": [{
                "label": "Score Percentage",
                "data": scores,
                "borderColor": self.color_palette[0],
                "backgroundColor": f"{self.color_palette[0]}20",
                "borderWidth": 2,
                "fill": True,
                "tension": 0.4
            }]
        }
    
    def create_comparison_chart(self, results: List[Dict[str, Any]], parameter: str) -> Dict[str, Any]:
        """Create comparison chart for specific parameter"""
        case_ids = []
        parameter_scores = []
        
        for result in results:
            individual_scores = result.get("individual_scores", {})
            if parameter in individual_scores:
                case_ids.append(result.get("case_id", "Unknown"))
                parameter_scores.append(individual_scores[parameter])
        
        return {
            "type": "bar",
            "labels": case_ids,
            "datasets": [{
                "label": f"{parameter} Score",
                "data": parameter_scores,
                "backgroundColor": self.color_palette[1],
                "borderColor": self.color_palette[1],
                "borderWidth": 1
            }]
        }
    
    def create_correlation_matrix(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create correlation matrix for parameters"""
        if not results:
            return {"labels": [], "data": []}
        
        # Collect all parameters and their scores
        all_parameters = set()
        for result in results:
            all_parameters.update(result.get("individual_scores", {}).keys())
        
        parameters = list(all_parameters)
        
        # Create data matrix
        data_matrix = []
        for result in results:
            row = []
            individual_scores = result.get("individual_scores", {})
            for param in parameters:
                row.append(individual_scores.get(param, 0))
            data_matrix.append(row)
        
        if not data_matrix:
            return {"labels": [], "data": []}
        
        # Calculate correlation matrix
        df = pd.DataFrame(data_matrix, columns=parameters)
        correlation_matrix = df.corr().fillna(0)
        
        return {
            "labels": parameters,
            "data": correlation_matrix.values.tolist()
        }
    
    def _empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure"""
        return {
            "total_cases": 0,
            "eligible_cases": 0,
            "average_score": 0,
            "score_distribution": {"type": "bar", "labels": [], "datasets": []},
            "eligibility_breakdown": {"type": "pie", "labels": [], "datasets": []},
            "parameter_analysis": {"type": "bar", "labels": [], "datasets": []},
            "score_trends": {"type": "line", "labels": [], "datasets": []},
            "top_performers": [],
            "score_stats": {}
        } 