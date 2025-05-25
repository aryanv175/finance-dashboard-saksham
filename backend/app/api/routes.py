from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uuid

from ..models.schemas import (
    FileUploadResponse, AnalysisRequest, AnalysisResponse, 
    DashboardData, ChartData
)
from ..services.excel_processor import ExcelProcessor
from ..services.scoring_engine import ScoringEngine
from ..services.visualization import VisualizationService

router = APIRouter()

# Service instances
excel_processor = ExcelProcessor()
scoring_engine = ScoringEngine()
visualization_service = VisualizationService()

# In-memory storage for analysis results (in production, use a database)
analysis_storage = {}

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload Excel file and return file information"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
        # Read file content
        content = await file.read()
        
        # Save file and get file_id
        file_id = await excel_processor.save_uploaded_file(content, file.filename)
        
        # Get file information
        file_info = excel_processor.get_file_info(file_id)
        
        return FileUploadResponse(
            filename=file.filename,
            file_id=file_id,
            message="File uploaded successfully",
            sheets=file_info.get("sheets", [])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/file/{file_id}/info")
async def get_file_info(file_id: str):
    """Get information about uploaded file"""
    try:
        file_info = excel_processor.get_file_info(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "file_id": file_id,
            "filename": file_info["filename"],
            "sheets": file_info["sheets"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

@router.get("/file/{file_id}/criteria/{sheet_name}")
async def get_criteria(file_id: str, sheet_name: str):
    """Get eligibility criteria from specified sheet"""
    try:
        criteria = excel_processor.read_criteria_sheet(file_id, sheet_name)
        return criteria
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading criteria: {str(e)}")

@router.get("/file/{file_id}/cases/{sheet_name}")
async def get_cases(file_id: str, sheet_name: str):
    """Get case data from specified sheet"""
    try:
        cases = excel_processor.read_cases_sheet(file_id, sheet_name)
        return {"cases": cases}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cases: {str(e)}")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """Analyze cases against criteria and generate scores"""
    try:
        # Read criteria
        criteria_data = excel_processor.read_criteria_sheet(request.file_id, request.criteria_sheet)
        criteria = criteria_data.get("criteria", [])
        
        if not criteria:
            raise HTTPException(status_code=400, detail="No criteria found in the specified sheet")
        
        # Read all cases
        all_cases = excel_processor.get_all_cases(request.file_id, request.cases_sheets)
        
        if not all_cases:
            raise HTTPException(status_code=400, detail="No cases found in the specified sheets")
        
        # Calculate scores
        analysis_results = scoring_engine.calculate_scores(criteria, all_cases)
        
        # Store results
        analysis_id = analysis_results["analysis_id"]
        analysis_storage[analysis_id] = analysis_results
        
        return AnalysisResponse(
            file_id=request.file_id,
            analysis_id=analysis_id,
            results=analysis_results["results"],
            summary=analysis_results["summary"],
            created_at=analysis_results["created_at"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis_storage[analysis_id]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analysis: {str(e)}")

@router.get("/dashboard/{analysis_id}", response_model=DashboardData)
async def get_dashboard_data(analysis_id: str):
    """Get dashboard visualization data"""
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_storage[analysis_id]
        dashboard_data = visualization_service.generate_dashboard_data(analysis_results)
        
        return DashboardData(**dashboard_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard data: {str(e)}")

@router.get("/chart/comparison/{analysis_id}")
async def get_comparison_chart(analysis_id: str, parameter: str):
    """Get comparison chart for specific parameter"""
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_storage[analysis_id]
        results = analysis_results.get("results", [])
        
        chart_data = visualization_service.create_comparison_chart(results, parameter)
        return chart_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comparison chart: {str(e)}")

@router.get("/chart/correlation/{analysis_id}")
async def get_correlation_matrix(analysis_id: str):
    """Get correlation matrix for parameters"""
    try:
        if analysis_id not in analysis_storage:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_storage[analysis_id]
        results = analysis_results.get("results", [])
        
        correlation_data = visualization_service.create_correlation_matrix(results)
        return correlation_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating correlation matrix: {str(e)}")

@router.delete("/file/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file and clean up"""
    try:
        success = excel_processor.cleanup_file(file_id)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found or could not be deleted")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Finance Dashboard API is running"} 