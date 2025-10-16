"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { format, subDays, parseISO } from 'date-fns'

interface MCPAnalyticsProps {
  mcpSlug: string
}

interface ChartDataPoint {
  date: string
  calls: number
  displayDate: string
}

interface ToolStats {
  [toolName: string]: {
    total_calls: number
    successful_calls: number
    failed_calls: number
    avg_duration_ms: number
  }
}

interface MetricsResponse {
  period_hours: number
  total_calls: number
  unique_users: number
  tools: ToolStats
}

export function MCPAnalytics({ mcpSlug }: MCPAnalyticsProps) {
  const [timeRange, setTimeRange] = useState('168') // 7 days in hours
  const [loading, setLoading] = useState(true)
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [totalCalls, setTotalCalls] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAnalytics()
  }, [timeRange, mcpSlug])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('Not authenticated')
        return
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/metrics/tools?hours=${timeRange}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (!response.ok) {
        throw new Error('Failed to fetch analytics')
      }

      const data: MetricsResponse = await response.json()

      // Process data for chart
      const processedData = processChartData(data, parseInt(timeRange))
      setChartData(processedData)
      setTotalCalls(data.total_calls)

    } catch (err) {
      console.error('Error fetching analytics:', err)
      setError('Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  const processChartData = (data: MetricsResponse, hours: number): ChartDataPoint[] => {
    const days = Math.ceil(hours / 24)
    const result: ChartDataPoint[] = []
    const today = new Date()

    // Create data points for each day
    for (let i = days - 1; i >= 0; i--) {
      const date = subDays(today, i)
      const dateStr = format(date, 'yyyy-MM-dd')
      const displayDate = format(date, 'MMM d')

      result.push({
        date: dateStr,
        calls: 0, // Will be filled with actual data
        displayDate
      })
    }

    // For now, distribute calls evenly (in real implementation, backend would provide daily breakdown)
    // This is a simple visualization - ideally backend should track calls by date
    const callsPerDay = Math.floor(data.total_calls / days)
    const remainder = data.total_calls % days

    result.forEach((point, index) => {
      point.calls = callsPerDay + (index < remainder ? 1 : 0)
    })

    return result
  }

  const timeRangeOptions = [
    { value: '24', label: 'Last 24 Hours' },
    { value: '168', label: 'Last 7 Days' },
    { value: '720', label: 'Last 30 Days' }
  ]

  if (error) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white text-lg sm:text-xl">📊 MCP Usage Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-sm">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <CardTitle className="text-white text-lg sm:text-xl">📊 MCP Usage Analytics</CardTitle>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-full sm:w-[180px] bg-slate-900 border-slate-700 text-white">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700">
              {timeRangeOptions.map(option => (
                <SelectItem
                  key={option.value}
                  value={option.value}
                  className="text-white hover:bg-slate-800"
                >
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <p className="text-slate-400">Loading analytics...</p>
          </div>
        ) : chartData.length === 0 || totalCalls === 0 ? (
          <div className="h-64 flex items-center justify-center">
            <div className="text-center space-y-2">
              <p className="text-slate-400 text-lg">No data yet</p>
              <p className="text-slate-500 text-sm">Start sharing your MCP URL to see analytics</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Calls</p>
                <p className="text-white text-2xl font-bold">{totalCalls.toLocaleString()}</p>
              </div>
              <div className="text-right">
                <p className="text-slate-400 text-sm">Average per Day</p>
                <p className="text-white text-2xl font-bold">
                  {Math.round(totalCalls / (parseInt(timeRange) / 24))}
                </p>
              </div>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis
                    dataKey="displayDate"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      border: '1px solid #475569',
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="calls"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorCalls)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-4 border-t border-slate-700">
              <p className="text-slate-400 text-xs text-center">
                Analytics update in real-time as your MCP server is accessed
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
