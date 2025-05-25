import numpy as np
from typing import Dict, List, Any, Tuple
from ..models.financial_data import MetricScore, ScoringResult, EligibilityCriteria
import uuid
from datetime import datetime

class ScoringEngine:
    """Rule-based scoring engine for loan eligibility assessment"""
    
    def __init__(self):
        self.grade_thresholds = {
            90: "A+", 85: "A", 80: "B+", 75: "B", 
            70: "C+", 65: "C", 60: "D", 0: "F"
        }
        
        self.recommendation_thresholds = {
            80: "Approve", 65: "Review", 0: "Reject"
        }
        
        self.risk_thresholds = {
            75: "Low", 50: "Medium", 0: "High"
        }
    
    def calculate_scores(self, criteria: List[Dict[str, Any]], cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate scores for multiple cases against criteria"""
        analysis_id = str(uuid.uuid4())
        results = []
        
        # Calculate scores for each case
        for case in cases:
            case_result = self.calculate_score_with_intervals(case, criteria)
            
            # Convert to the expected ScoreResult format
            individual_scores = {}
            total_score = 0  # This will be the sum of individual scores (max 10 each)
            
            for metric_score in case_result["metric_scores"]:
                metric_name = metric_score["metric_name"]
                # Individual score is already 0-10 from intervals
                individual_score = metric_score["score"]
                individual_scores[metric_name] = individual_score
                total_score += individual_score
            
            # Total possible score is 10 * number of criteria
            max_possible_score = len(criteria) * 10
            
            # Calculate percentage based on total score out of max possible
            percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
            
            # Determine eligibility status based on percentage
            if percentage >= 80:
                eligibility_status = "Eligible"
            elif percentage >= 60:
                eligibility_status = "Review Required"
            else:
                eligibility_status = "Not Eligible"
            
            score_result = {
                "case_id": case_result["case_id"],
                "total_score": total_score,  # Sum of individual scores
                "max_possible_score": max_possible_score,  # 10 * number of criteria
                "percentage": round(percentage, 2),
                "individual_scores": individual_scores,
                "eligibility_status": eligibility_status,
                "metric_scores": case_result["metric_scores"]
            }
            
            results.append(score_result)
        
        # Calculate summary statistics
        if results:
            percentages = [r["percentage"] for r in results]
            summary = {
                "total_cases": len(results),
                "average_score": round(np.mean(percentages), 2),
                "highest_score": round(max(percentages), 2),
                "lowest_score": round(min(percentages), 2),
                "eligible_cases": len([r for r in results if r["eligibility_status"] == "Eligible"]),
                "review_cases": len([r for r in results if r["eligibility_status"] == "Review Required"]),
                "rejected_cases": len([r for r in results if r["eligibility_status"] == "Not Eligible"])
            }
        else:
            summary = {
                "total_cases": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "eligible_cases": 0,
                "review_cases": 0,
                "rejected_cases": 0
            }
        
        return {
            "analysis_id": analysis_id,
            "results": results,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        }

    def calculate_score_with_intervals(self, case_data: Dict[str, Any], criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive score for a case using scoring intervals"""
        case_metrics = case_data.get("data", {})
        case_id = case_data.get("case_id", "unknown")
        case_name = case_data.get("case_name", case_id)
        
        print(f"\n=== Scoring Case: {case_id} ===")
        print(f"Case metrics: {case_metrics}")
        
        metric_scores = []
        total_weighted_score = 0
        total_weight = 0
        
        # Calculate score for each criterion
        for criterion in criteria:
            metric_name = criterion["parameter"]
            weight = criterion["weight"]
            scoring_intervals = criterion.get("scoring_intervals", [])
            
            print(f"\n--- Processing criterion: {metric_name} ---")
            print(f"Weight: {weight}")
            print(f"Scoring intervals: {scoring_intervals}")
            
            # Find matching metric in case data
            actual_value = self._find_matching_metric(metric_name.lower(), case_metrics)
            print(f"Found actual value: {actual_value} (type: {type(actual_value)})")
            
            if actual_value is not None:
                # Special handling for specific criteria
                if 'tol/tnw' in metric_name.lower() or 'tol' in metric_name.lower():
                    # TOL/TNW: 10 if less than 3, 0 otherwise
                    try:
                        numeric_value = float(str(actual_value).replace(',', ''))
                        score = 10.0 if numeric_value < 3 else 0.0
                        print(f"TOL/TNW special handling: {numeric_value} < 3 = {score}")
                    except (ValueError, TypeError):
                        score = 0.0
                elif 'cmr' in metric_name.lower():
                    # CMR Score: 10 if >= 5, 0 otherwise
                    try:
                        numeric_value = float(str(actual_value).replace(',', ''))
                        score = 10.0 if numeric_value >= 5 else 0.0
                        print(f"CMR Score special handling: {numeric_value} >= 5 = {score}")
                    except (ValueError, TypeError):
                        score = 0.0
                elif scoring_intervals:
                    # Calculate metric score using intervals if available
                    score = self._calculate_score_from_intervals(actual_value, scoring_intervals)
                    print(f"Score from intervals: {score}")
                else:
                    # Fallback to old method if no intervals
                    benchmark_value = criterion.get("min_value") or criterion.get("preferred_value")
                    score = self._calculate_metric_score(actual_value, benchmark_value, True)
                    print(f"Score from fallback method: {score}")
                
                weighted_score = score * (weight / 100)
                
                # Determine status and recommendation
                status = self._get_status(score)
                recommendation = self._get_metric_recommendation(
                    metric_name, actual_value, criterion.get("min_value"), score
                )
                
                metric_scores.append({
                    "metric_name": metric_name,
                    "actual_value": actual_value,
                    "benchmark_value": criterion.get("min_value"),
                    "score": round(score, 2),
                    "weight": weight,
                    "weighted_score": round(weighted_score, 2),
                    "status": status,
                    "recommendation": recommendation
                })
                
                total_weighted_score += weighted_score
                total_weight += weight
                
                print(f"Final score: {score}, weighted: {weighted_score}")
            else:
                print(f"No matching value found for {metric_name}")
        
        # Calculate overall score
        if total_weight > 0:
            overall_score = (total_weighted_score / total_weight) * 100
        else:
            overall_score = 0
        
        print(f"\n=== Final Results for {case_id} ===")
        print(f"Total weighted score: {total_weighted_score}")
        print(f"Total weight: {total_weight}")
        print(f"Overall score: {overall_score}")
        
        # Determine grade, recommendation, and risk level
        grade = self._get_grade(overall_score)
        recommendation = self._get_recommendation(overall_score)
        risk_level = self._get_risk_level(overall_score)
        
        # Generate strengths and weaknesses
        strengths, weaknesses = self._analyze_performance(metric_scores)
        
        return {
            "case_id": case_id,
            "case_name": case_name,
            "overall_score": round(overall_score, 2),
            "grade": grade,
            "recommendation": recommendation,
            "metric_scores": metric_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "risk_level": risk_level
        }

    def _calculate_score_from_intervals(self, actual_value: Any, scoring_intervals: List[Dict[str, Any]]) -> float:
        """Calculate score based on scoring intervals from Excel"""
        try:
            # Convert actual value to appropriate format for comparison
            actual_str = str(actual_value).lower().strip()
            
            # Try to extract numeric value if it contains numbers
            actual_numeric = None
            try:
                # Remove common suffixes and extract number
                cleaned_value = actual_str.replace('cr', '').replace('crore', '').replace('months', '').replace('month', '').replace(',', '').strip()
                # Extract first number found
                import re
                number_match = re.search(r'(\d+(?:\.\d+)?)', cleaned_value)
                if number_match:
                    actual_numeric = float(number_match.group(1))
            except (ValueError, AttributeError):
                pass
            
            print(f"    Actual value: '{actual_value}' -> str: '{actual_str}', numeric: {actual_numeric}")
            
            # Check each interval to find the matching score
            for interval_data in scoring_intervals:
                interval_str = interval_data["interval"].lower().strip()
                score = interval_data["score"]
                
                print(f"    Checking interval: '{interval_str}' (score: {score})")
                
                # Parse different interval formats
                if self._value_matches_interval(actual_value, actual_str, actual_numeric, interval_str):
                    print(f"    ✓ MATCH! Returning score: {score}")
                    # Ensure score is capped at 10 for individual criteria
                    return min(10.0, float(score))
                else:
                    print(f"    ✗ No match")
            
            # If no interval matches, return 0
            print(f"    No intervals matched, returning 0")
            return 0.0
            
        except (ValueError, TypeError) as e:
            print(f"    Error in _calculate_score_from_intervals: {e}")
            return 0.0

    def _value_matches_interval(self, original_value: Any, value_str: str, value_numeric: float, interval_str: str) -> bool:
        """Check if a value matches an interval string"""
        try:
            print(f"      Matching '{original_value}' (str: '{value_str}', numeric: {value_numeric}) against interval '{interval_str}'")
            
            # Special handling for TOL/TNW - less than 3 gets full points
            if 'less than' in interval_str and value_numeric is not None:
                import re
                threshold_match = re.search(r'(\d+(?:\.\d+)?)', interval_str)
                if threshold_match:
                    threshold = float(threshold_match.group(1))
                    result = value_numeric < threshold
                    print(f"      Less than {threshold}: {value_numeric} < {threshold} = {result}")
                    return result
            
            # Handle text-based intervals first
            if 'months' in interval_str or 'month' in interval_str:
                result = self._match_time_interval(value_str, value_numeric, interval_str)
                print(f"      Time interval match result: {result}")
                return result
            
            # Handle yes/no or categorical values
            if interval_str in ['yes', 'no'] or value_str in ['yes', 'no']:
                result = value_str == interval_str
                print(f"      Yes/No match result: {result}")
                return result
            
            # Handle credit ratings
            if any(rating in interval_str.upper() for rating in ['A', 'B', 'C', 'D']) and len(interval_str) <= 3:
                result = value_str.upper() == interval_str.upper()
                print(f"      Credit rating match result: {result}")
                return result
            
            # Handle numeric intervals
            if value_numeric is not None:
                result = self._match_numeric_interval(value_numeric, interval_str)
                print(f"      Numeric interval match result: {result}")
                return result
            
            # Fallback to exact string match
            result = value_str == interval_str
            print(f"      String match result: {result}")
            return result
                
        except (ValueError, IndexError) as e:
            print(f"      Error in _value_matches_interval: {e}")
            pass
        
        return False

    def _match_time_interval(self, value_str: str, value_numeric: float, interval_str: str) -> bool:
        """Match time-based intervals like '6 months and above'"""
        try:
            # Extract threshold from interval
            import re
            threshold_match = re.search(r'(\d+(?:\.\d+)?)', interval_str)
            if not threshold_match:
                return False
            
            threshold = float(threshold_match.group(1))
            
            # Check if we have a numeric value to compare
            if value_numeric is None:
                return False
            
            # Determine the comparison type
            if 'above' in interval_str or 'and above' in interval_str or '+' in interval_str:
                return value_numeric >= threshold
            elif 'below' in interval_str or 'under' in interval_str:
                return value_numeric < threshold
            elif 'between' in interval_str or '-' in interval_str:
                # Handle ranges like "6-12 months"
                parts = re.findall(r'(\d+(?:\.\d+)?)', interval_str)
                if len(parts) >= 2:
                    min_val = float(parts[0])
                    max_val = float(parts[1])
                    return min_val <= value_numeric <= max_val
            else:
                # Exact match
                return value_numeric == threshold
                
        except (ValueError, IndexError):
            pass
        
        return False

    def _match_numeric_interval(self, value: float, interval_str: str) -> bool:
        """Match numeric intervals like '1000 cr+' or '800 - 999'"""
        try:
            # Clean the interval string
            interval_clean = interval_str.replace('cr', '').replace('crore', '').replace(',', '').strip()
            print(f"        Numeric matching: value={value}, interval_clean='{interval_clean}'")
            
            # Handle "above X" format
            if 'above' in interval_clean:
                import re
                threshold_match = re.search(r'(\d+(?:\.\d+)?)', interval_clean)
                if threshold_match:
                    threshold = float(threshold_match.group(1))
                    result = value > threshold
                    print(f"        Above {threshold}: {value} > {threshold} = {result}")
                    return result
            
            # Handle "below X" format  
            elif 'below' in interval_clean:
                import re
                threshold_match = re.search(r'(\d+(?:\.\d+)?)', interval_clean)
                if threshold_match:
                    threshold = float(threshold_match.group(1))
                    result = value < threshold
                    print(f"        Below {threshold}: {value} < {threshold} = {result}")
                    return result
            
            # Handle different interval formats
            elif '+' in interval_clean:
                # Format: "1000+" means >= 1000
                threshold_str = interval_clean.replace('+', '').strip()
                threshold = float(threshold_str)
                result = value >= threshold
                print(f"        Plus format: {value} >= {threshold} = {result}")
                return result
            elif '-' in interval_clean and not interval_clean.startswith('-'):
                # Format: "800 - 999" or "760-799" means 800 <= value <= 999
                # Split by dash and handle both "800 - 999" and "760-799" formats
                import re
                parts = re.split(r'\s*-\s*', interval_clean)
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    result = min_val <= value <= max_val
                    print(f"        Range format: {min_val} <= {value} <= {max_val} = {result}")
                    return result
            else:
                # Exact match or single value
                threshold = float(interval_clean)
                result = value == threshold
                print(f"        Exact match: {value} == {threshold} = {result}")
                return result
                
        except (ValueError, IndexError) as e:
            print(f"        Error in _match_numeric_interval: {e}")
            pass
        
        return False

    def _find_matching_metric(self, metric_name: str, case_metrics: Dict[str, Any]) -> Any:
        """Find matching metric in case data using fuzzy matching"""
        metric_lower = metric_name.lower()
        
        print(f"    Looking for metric: '{metric_name}' (lowercase: '{metric_lower}')")
        print(f"    Available case metrics: {list(case_metrics.keys())}")
        
        # Direct match
        if metric_lower in case_metrics:
            print(f"    Direct match found: {case_metrics[metric_lower]}")
            return case_metrics[metric_lower]
        
        # Try exact case-insensitive match
        for key, value in case_metrics.items():
            if str(key).lower() == metric_lower:
                print(f"    Case-insensitive match found: '{key}' -> {value}")
                return value
        
        # Fuzzy matching
        for key, value in case_metrics.items():
            key_lower = str(key).lower()
            
            # Check if metric name is contained in key or vice versa
            if metric_lower in key_lower or key_lower in metric_lower:
                print(f"    Fuzzy match found: '{key}' -> {value}")
                return value
            
            # Check for common variations
            if self._are_similar_metrics(metric_lower, key_lower):
                print(f"    Similar metric match found: '{key}' -> {value}")
                return value
        
        print(f"    No match found for '{metric_name}'")
        return None
    
    def _are_similar_metrics(self, metric1: str, metric2: str) -> bool:
        """Check if two metric names are similar"""
        synonyms = {
            'revenue': ['sales', 'income', 'turnover'],
            'profit': ['earnings', 'net income', 'profit margin'],
            'debt': ['liability', 'borrowing'],
            'equity': ['capital', 'net worth'],
            'rating': ['score', 'grade'],
            'growth': ['increase', 'expansion'],
            'cibil': ['credit score', 'credit rating'],
            'business vintage': ['vintage', 'business age', 'company age'],
            'current ratio': ['liquidity ratio'],
            'pat': ['profit after tax', 'net profit'],
            'debtor days': ['receivables days', 'collection period'],
            'tol/tnw': ['debt equity', 'leverage ratio'],
            'cmr score': ['cmr', 'credit monitoring'],
            'listed': ['listing status', 'public']
        }
        
        for key, values in synonyms.items():
            if (key in metric1 and any(v in metric2 for v in values)) or \
               (key in metric2 and any(v in metric1 for v in values)) or \
               (key in metric1 and key in metric2):
                return True
        
        return False
    
    def _calculate_metric_score(self, actual: Any, benchmark: Any, is_higher_better: bool) -> float:
        """Calculate score for individual metric (0-100)"""
        try:
            actual_num = float(actual)
            benchmark_num = float(benchmark)
            
            if benchmark_num == 0:
                return 50  # Neutral score if benchmark is zero
            
            ratio = actual_num / benchmark_num
            
            if is_higher_better:
                # Higher values are better
                if ratio >= 1.2:
                    score = 100  # Excellent
                elif ratio >= 1.0:
                    score = 80 + (ratio - 1.0) * 100  # Good to excellent
                elif ratio >= 0.8:
                    score = 60 + (ratio - 0.8) * 100  # Average to good
                else:
                    score = ratio * 75  # Poor to average
            else:
                # Lower values are better (e.g., debt ratio)
                if ratio <= 0.8:
                    score = 100  # Excellent
                elif ratio <= 1.0:
                    score = 80 + (1.0 - ratio) * 100  # Good to excellent
                elif ratio <= 1.2:
                    score = 60 + (1.2 - ratio) * 100  # Average to good
                else:
                    score = max(0, 60 - (ratio - 1.2) * 50)  # Poor
            
            return min(100, max(0, score))
            
        except (ValueError, TypeError):
            # Handle non-numeric values (e.g., credit ratings)
            return self._score_categorical_metric(actual, benchmark)
    
    def _score_categorical_metric(self, actual: Any, benchmark: Any) -> float:
        """Score categorical metrics like credit ratings"""
        actual_str = str(actual).upper().strip()
        benchmark_str = str(benchmark).upper().strip()
        
        # Credit rating scoring
        rating_scores = {
            'AAA': 100, 'AA+': 95, 'AA': 90, 'AA-': 85,
            'A+': 80, 'A': 75, 'A-': 70,
            'BBB+': 65, 'BBB': 60, 'BBB-': 55,
            'BB+': 50, 'BB': 45, 'BB-': 40,
            'B+': 35, 'B': 30, 'B-': 25,
            'CCC': 20, 'CC': 15, 'C': 10, 'D': 5
        }
        
        actual_score = rating_scores.get(actual_str, 50)
        benchmark_score = rating_scores.get(benchmark_str, 50)
        
        if benchmark_score > 0:
            return min(100, (actual_score / benchmark_score) * 100)
        
        return 50  # Default neutral score
    
    def _get_status(self, score: float) -> str:
        """Get status based on score"""
        if score >= 85:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "average"
        else:
            return "poor"
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade based on overall score"""
        for threshold, grade in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return "F"
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on overall score"""
        for threshold, recommendation in self.recommendation_thresholds.items():
            if score >= threshold:
                return recommendation
        return "Reject"
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on overall score"""
        for threshold, risk in self.risk_thresholds.items():
            if score >= threshold:
                return risk
        return "High"
    
    def _get_metric_recommendation(self, metric_name: str, actual: Any, benchmark: Any, score: float) -> str:
        """Generate specific recommendation for metric"""
        if score >= 85:
            return f"Excellent {metric_name} performance"
        elif score >= 70:
            return f"Good {metric_name}, meets requirements"
        elif score >= 50:
            return f"Average {metric_name}, consider improvement"
        else:
            return f"Poor {metric_name}, significant concern"
    
    def _analyze_performance(self, metric_scores: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Analyze performance to identify strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for metric in metric_scores:
            score = metric["score"]
            metric_name = metric["metric_name"].title()
            
            if score >= 85:
                strengths.append(f"Strong {metric_name} ({score:.1f}/100)")
            elif score < 50:
                weaknesses.append(f"Weak {metric_name} ({score:.1f}/100)")
        
        # Add overall insights
        avg_score = np.mean([m["score"] for m in metric_scores]) if metric_scores else 0
        
        if avg_score >= 80:
            strengths.append("Overall strong financial profile")
        elif avg_score < 60:
            weaknesses.append("Overall financial profile needs improvement")
        
        return strengths[:5], weaknesses[:5]  # Limit to top 5 each
    
    def get_default_criteria(self) -> Dict[str, Any]:
        """Get default scoring criteria"""
        return {
            "grade_thresholds": self.grade_thresholds,
            "recommendation_thresholds": self.recommendation_thresholds,
            "risk_thresholds": self.risk_thresholds,
            "scoring_methodology": {
                "excellent": "85-100 points",
                "good": "70-84 points", 
                "average": "50-69 points",
                "poor": "0-49 points"
            }
        } 