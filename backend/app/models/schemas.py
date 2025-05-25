from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    message: str
    sheets: List[str]

class CriteriaItem(BaseModel):
    parameter: str
    weight: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    preferred_value: Optional[str] = None

class EligibilityCriteria(BaseModel):
    criteria: List[CriteriaItem]

class CaseData(BaseModel):
    case_id: str
    data: Dict[str, Any]

class ScoreResult(BaseModel):
    case_id: str
    total_score: float
    max_possible_score: float
    percentage: float
    individual_scores: Dict[str, float]
    eligibility_status: str

class AnalysisRequest(BaseModel):
    file_id: str
    criteria_sheet: str = "Sheet1"
    cases_sheets: List[str]

class AnalysisResponse(BaseModel):
    file_id: str
    analysis_id: str
    results: List[ScoreResult]
    summary: Dict[str, Any]
    created_at: datetime

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class DashboardData(BaseModel):
    total_cases: int
    eligible_cases: int
    average_score: float
    score_distribution: ChartData
    parameter_analysis: Dict[str, Any]
    top_performers: List[ScoreResult] 