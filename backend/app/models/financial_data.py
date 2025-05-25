from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class EligibilityCriteria(BaseModel):
    """Model for eligibility criteria from first sheet"""
    metric_name: str
    benchmark_value: Union[float, int, str]
    weight: float = Field(ge=0, le=100)
    is_higher_better: bool = True
    description: Optional[str] = None

class CaseData(BaseModel):
    """Model for individual case data"""
    case_id: str
    case_name: Optional[str] = None
    metrics: Dict[str, Union[float, int, str]]
    metadata: Optional[Dict[str, Any]] = None

class ProcessedData(BaseModel):
    """Model for processed Excel data"""
    eligibility_criteria: List[EligibilityCriteria]
    cases: List[CaseData]
    sheet_names: List[str]
    processing_timestamp: datetime = Field(default_factory=datetime.now)

class MetricScore(BaseModel):
    """Model for individual metric scoring"""
    metric_name: str
    actual_value: Union[float, int, str]
    benchmark_value: Union[float, int, str]
    score: float = Field(ge=0, le=100)
    weight: float
    weighted_score: float
    status: str  # "excellent", "good", "average", "poor"
    recommendation: str

class ScoringResult(BaseModel):
    """Model for case scoring results"""
    case_id: str
    case_name: Optional[str] = None
    overall_score: float = Field(ge=0, le=100)
    grade: str  # A+, A, B+, B, C+, C, D, F
    recommendation: str  # "Approve", "Review", "Reject"
    metric_scores: List[MetricScore]
    strengths: List[str]
    weaknesses: List[str]
    risk_level: str  # "Low", "Medium", "High"

class ChartData(BaseModel):
    """Model for chart data"""
    chart_type: str
    title: str
    data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None

class DashboardData(BaseModel):
    """Model for complete dashboard data"""
    processed_data: ProcessedData
    scoring_results: List[ScoringResult]
    charts: List[ChartData]
    summary_stats: Dict[str, Any] 