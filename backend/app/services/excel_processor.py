import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import re
from ..models.financial_data import EligibilityCriteria, CaseData, ProcessedData
import uuid
import os
from pathlib import Path

class ExcelProcessor:
    """Service for processing Excel files with eligibility criteria and cases"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.processed_files = {}
        self.financial_keywords = [
            'revenue', 'profit', 'loss', 'credit', 'rating', 'sales', 
            'income', 'expense', 'cash', 'debt', 'equity', 'assets',
            'liability', 'margin', 'growth', 'roi', 'ebitda', 'turnover',
            'ratio', 'score', 'value', 'amount', 'total', 'net'
        ]
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file and return file_id"""
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_{filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        self.processed_files[file_id] = {
            "filename": filename,
            "path": str(file_path),
            "sheets": self._get_sheet_names(str(file_path))
        }
        
        return file_id
    
    def _get_sheet_names(self, file_path: str) -> List[str]:
        """Get all sheet names from Excel file"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return []
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get information about processed file"""
        return self.processed_files.get(file_id, {})
    
    def read_criteria_sheet(self, file_id: str, sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """Read eligibility criteria from specified sheet"""
        file_info = self.processed_files.get(file_id)
        if not file_info:
            raise ValueError(f"File with ID {file_id} not found")
        
        try:
            # Read the entire sheet first
            df_full = pd.read_excel(file_info["path"], sheet_name=sheet_name, header=None)
            
            criteria = []
            scoring_intervals = {}
            
            # Read first criteria block (C2:E12) - columns 2,3,4 and rows 1-11 (0-indexed)
            print("Reading first criteria block (C2:E12)")
            for row_idx in range(1, 12):  # rows 2-12 (1-indexed) = 1-11 (0-indexed)
                if row_idx < len(df_full):
                    metric = df_full.iloc[row_idx, 2] if len(df_full.columns) > 2 else None  # Column C
                    min_criteria = df_full.iloc[row_idx, 3] if len(df_full.columns) > 3 else None  # Column D
                    weight = df_full.iloc[row_idx, 4] if len(df_full.columns) > 4 else None  # Column E
                    
                    # Skip header row and empty rows
                    if (pd.isna(metric) or str(metric).strip() == '' or 
                        str(metric).lower() in ['metrics', 'parameter', 'metric']):
                        continue
                    
                    # Process the criteria item
                    weight_value = 10.0  # default
                    if pd.notna(weight):
                        try:
                            weight_value = float(weight)
                        except (ValueError, TypeError):
                            weight_value = 10.0
                    
                    criteria_item = {
                        "parameter": str(metric).strip(),
                        "weight": weight_value,
                        "min_value": min_criteria if pd.notna(min_criteria) else None,
                        "max_value": None,
                        "preferred_value": str(min_criteria) if pd.notna(min_criteria) else None
                    }
                    criteria.append(criteria_item)
                    print(f"Added criteria: {criteria_item}")
            
            # Read second criteria block (I2:K45) - columns 8,9,10 and rows 1-44 (0-indexed)
            print("Reading second criteria block (I2:K45) for scoring intervals")
            current_metric = None
            
            for row_idx in range(1, 45):  # rows 2-45 (1-indexed) = 1-44 (0-indexed)
                if row_idx < len(df_full):
                    metric = df_full.iloc[row_idx, 8] if len(df_full.columns) > 8 else None  # Column I
                    intervals = df_full.iloc[row_idx, 9] if len(df_full.columns) > 9 else None  # Column J
                    scoring = df_full.iloc[row_idx, 10] if len(df_full.columns) > 10 else None  # Column K
                    
                    # Skip header row
                    if (pd.notna(metric) and str(metric).lower() in ['metrics', 'parameter', 'metric', 'intervals', 'scoring']):
                        continue
                    
                    # Check if this is a new metric name
                    if pd.notna(metric) and str(metric).strip() != '':
                        current_metric = str(metric).strip()
                        if current_metric not in scoring_intervals:
                            scoring_intervals[current_metric] = []
                        print(f"Found metric for scoring: {current_metric}")
                    
                    # If we have interval and scoring data for the current metric
                    if current_metric and pd.notna(intervals) and pd.notna(scoring):
                        try:
                            interval_str = str(intervals).strip()
                            score_value = float(scoring)
                            
                            # Parse interval string (e.g., "1000 cr+", "800 cr - 999 cr", etc.)
                            scoring_intervals[current_metric].append({
                                "interval": interval_str,
                                "score": score_value
                            })
                            print(f"Added scoring interval for {current_metric}: {interval_str} -> {score_value}")
                        except (ValueError, TypeError) as e:
                            print(f"Error parsing scoring data: {e}")
                            continue
            
            # Merge scoring intervals with criteria
            for criterion in criteria:
                param_name = criterion["parameter"]
                if param_name in scoring_intervals:
                    criterion["scoring_intervals"] = scoring_intervals[param_name]
                    print(f"Added {len(scoring_intervals[param_name])} scoring intervals to {param_name}")
            
            print(f"Total extracted {len(criteria)} criteria items with scoring intervals")
            return {"criteria": criteria, "scoring_intervals": scoring_intervals}
        
        except Exception as e:
            print(f"Error details: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Error reading criteria sheet: {e}")
    
    def read_cases_sheet(self, file_id: str, sheet_name: str) -> List[Dict[str, Any]]:
        """Read case data from specified sheet"""
        file_info = self.processed_files.get(file_id)
        if not file_info:
            raise ValueError(f"File with ID {file_id} not found")
        
        try:
            # Read the entire sheet without headers
            df_full = pd.read_excel(file_info["path"], sheet_name=sheet_name, header=None)
            
            cases = []
            case_data = {}
            case_id = sheet_name  # Use sheet name as case ID
            
            # Read case data from C4:D13 (columns 2,3 and rows 3-12 in 0-indexed)
            print(f"Reading case data from {sheet_name} (C4:D13)")
            
            for row_idx in range(3, 13):  # rows 4-13 (1-indexed) = 3-12 (0-indexed)
                if row_idx < len(df_full):
                    metric = df_full.iloc[row_idx, 2] if len(df_full.columns) > 2 else None  # Column C
                    value = df_full.iloc[row_idx, 3] if len(df_full.columns) > 3 else None  # Column D
                    
                    # Skip empty rows
                    if pd.isna(metric) or str(metric).strip() == '':
                        continue
                    
                    metric_name = str(metric).strip()
                    
                    # Try to convert value to appropriate type
                    if pd.notna(value):
                        try:
                            # Try numeric conversion first
                            case_data[metric_name] = float(value)
                        except (ValueError, TypeError):
                            # Keep as string if not numeric
                            case_data[metric_name] = str(value).strip()
                    
                    print(f"Added metric: {metric_name} = {case_data.get(metric_name)}")
            
            if case_data:  # Only add if we found some data
                cases.append({
                    "case_id": case_id,
                    "data": case_data
                })
                print(f"Created case: {case_id} with {len(case_data)} metrics")
            else:
                print(f"No data found in sheet {sheet_name}")
            
            print(f"Extracted {len(cases)} cases from sheet {sheet_name}")
            return cases
        
        except Exception as e:
            print(f"Error reading cases sheet {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Error reading cases sheet {sheet_name}: {e}")
    
    def get_all_cases(self, file_id: str, sheet_names: List[str]) -> List[Dict[str, Any]]:
        """Read cases from multiple sheets"""
        all_cases = []
        for sheet_name in sheet_names:
            try:
                cases = self.read_cases_sheet(file_id, sheet_name)
                all_cases.extend(cases)
            except Exception as e:
                print(f"Warning: Could not read sheet {sheet_name}: {e}")
        
        return all_cases
    
    def cleanup_file(self, file_id: str) -> bool:
        """Remove uploaded file and clean up"""
        file_info = self.processed_files.get(file_id)
        if file_info:
            try:
                os.remove(file_info["path"])
                del self.processed_files[file_id]
                return True
            except Exception as e:
                print(f"Error cleaning up file {file_id}: {e}")
                return False
        return False
    
    def process_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Process Excel file and extract eligibility criteria and cases"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            # Process first sheet as eligibility criteria
            criteria_df = pd.read_excel(file_path, sheet_name=sheet_names[0])
            eligibility_criteria = self._extract_eligibility_criteria(criteria_df)
            
            # Process remaining sheets as cases
            cases = []
            for sheet_name in sheet_names[1:]:
                case_df = pd.read_excel(file_path, sheet_name=sheet_name)
                case_data = self._extract_case_data(case_df, sheet_name)
                cases.extend(case_data)
            
            return {
                "eligibility_criteria": [criteria.dict() for criteria in eligibility_criteria],
                "cases": [case.dict() for case in cases],
                "sheet_names": sheet_names,
                "total_cases": len(cases),
                "total_criteria": len(eligibility_criteria)
            }
            
        except Exception as e:
            raise Exception(f"Error processing Excel file: {str(e)}")
    
    def _extract_eligibility_criteria(self, df: pd.DataFrame) -> List[EligibilityCriteria]:
        """Extract eligibility criteria from first sheet"""
        criteria = []
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Look for standard column patterns
        metric_col = self._find_column(df, ['metric', 'criteria', 'parameter', 'factor'])
        value_col = self._find_column(df, ['benchmark', 'target', 'value', 'threshold'])
        weight_col = self._find_column(df, ['weight', 'importance', 'percentage'])
        
        if not metric_col or not value_col:
            # Fallback: assume first two columns are metric and value
            metric_col = df.columns[0]
            value_col = df.columns[1]
            weight_col = df.columns[2] if len(df.columns) > 2 else None
        
        for idx, row in df.iterrows():
            if pd.isna(row[metric_col]) or pd.isna(row[value_col]):
                continue
                
            metric_name = str(row[metric_col]).strip()
            benchmark_value = row[value_col]
            
            # Determine weight
            weight = 10.0  # Default weight
            if weight_col and not pd.isna(row[weight_col]):
                weight = float(row[weight_col])
            
            # Determine if higher is better
            is_higher_better = self._determine_direction(metric_name)
            
            criteria.append(EligibilityCriteria(
                metric_name=metric_name,
                benchmark_value=benchmark_value,
                weight=weight,
                is_higher_better=is_higher_better
            ))
        
        return criteria
    
    def _extract_case_data(self, df: pd.DataFrame, sheet_name: str) -> List[CaseData]:
        """Extract case data from individual sheets"""
        cases = []
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Check if data is in rows or columns
        if self._is_data_in_rows(df):
            cases.extend(self._extract_row_based_cases(df, sheet_name))
        else:
            cases.extend(self._extract_column_based_cases(df, sheet_name))
        
        return cases
    
    def _extract_row_based_cases(self, df: pd.DataFrame, sheet_name: str) -> List[CaseData]:
        """Extract cases when each row represents a case"""
        cases = []
        
        # Find ID column
        id_col = self._find_column(df, ['id', 'case', 'name', 'company', 'client'])
        if not id_col:
            id_col = df.columns[0]
        
        for idx, row in df.iterrows():
            if pd.isna(row[id_col]):
                continue
                
            case_id = f"{sheet_name}_{idx}"
            case_name = str(row[id_col])
            
            # Extract metrics
            metrics = {}
            for col in df.columns:
                if col != id_col and not pd.isna(row[col]):
                    metrics[col] = row[col]
            
            cases.append(CaseData(
                case_id=case_id,
                case_name=case_name,
                metrics=metrics
            ))
        
        return cases
    
    def _extract_column_based_cases(self, df: pd.DataFrame, sheet_name: str) -> List[CaseData]:
        """Extract cases when each column represents a case"""
        cases = []
        
        # Assume first column contains metric names
        metric_col = df.columns[0]
        
        for col in df.columns[1:]:
            if df[col].isna().all():
                continue
                
            case_id = f"{sheet_name}_{col}"
            case_name = str(col)
            
            # Extract metrics
            metrics = {}
            for idx, row in df.iterrows():
                if not pd.isna(row[metric_col]) and not pd.isna(row[col]):
                    metric_name = str(row[metric_col]).strip().lower()
                    metrics[metric_name] = row[col]
            
            cases.append(CaseData(
                case_id=case_id,
                case_name=case_name,
                metrics=metrics
            ))
        
        return cases
    
    def _find_column(self, df: pd.DataFrame, keywords: List[str]) -> str:
        """Find column that matches any of the keywords"""
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in keywords):
                return col
        return None
    
    def _is_data_in_rows(self, df: pd.DataFrame) -> bool:
        """Determine if data is organized in rows (vs columns)"""
        # Heuristic: if first column contains text and others contain numbers
        first_col = df.iloc[:, 0]
        other_cols = df.iloc[:, 1:]
        
        text_ratio = first_col.apply(lambda x: isinstance(x, str)).mean()
        numeric_ratio = other_cols.select_dtypes(include=[np.number]).shape[1] / other_cols.shape[1]
        
        return text_ratio > 0.5 and numeric_ratio > 0.5
    
    def _determine_direction(self, metric_name: str) -> bool:
        """Determine if higher values are better for a metric"""
        metric_lower = metric_name.lower()
        
        # Metrics where lower is better
        negative_indicators = [
            'debt', 'loss', 'expense', 'cost', 'risk', 'default', 
            'delinquency', 'ratio', 'leverage', 'liability'
        ]
        
        # Metrics where higher is better
        positive_indicators = [
            'revenue', 'profit', 'income', 'sales', 'growth', 
            'margin', 'rating', 'score', 'cash', 'equity', 'assets'
        ]
        
        if any(indicator in metric_lower for indicator in negative_indicators):
            return False
        elif any(indicator in metric_lower for indicator in positive_indicators):
            return True
        else:
            return True  # Default to higher is better 