import React, { useState } from 'react'
import { Dashboard } from './components/Dashboard'
import { FileUpload } from './components/FileUpload'
import './App.css'

interface AnalysisData {
  uploadResult: any;
  criteriaData: any;
  cases: any[];
  analysisResult: any;
  dashboardData: any;
  file_id: string;
  analysis_id: string;
}

function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = (data: AnalysisData) => {
    setAnalysisData(data);
    setError(null);
  };

  const handleReset = () => {
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="App">
      {!analysisData ? (
        <div className="upload-container">
          <h1 className="text-3xl font-bold text-center mb-8">Finance Dashboard</h1>
          <FileUpload 
            onUpload={handleFileUpload}
            isLoading={isLoading}
          />
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg max-w-2xl mx-auto">
              <p className="text-red-600">{error}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="dashboard-container">
          <div className="flex justify-between items-center mb-6 px-6 pt-6">
            <h1 className="text-3xl font-bold">Finance Dashboard</h1>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload New File
            </button>
          </div>
          <Dashboard data={analysisData} />
        </div>
      )}
    </div>
  )
}

export default App 