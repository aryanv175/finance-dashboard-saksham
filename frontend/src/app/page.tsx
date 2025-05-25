'use client'

import { useState } from 'react'
import { FileUpload } from '@/components/FileUpload'
import { Dashboard } from '@/components/Dashboard'
import { Header } from '@/components/Header'

export default function Home() {
  const [dashboardData, setDashboardData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleFileUpload = async (data: any) => {
    setIsLoading(true)
    try {
      // Process the uploaded data and set it for the dashboard
      setDashboardData(data)
    } catch (error) {
      console.error('Error processing file:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReset = () => {
    setDashboardData(null)
    setIsLoading(false)
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />
      
      {!dashboardData ? (
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <div className="max-w-4xl w-full">
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Finance Dashboard
                </h1>
                <p className="text-lg text-gray-600 mb-2">
                  Upload your Excel file to analyze financial data and generate loan eligibility scores
                </p>
                <p className="text-sm text-gray-500">
                  Supports comprehensive financial analysis with automated scoring and visualization
                </p>
              </div>
              <FileUpload onUpload={handleFileUpload} isLoading={isLoading} />
            </div>
          </div>
        </div>
      ) : (
        <div className="container mx-auto px-4 py-8">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
              <p className="text-gray-600">Financial data analysis and loan eligibility assessment</p>
            </div>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload New File
            </button>
          </div>
          <Dashboard data={dashboardData} />
        </div>
      )}
    </main>
  )
} 