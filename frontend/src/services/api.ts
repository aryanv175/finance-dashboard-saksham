import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FileUploadResponse {
  filename: string;
  file_id: string;
  message: string;
  sheets: string[];
}

export interface CriteriaItem {
  parameter: string;
  weight: number;
  min_value?: number;
  max_value?: number;
  preferred_value?: string;
}

export interface EligibilityCriteria {
  criteria: CriteriaItem[];
}

export interface CaseData {
  case_id: string;
  data: Record<string, any>;
}

export interface ScoreResult {
  case_id: string;
  total_score: number;
  max_possible_score: number;
  percentage: number;
  individual_scores: Record<string, number>;
  eligibility_status: string;
}

export interface AnalysisRequest {
  file_id: string;
  criteria_sheet: string;
  cases_sheets: string[];
}

export interface AnalysisResponse {
  file_id: string;
  analysis_id: string;
  results: ScoreResult[];
  summary: Record<string, any>;
  created_at: string;
}

export interface ChartData {
  type: string;
  labels: string[];
  datasets: Array<{
    label?: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
    tension?: number;
  }>;
}

export interface DashboardData {
  total_cases: number;
  eligible_cases: number;
  average_score: number;
  score_distribution: ChartData;
  eligibility_breakdown: ChartData;
  parameter_analysis: ChartData;
  score_trends: ChartData;
  top_performers: ScoreResult[];
  score_stats: Record<string, number>;
}

export const apiService = {
  // File upload
  uploadFile: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get file info
  getFileInfo: async (fileId: string) => {
    const response = await api.get(`/file/${fileId}/info`);
    return response.data;
  },

  // Get criteria
  getCriteria: async (fileId: string, sheetName: string): Promise<EligibilityCriteria> => {
    const response = await api.get(`/file/${fileId}/criteria/${sheetName}`);
    return response.data;
  },

  // Get cases
  getCases: async (fileId: string, sheetName: string) => {
    const response = await api.get(`/file/${fileId}/cases/${sheetName}`);
    return response.data;
  },

  // Analyze data
  analyzeData: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response = await api.post('/analyze', request);
    return response.data;
  },

  // Get analysis results
  getAnalysis: async (analysisId: string) => {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  },

  // Get dashboard data
  getDashboardData: async (analysisId: string): Promise<DashboardData> => {
    const response = await api.get(`/dashboard/${analysisId}`);
    return response.data;
  },

  // Get comparison chart
  getComparisonChart: async (analysisId: string, parameter: string): Promise<ChartData> => {
    const response = await api.get(`/chart/comparison/${analysisId}?parameter=${parameter}`);
    return response.data;
  },

  // Get correlation matrix
  getCorrelationMatrix: async (analysisId: string) => {
    const response = await api.get(`/chart/correlation/${analysisId}`);
    return response.data;
  },

  // Delete file
  deleteFile: async (fileId: string) => {
    const response = await api.delete(`/file/${fileId}`);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
}; 