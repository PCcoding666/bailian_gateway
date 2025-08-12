import React, { useState, useEffect } from 'react'
import { apiCall } from '../services/api'

const HistoryPage = ({ user }) => {
  const [apiCalls, setApiCalls] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    modelName: ''
  })

  useEffect(() => {
    loadApiCalls()
  }, [filters])

  const loadApiCalls = async () => {
    try {
      setLoading(true)
      // In a real implementation, you would call the actual API endpoint
      // For now, we'll simulate the data
      const mockData = [
        {
          id: 1,
          user_id: user.id,
          model_name: 'qwen-vl-max-latest',
          api_endpoint: '/api/bailian/chat/completions',
          status_code: 200,
          request_tokens: 9,
          response_tokens: 12,
          total_tokens: 21,
          call_duration: 1200,
          client_ip: '192.168.1.100',
          created_at: '2023-01-01T10:00:00Z'
        },
        {
          id: 2,
          user_id: user.id,
          model_name: 'qwen-plus',
          api_endpoint: '/api/bailian/chat/completions',
          status_code: 200,
          request_tokens: 15,
          response_tokens: 8,
          total_tokens: 23,
          call_duration: 800,
          client_ip: '192.168.1.100',
          created_at: '2023-01-01T09:30:00Z'
        }
      ]
      
      setApiCalls(mockData)
    } catch (err) {
      setError(err.message || 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    })
  }

  const handleExport = () => {
    // In a real implementation, this would export the data
    alert('Export functionality would be implemented here')
  }

  if (loading) {
    return <div className="page-container">Loading...</div>
  }

  if (error) {
    return <div className="page-container error">{error}</div>
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <h1>History Records</h1>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="startDate">Start Date:</label>
          <input
            type="date"
            id="startDate"
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="endDate">End Date:</label>
          <input
            type="date"
            id="endDate"
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="filter-group">
          <label htmlFor="modelName">Model:</label>
          <select
            id="modelName"
            name="modelName"
            value={filters.modelName}
            onChange={handleFilterChange}
          >
            <option value="">All Models</option>
            <option value="qwen-vl-max-latest">Qwen VL Max</option>
            <option value="qwen-plus">Qwen Plus</option>
          </select>
        </div>
        
        <button onClick={handleExport} className="export-button">
          Export CSV
        </button>
      </div>

      {/* Stats Summary */}
      <div className="stats-summary">
        <div className="stat-card">
          <h3>Total Conversations</h3>
          <div className="stat-value">15</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Messages</h3>
          <div className="stat-value">128</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Tokens</h3>
          <div className="stat-value">2,560</div>
        </div>
        
        <div className="stat-card">
          <h3>Model Usage</h3>
          <div className="stat-value">2 Models</div>
        </div>
      </div>

      {/* Chart Section (Placeholder) */}
      <div className="chart-section">
        <h2>Usage Statistics</h2>
        <div className="chart-placeholder">
          Charts would be displayed here showing:
          <ul>
            <li>Daily usage statistics</li>
            <li>Model usage distribution</li>
            <li>Token consumption trends</li>
          </ul>
        </div>
      </div>

      {/* API Calls Table */}
      <div className="api-calls-section">
        <h2>API Call History</h2>
        <div className="table-container">
          <table className="api-calls-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Model</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Tokens</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {apiCalls.map(call => (
                <tr key={call.id}>
                  <td>{new Date(call.created_at).toLocaleString()}</td>
                  <td>{call.model_name}</td>
                  <td>{call.api_endpoint}</td>
                  <td>
                    <span className={`status-badge ${call.status_code === 200 ? 'success' : 'error'}`}>
                      {call.status_code}
                    </span>
                  </td>
                  <td>{call.total_tokens}</td>
                  <td>{call.call_duration}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default HistoryPage