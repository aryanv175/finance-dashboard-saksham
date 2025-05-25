'use client'

import React, { useState, useEffect, useMemo } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Users, 
  FileText,
  BarChart3,
  PieChart,
  Award,
  Target,
  Calculator,
  FileSpreadsheet,
  Activity,
  Zap,
  GitCompare
} from 'lucide-react'

// Chart.js imports
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Bar, Pie, Line, Radar, Doughnut } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
)

interface DashboardProps {
  data: {
    uploadResult?: any
    criteriaData?: any
    cases?: any[]
    analysisResult?: any
    dashboardData?: any
    file_id?: string
    analysis_id?: string
  }
}

export function Dashboard({ data }: DashboardProps) {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedCriteria, setSelectedCriteria] = useState<string>('Revenue')

  const { 
    uploadResult, 
    criteriaData, 
    cases = [], 
    analysisResult, 
    dashboardData 
  } = data

  // Extract analysis data
  const results = analysisResult?.results || []
  const summary = analysisResult?.summary || {}
  const criteria = criteriaData?.criteria || []

  // Extract criteria for comparison
  const criteriaForComparison = useMemo(() => {
    const criteriaSource = data?.criteriaData?.criteria || data?.analysisResult?.criteria || {};
    if (!criteriaSource || Object.keys(criteriaSource).length === 0) return [];
    
    // Convert criteria object to array format
    const criteriaArray = Object.entries(criteriaSource).map(([name, criteriaData]: [string, any]) => {
      // Extract ideal value from scoring intervals
      let idealValue = 'N/A';
      if (criteriaData.scoring_intervals && Array.isArray(criteriaData.scoring_intervals)) {
        // Find the interval with the highest score (usually score 10)
        const bestInterval = criteriaData.scoring_intervals
          .filter((interval: any) => interval.score === 10)
          .sort((a: any, b: any) => b.score - a.score)[0];
        
        if (bestInterval) {
          idealValue = bestInterval.range || bestInterval.condition || 'Best performance';
        }
      }
      
      return {
        name,
        weight: criteriaData.weight || 1,
        idealValue,
        description: criteriaData.description || name
      };
    });
    
    return criteriaArray;
  }, [data?.criteriaData?.criteria, data?.analysisResult?.criteria]);

  // Set default selected criteria to Revenue
  useEffect(() => {
    if (criteria.length > 0 && (!selectedCriteria || selectedCriteria === 'Revenue')) {
      const revenueItem = criteria.find((item: any) => 
        item.parameter && (
          item.parameter.toLowerCase().includes('revenue') || 
          item.parameter.toLowerCase().includes('sales') ||
          item.parameter.toLowerCase().includes('turnover')
        )
      );
      setSelectedCriteria(revenueItem ? revenueItem.parameter : criteria[0].parameter);
    } else if (criteriaForComparison.length > 0 && (!selectedCriteria || selectedCriteria === 'Revenue')) {
      const revenueItem = criteriaForComparison.find(item => 
        item.name.toLowerCase().includes('revenue') || 
        item.name.toLowerCase().includes('sales') ||
        item.name.toLowerCase().includes('turnover')
      );
      setSelectedCriteria(revenueItem ? revenueItem.name : criteriaForComparison[0].name);
    }
  }, [criteria, criteriaForComparison]);

  // Calculate summary statistics
  const totalCases = results.length
  const avgScore = results.length > 0 
    ? results.reduce((sum: number, result: any) => sum + (result.percentage || 0), 0) / results.length 
    : 0

  const approvedCount = results.filter((result: any) => result.eligibility_status === 'Eligible').length
  const rejectedCount = results.filter((result: any) => result.eligibility_status === 'Not Eligible').length
  const reviewCount = results.filter((result: any) => result.eligibility_status === 'Review Required').length

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Eligible':
        return 'bg-green-100 text-green-800'
      case 'Review Required':
        return 'bg-yellow-100 text-yellow-800'
      case 'Not Eligible':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  // Chart data preparation
  const statusPieData = {
    labels: ['Eligible', 'Review Required', 'Not Eligible'],
    datasets: [
      {
        data: [approvedCount, reviewCount, rejectedCount],
        backgroundColor: [
          '#10B981', // green
          '#F59E0B', // yellow
          '#EF4444', // red
        ],
        borderColor: [
          '#059669',
          '#D97706',
          '#DC2626',
        ],
        borderWidth: 2,
      },
    ],
  }

  // Case scores comparison chart
  const caseScoresData = {
    labels: results.map((result: any) => result.case_id),
    datasets: [
      {
        label: 'Score (%)',
        data: results.map((result: any) => result.percentage || 0),
        backgroundColor: results.map((result: any) => {
          const score = result.percentage || 0
          if (score >= 80) return '#10B981'
          if (score >= 60) return '#F59E0B'
          return '#EF4444'
        }),
        borderColor: results.map((result: any) => {
          const score = result.percentage || 0
          if (score >= 80) return '#059669'
          if (score >= 60) return '#D97706'
          return '#DC2626'
        }),
        borderWidth: 2,
      },
    ],
  }

  // Individual criteria performance across all cases
  const getCriteriaPerformanceData = () => {
    if (results.length === 0) return null

    const criteriaNames = Object.keys(results[0]?.individual_scores || {})
    const datasets = criteriaNames.map((criteria, index) => ({
      label: criteria,
      data: results.map((result: any) => result.individual_scores?.[criteria] || 0),
      backgroundColor: `hsla(${index * 360 / criteriaNames.length}, 70%, 60%, 0.6)`,
      borderColor: `hsla(${index * 360 / criteriaNames.length}, 70%, 50%, 1)`,
      borderWidth: 2,
    }))

    return {
      labels: results.map((result: any) => result.case_id),
      datasets,
    }
  }

  const criteriaPerformanceData = getCriteriaPerformanceData()

  // Radar chart for average performance by criteria
  const getRadarData = () => {
    if (results.length === 0) return null

    const criteriaNames = Object.keys(results[0]?.individual_scores || {})
    const avgScores = criteriaNames.map(criteria => {
      const scores = results.map((result: any) => result.individual_scores?.[criteria] || 0)
      return scores.reduce((sum: number, score: number) => sum + score, 0) / scores.length
    })

    return {
      labels: criteriaNames,
      datasets: [
        {
          label: 'Average Performance',
          data: avgScores,
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(59, 130, 246, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
        },
      ],
    }
  }

  const radarData = getRadarData()

  // Score distribution chart
  const getScoreDistributionData = () => {
    const ranges = ['0-20', '21-40', '41-60', '61-80', '81-100']
    const distribution = [0, 0, 0, 0, 0]

    results.forEach((result: any) => {
      const score = result.percentage || 0
      if (score <= 20) distribution[0]++
      else if (score <= 40) distribution[1]++
      else if (score <= 60) distribution[2]++
      else if (score <= 80) distribution[3]++
      else distribution[4]++
    })

    return {
      labels: ranges,
      datasets: [
        {
          data: distribution,
          backgroundColor: [
            '#EF4444', // red
            '#F97316', // orange
            '#F59E0B', // yellow
            '#84CC16', // lime
            '#10B981', // green
          ],
          borderColor: [
            '#DC2626',
            '#EA580C',
            '#D97706',
            '#65A30D',
            '#059669',
          ],
          borderWidth: 2,
        },
      ],
    }
  }

  const scoreDistributionData = getScoreDistributionData()

  // Get comparison data for selected criteria
  const getComparisonData = () => {
    if (!selectedCriteria) return null; 

    const resultsSource = data?.analysisResult?.results || [];
    if (resultsSource.length === 0) return null;

    const currentCriterionDisplayInfo = criteriaForComparison.find(c => c.name === selectedCriteria);
    const idealDisplayValue = currentCriterionDisplayInfo?.idealValue || 'N/A';

    const originalCriterionData = criteria.find((c: any) =>
      c.parameter && c.parameter.toLowerCase() === selectedCriteria.toLowerCase()
    );
    const minRequiredValue = originalCriterionData?.min_value;

    const displayValueForRequired = (idealDisplayValue !== 'N/A')
      ? idealDisplayValue
      : (minRequiredValue !== null && minRequiredValue !== undefined ? String(minRequiredValue) : 'N/A');

    const caseComparisons = resultsSource.map((result: any, index: number) => {
      let actualValueForCriterion = 'N/A';
      let scoreForCriterion = 0;

      if (result.metric_scores && Array.isArray(result.metric_scores)) {
        const lowerSelectedCriteria = selectedCriteria.toLowerCase().trim();
        const matchedMetric = result.metric_scores.find((ms: any) => {
          if (ms.metric_name) {
            const metricNameFromBackend = String(ms.metric_name).toLowerCase().trim();
            return metricNameFromBackend === lowerSelectedCriteria;
          }
          return false;
        });

        if (matchedMetric) {
          actualValueForCriterion = (matchedMetric.actual_value !== null && matchedMetric.actual_value !== undefined && String(matchedMetric.actual_value).trim() !== '')
            ? String(matchedMetric.actual_value)
            : 'N/A';
          scoreForCriterion = matchedMetric.score || 0;
        } 
      } 

      return {
        caseName: result.case_id || `Case ${index + 1}`,
        actualValue: actualValueForCriterion,
        score: scoreForCriterion, 
      };
    });

    return {
      criterionName: selectedCriteria, 
      requiredValueDisplay: displayValueForRequired,
      caseComparisons: caseComparisons,
    };
  };

  const comparisonData = getComparisonData()

  // Chart options are no longer needed for this specific display, but keep for other charts
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  }

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  }

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 2
        }
      },
    },
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalCases}</div>
              <p className="text-xs text-muted-foreground">
                Cases analyzed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <Calculator className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getScoreColor(avgScore)}`}>
                {avgScore.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Overall performance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Eligible Cases</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{approvedCount}</div>
              <p className="text-xs text-muted-foreground">
                {totalCases > 0 ? ((approvedCount / totalCases) * 100).toFixed(1) : 0}% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Criteria Count</CardTitle>
              <Target className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{criteria.length}</div>
              <p className="text-xs text-muted-foreground">
                Evaluation parameters
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="results">Results</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="criteria">Criteria</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Status Distribution and Top Performers */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5" />
                    Eligibility Status Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <div className="h-64 w-full flex justify-center items-center">
                    <Pie data={statusPieData} options={pieOptions} />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Top Performing Cases
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {results
                      .sort((a: any, b: any) => (b.percentage || 0) - (a.percentage || 0))
                      .slice(0, 5)
                      .map((result: any, index: number) => (
                        <div key={result.case_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">
                              {index + 1}
                            </div>
                            <span className="font-medium">{result.case_id}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`font-semibold ${getScoreColor(result.percentage || 0)}`}>
                              {(result.percentage || 0).toFixed(1)}%
                            </span>
                            <Badge className={getStatusColor(result.eligibility_status)}>
                              {result.eligibility_status}
                            </Badge>
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Detailed Results
                </CardTitle>
                <CardDescription>
                  Individual case analysis and scoring breakdown
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.map((result: any) => (
                    <div key={result.case_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-lg">{result.case_id}</h3>
                        <div className="flex items-center gap-2">
                          <span className={`text-xl font-bold ${getScoreColor(result.percentage || 0)}`}>
                            {(result.percentage || 0).toFixed(1)}%
                          </span>
                          <Badge className={getStatusColor(result.eligibility_status)}>
                            {result.eligibility_status}
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Overall Score</span>
                          <span>{result.total_score?.toFixed(1) || 0} / {result.max_possible_score?.toFixed(1) || 0}</span>
                        </div>
                        <Progress value={result.percentage || 0} className="h-2" />
                      </div>

                      {result.individual_scores && (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {Object.entries(result.individual_scores).map(([param, score]: [string, any]) => (
                            <div key={param} className="bg-gray-50 p-3 rounded">
                              <div className="text-sm font-medium mb-1">{param}</div>
                              <div className="text-lg font-semibold text-blue-600">{score?.toFixed(1) || 0}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Analysis Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{totalCases}</div>
                    <div className="text-sm text-blue-800">Total Cases Analyzed</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{avgScore.toFixed(1)}%</div>
                    <div className="text-sm text-green-800">Average Score</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{criteria.length}</div>
                    <div className="text-sm text-purple-800">Evaluation Criteria</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {totalCases > 0 ? ((approvedCount / totalCases) * 100).toFixed(1) : 0}%
                    </div>
                    <div className="text-sm text-orange-800">Approval Rate</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Case Scores Comparison */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Case Scores Comparison
                </CardTitle>
                <CardDescription>
                  Overall performance scores for all cases
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <div className="h-80 w-full">
                  <Bar data={caseScoresData} options={chartOptions} />
                </div>
              </CardContent>
            </Card>

            {/* Criteria Performance and Score Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {criteriaPerformanceData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Criteria Performance by Case
                    </CardTitle>
                    <CardDescription>
                      Individual criteria scores across all cases
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex justify-center">
                    <div className="h-80 w-full">
                      <Bar data={criteriaPerformanceData} options={chartOptions} />
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <PieChart className="h-5 w-5" />
                    Score Distribution
                  </CardTitle>
                  <CardDescription>
                    Distribution of scores across different ranges
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <div className="h-80 w-full flex justify-center items-center">
                    <Doughnut data={scoreDistributionData} options={pieOptions} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Radar Chart and Compare Criteria */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {radarData && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="h-5 w-5" />
                      Average Performance Radar
                    </CardTitle>
                    <CardDescription>
                      Multi-dimensional view of average criteria performance
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex justify-center">
                    <div className="h-80 w-full flex justify-center items-center">
                      <Radar data={radarData} options={radarOptions} />
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <GitCompare className="h-5 w-5" />
                    Compare Criteria
                  </CardTitle>
                  <CardDescription>
                    Side-by-side comparison of case values for the selected criterion
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Select value={selectedCriteria} onValueChange={setSelectedCriteria}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a criterion to compare" />
                      </SelectTrigger>
                      <SelectContent>
                        {criteria.length > 0 ? (
                          criteria.map((criterion: any, index: number) => (
                            <SelectItem key={index} value={criterion.parameter}>
                              {criterion.parameter}
                            </SelectItem>
                          ))
                        ) : (
                          criteriaForComparison.map((criterion: any, index: number) => (
                            <SelectItem key={index} value={criterion.name}>
                              {criterion.name}
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                    
                    {comparisonData && comparisonData.caseComparisons && (
                      <div className="mt-4 space-y-3 p-3 bg-gray-50 rounded-lg">
                        <div className="font-semibold text-lg mb-2 text-center">
                          {comparisonData.criterionName}
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-sm font-medium pb-2 border-b">
                          <div>Case ID</div>
                          <div className="text-center">Actual Value</div>
                          <div className="text-right">Score (0-10)</div>
                        </div>
                        {/* Ideal/Required Value Display */}
                        <div className="grid grid-cols-3 gap-2 text-sm py-2 border-b border-dashed">
                          <div className="font-medium text-blue-600">Ideal / Required</div>
                          <div className="text-center font-medium text-blue-600">
                            {comparisonData.requiredValueDisplay}
                          </div>
                          <div className="text-right font-medium text-blue-600">-</div>
                        </div>
                        {/* Case Values Display */}
                        {comparisonData.caseComparisons.map((comp: any, index: number) => (
                          <div key={index} className="grid grid-cols-3 gap-2 text-sm py-1">
                            <div>{comp.caseName}</div>
                            <div className="text-center">{comp.actualValue}</div>
                            <div className={`text-right font-semibold ${getScoreColor(comp.score * 10)}`}>
                              {comp.score.toFixed(1)}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {(!comparisonData || !comparisonData.caseComparisons || comparisonData.caseComparisons.length === 0) && selectedCriteria && (
                      <div className="text-center text-gray-500 py-8">
                        No comparison data available for "{selectedCriteria}" or no cases processed.
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="criteria" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Eligibility Criteria
                </CardTitle>
                <CardDescription>
                  Parameters and weights used for evaluation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {criteria.map((criterion: any, index: number) => {
                    // Get ideal value from scoring intervals (highest score interval)
                    let idealValue = null
                    if (criterion.scoring_intervals && criterion.scoring_intervals.length > 0) {
                      // Find the interval with the highest score (score 10)
                      const bestInterval = criterion.scoring_intervals.find((interval: any) => interval.score === 10)
                      if (bestInterval) {
                        idealValue = bestInterval.interval
                      } else {
                        // Fallback to highest scoring interval
                        const highestInterval = criterion.scoring_intervals.reduce((best: any, current: any) => 
                          current.score > best.score ? current : best
                        )
                        idealValue = highestInterval.interval
                      }
                    }

                    return (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold">{criterion.parameter}</h3>
                          <Badge variant="outline">{criterion.weight}% weight</Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          {criterion.min_value !== null && (
                            <div>
                              <span className="text-gray-500">Min Required:</span>
                              <span className="ml-2 font-medium">{criterion.min_value}</span>
                            </div>
                          )}
                          {idealValue && (
                            <div>
                              <span className="text-gray-500">Ideal Value:</span>
                              <span className="ml-2 font-medium text-green-600">{idealValue}</span>
                            </div>
                          )}
                          {criterion.preferred_value && (
                            <div>
                              <span className="text-gray-500">Preferred:</span>
                              <span className="ml-2 font-medium">{criterion.preferred_value}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 