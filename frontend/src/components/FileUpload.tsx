'use client'

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  FileSpreadsheet, 
  CheckCircle, 
  AlertCircle, 
  X,
  Loader2
} from 'lucide-react'

interface FileUploadProps {
  onUpload: (data: any) => void
  isLoading: boolean
}

export function FileUpload({ onUpload, isLoading }: FileUploadProps) {
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setError('Please upload an Excel file (.xlsx or .xls)')
      return
    }

    setError(null)
    setUploadedFile(file)
    setUploadProgress(0)

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)

      // Upload to backend
      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }

      const uploadResult = await response.json()
      
      // Complete progress
      clearInterval(progressInterval)
      setUploadProgress(100)

      // Process the uploaded file
      await processExcelFile(uploadResult)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploadProgress(0)
    }
  }, [])

  const processExcelFile = async (uploadResult: any) => {
    try {
      // Get file info and sheets
      const { file_id, sheets } = uploadResult
      console.log('Upload result:', uploadResult)

      if (!sheets || sheets.length === 0) {
        throw new Error('No sheets found in the Excel file')
      }

      console.log('Available sheets:', sheets)

      // Read criteria from first sheet
      console.log('Reading criteria from sheet:', sheets[0])
      const criteriaResponse = await fetch(`http://localhost:8000/api/v1/file/${file_id}/criteria/${sheets[0]}`)
      if (!criteriaResponse.ok) {
        const errorText = await criteriaResponse.text()
        console.error('Criteria response error:', errorText)
        throw new Error(`Failed to read criteria from Excel file: ${errorText}`)
      }
      const criteriaData = await criteriaResponse.json()
      console.log('Criteria data:', criteriaData)

      // Read cases from remaining sheets
      const casesSheets = sheets.slice(1)
      console.log('Reading cases from sheets:', casesSheets)
      const allCases = []

      for (const sheet of casesSheets) {
        console.log('Processing sheet:', sheet)
        const casesResponse = await fetch(`http://localhost:8000/api/v1/file/${file_id}/cases/${sheet}`)
        if (casesResponse.ok) {
          const casesData = await casesResponse.json()
          console.log(`Cases from ${sheet}:`, casesData)
          allCases.push(...casesData.cases)
        } else {
          const errorText = await casesResponse.text()
          console.warn(`Could not read sheet ${sheet}:`, errorText)
        }
      }

      console.log('Total cases found:', allCases.length)

      if (allCases.length === 0) {
        throw new Error('No case data found in the Excel file')
      }

      // Analyze the data
      console.log('Starting analysis...')
      const analysisResponse = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_id,
          criteria_sheet: sheets[0],
          cases_sheets: casesSheets,
        }),
      })

      if (!analysisResponse.ok) {
        const errorText = await analysisResponse.text()
        console.error('Analysis response error:', errorText)
        throw new Error(`Failed to analyze the data: ${errorText}`)
      }

      const analysisResult = await analysisResponse.json()
      console.log('Analysis result:', analysisResult)

      // Get dashboard data
      console.log('Getting dashboard data...')
      const dashboardResponse = await fetch(`http://localhost:8000/api/v1/dashboard/${analysisResult.analysis_id}`)
      if (!dashboardResponse.ok) {
        const errorText = await dashboardResponse.text()
        console.error('Dashboard response error:', errorText)
        throw new Error(`Failed to generate dashboard data: ${errorText}`)
      }

      const dashboardData = await dashboardResponse.json()
      console.log('Dashboard data:', dashboardData)

      // Pass the complete data to parent component
      onUpload({
        uploadResult,
        criteriaData,
        cases: allCases,
        analysisResult,
        dashboardData,
        file_id,
        analysis_id: analysisResult.analysis_id,
      })

    } catch (err) {
      console.error('Process Excel file error:', err)
      setError(err instanceof Error ? err.message : 'Failed to process Excel file')
      setUploadProgress(0)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    multiple: false,
    disabled: isLoading,
  })

  const removeFile = () => {
    setUploadedFile(null)
    setUploadProgress(0)
    setError(null)
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-6 w-6" />
            Upload Excel File
          </CardTitle>
          <CardDescription>
            Upload your Excel file with eligibility criteria (first sheet) and case data (subsequent sheets named 'Case 1', 'Case 2', etc.)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!uploadedFile ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-blue-400 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              {isDragActive ? (
                <p className="text-lg text-blue-600">Drop the Excel file here...</p>
              ) : (
                <div>
                  <p className="text-lg mb-2">
                    Drag & drop an Excel file here, or click to select
                  </p>
                  <p className="text-sm text-gray-500 mb-4">
                    Supports .xlsx and .xls files
                  </p>
                  <Button disabled={isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      'Select File'
                    )}
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileSpreadsheet className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="font-medium">{uploadedFile.name}</p>
                    <p className="text-sm text-gray-500">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {uploadProgress === 100 ? (
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Uploaded
                    </Badge>
                  ) : (
                    <Badge variant="secondary">
                      Uploading...
                    </Badge>
                  )}
                  {!isLoading && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={removeFile}
                      className="h-8 w-8 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {uploadProgress > 0 && uploadProgress < 100 && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <Progress value={uploadProgress} className="h-2" />
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-800">
                <AlertCircle className="h-5 w-5" />
                <p className="font-medium">Upload Error</p>
              </div>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Excel File Format:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>First Sheet (Eligibility Criteria):</strong> Column A: Metrics, Column B: Minimum criteria, Column C: Weights</li>
              <li>• <strong>Case Sheets (Case 1, Case 2, etc.):</strong> Column A: Metric names, Column B: Values for that case</li>
              <li>• Ensure all numeric values are properly formatted</li>
              <li>• Sheet names should be 'Case 1', 'Case 2', 'Case 3', etc.</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 