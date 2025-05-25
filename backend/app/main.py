from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import os
from typing import Dict, Any, List
import uuid
import aiofiles

from .services.excel_processor import ExcelProcessor
from .services.scoring_engine import ScoringEngine
from .services.chart_generator import ChartGenerator
from .models.financial_data import ProcessedData, ScoringResult

app = FastAPI(
    title="Finance Dashboard API",
    description="API for financial data analysis and loan scoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Initialize services
excel_processor = ExcelProcessor()
scoring_engine = ScoringEngine()
chart_generator = ChartGenerator()

@app.get("/")
async def root():
    return {"message": "Finance Dashboard API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "finance-dashboard-api"}

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload and process Excel file with eligibility criteria and cases"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = f"uploads/{file_id}_{file.filename}"
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process Excel file
        processed_data = excel_processor.process_excel_file(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return JSONResponse(content={
            "status": "success",
            "file_id": file_id,
            "data": processed_data
        })
    
    except Exception as e:
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/generate-charts")
async def generate_charts(data: Dict[str, Any]):
    """Generate charts and visualizations from processed data"""
    try:
        charts = chart_generator.generate_all_charts(data)
        return JSONResponse(content={"charts": charts})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {str(e)}")

@app.post("/calculate-scores")
async def calculate_scores(data: Dict[str, Any]):
    """Calculate scores for all cases based on eligibility criteria"""
    try:
        # Extract eligibility criteria and cases
        criteria = data.get("eligibility_criteria", {})
        cases = data.get("cases", [])
        
        # Calculate scores for all cases using the new method
        scoring_results = scoring_engine.calculate_scores(criteria, cases)
        
        return JSONResponse(content={
            "status": "success",
            "results": scoring_results
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating scores: {str(e)}")

@app.get("/scoring-criteria")
async def get_scoring_criteria():
    """Get default scoring criteria and weights"""
    return JSONResponse(content=scoring_engine.get_default_criteria())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 