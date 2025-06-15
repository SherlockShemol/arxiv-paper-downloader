import axios from 'axios'
import { ElMessage } from 'element-plus'

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Do something before request is sent
    console.log('Sending request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    // Do something with request error
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Debug information collector
const getDebugCollector = () => {
  return window.debugCollector || {
    addApiCall: () => {},
    addNetworkLog: () => {}
  }
}

// Request interceptor
api.interceptors.request.use(
  config => {
    const debugCollector = getDebugCollector()
    config.metadata = { startTime: Date.now() }
    debugCollector.addNetworkLog('info', `Initiating API request: ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data)
    return config
  },
  error => {
    const debugCollector = getDebugCollector()
    debugCollector.addNetworkLog('error', 'Request configuration error', error.message)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    const debugCollector = getDebugCollector()
    const duration = Date.now() - (response.config.metadata?.startTime || 0)
    
    debugCollector.addApiCall(
      response.config.method?.toUpperCase() || 'GET',
      response.config.url || '',
      response.status,
      duration
    )
    
    debugCollector.addNetworkLog('success', 
      `API request successful: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`,
      `Status code: ${response.status}`
    )
    
    return response.data
  },
  error => {
    const debugCollector = getDebugCollector()
    const duration = Date.now() - (error.config?.metadata?.startTime || 0)
    
    console.error('API request error:', error)
    
    let errorMessage = 'Unknown error'
    let statusCode = 0
    
    if (error.response) {
      // Server returned error status code
      statusCode = error.response.status
      errorMessage = error.response.data?.message || error.response.data?.error || 'Server error'
      
      debugCollector.addApiCall(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        statusCode,
        duration,
        errorMessage
      )
      
      debugCollector.addNetworkLog('error', 
        `API request failed: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
        `Status code: ${statusCode}, Error: ${errorMessage}`
      )
      
      ElMessage.error(`Request failed: ${errorMessage}`)
    } else if (error.request) {
      // Request sent but no response received
      errorMessage = 'Network connection failed, please check network settings'
      
      debugCollector.addApiCall(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        0,
        duration,
        errorMessage
      )
      
      debugCollector.addNetworkLog('error', 
        `Network connection failed: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
        'Request sent but no response received'
      )
      
      ElMessage.error('Network connection failed, please check network settings')
    } else {
      // Other errors
      errorMessage = 'Unknown error'
      
      debugCollector.addNetworkLog('error', 'Request configuration error', error.message)
      ElMessage.error('Request configuration error')
    }
    
    return Promise.reject(error)
  }
)

// Paper search API
export const searchPapers = async (params) => {
  return api.get('/papers/search', { params })
}

// Get paper details
export const getPaperDetail = async (paperId) => {
  return api.get(`/papers/${paperId}`)
}

// Download paper
export const downloadPaper = async (paperId, options = {}) => {
  return api.post('/papers/download', {
    paper_id: paperId,
    ...options
  })
}

// Batch download papers
export const batchDownloadPapers = async (paperIds, options = {}) => {
  return api.post('/papers/batch-download', {
    paper_ids: paperIds,
    ...options
  })
}

// Get download list
export const getDownloadList = async (params = {}) => {
  return api.get('/downloads', { params })
}

// Get download status
export const getDownloadStatus = async (downloadId) => {
  return api.get(`/downloads/${downloadId}/status`)
}

// Pause download
export const pauseDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/pause`)
}

// Resume download
export const resumeDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/resume`)
}

// Cancel download
export const cancelDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/cancel`)
}

// Delete download record
export const deleteDownload = async (downloadId) => {
  return api.delete(`/downloads/${downloadId}`)
}

// Clear completed downloads
export const clearCompletedDownloads = async () => {
  return api.post('/downloads/clear-completed')
}

// Get statistics data
export const getStatistics = async (timeRange = '30d') => {
  return api.get('/statistics', {
    params: { time_range: timeRange }
  })
}

// Get download trend data
export const getDownloadTrend = async (timeRange = '30d') => {
  return api.get('/statistics/download-trend', {
    params: { time_range: timeRange }
  })
}

// Get subject classification statistics
export const getCategoryStats = async (timeRange = '30d') => {
  return api.get('/statistics/categories', {
    params: { time_range: timeRange }
  })
}

// Get download speed distribution
export const getSpeedDistribution = async (timeRange = '30d') => {
  return api.get('/statistics/speed-distribution', {
    params: { time_range: timeRange }
  })
}

// Get system settings
export const getSettings = async () => {
  return api.get('/settings')
}

// Save system settings
export const saveSettings = async (settings) => {
  return api.post('/settings', settings)
}

// Reset settings to default
export const resetSettings = async () => {
  return api.post('/settings/reset')
}

// Get system information
export const getSystemInfo = async () => {
  return api.get('/system/info')
}

// Clear cache
export const clearCache = async () => {
  return api.post('/system/clear-cache')
}

// Check for updates
export const checkUpdates = async () => {
  return api.get('/system/check-updates')
}

// Get search history
export const getSearchHistory = async (limit = 20) => {
  return api.get('/search/history', {
    params: { limit }
  })
}

// Save search history
export const saveSearchHistory = async (query, filters = {}) => {
  return api.post('/search/history', {
    query,
    filters
  })
}

// Clear search history
export const clearSearchHistory = async () => {
  return api.delete('/search/history')
}

// Get search suggestions
export const getSearchSuggestions = async (query) => {
  return api.get('/search/suggestions', {
    params: { q: query }
  })
}

// Get popular searches
export const getPopularSearches = async (limit = 10) => {
  return api.get('/search/popular', {
    params: { limit }
  })
}

// File operation API
export const openFile = async (filePath) => {
  return api.post('/files/open', { file_path: filePath })
}

// Open folder
export const openFolder = async (folderPath) => {
  return api.post('/files/open-folder', { folder_path: folderPath })
}

// Get file information
export const getFileInfo = async (filePath) => {
  return api.get('/files/info', {
    params: { file_path: filePath }
  })
}

// Delete file
export const deleteFile = async (filePath) => {
  return api.delete('/files', {
    params: { file_path: filePath }
  })
}

// Rename file
export const renameFile = async (oldPath, newPath) => {
  return api.post('/files/rename', {
    old_path: oldPath,
    new_path: newPath
  })
}

// Get directory list
export const getDirectoryList = async (dirPath = '') => {
  return api.get('/files/directory', {
    params: { dir_path: dirPath }
  })
}

// Create directory
export const createDirectory = async (dirPath) => {
  return api.post('/files/directory', { dir_path: dirPath })
}

// Export data
export const exportData = async (dataType, format = 'json', timeRange = '30d') => {
  return api.get('/export', {
    params: {
      type: dataType,
      format,
      time_range: timeRange
    },
    responseType: 'blob'
  })
}

// Health check
export const healthCheck = async () => {
  return api.get('/health')
}

// WebSocket connection management
let wsConnection = null
let wsReconnectTimer = null
let wsReconnectAttempts = 0
const maxReconnectAttempts = 5

// Create WebSocket connection
export const createWebSocketConnection = (onMessage, onError, onClose) => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    return wsConnection
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws`
  
  wsConnection = new WebSocket(wsUrl)
  
  wsConnection.onopen = () => {
    console.log('WebSocket connection established')
    wsReconnectAttempts = 0
    if (wsReconnectTimer) {
      clearTimeout(wsReconnectTimer)
      wsReconnectTimer = null
    }
  }
  
  wsConnection.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage && onMessage(data)
    } catch (error) {
      console.error('WebSocket message parsing error:', error)
    }
  }
  
  wsConnection.onerror = (error) => {
    console.error('WebSocket error:', error)
    onError && onError(error)
  }
  
  wsConnection.onclose = (event) => {
    console.log('WebSocket connection closed:', event.code, event.reason)
    onClose && onClose(event)
    
    // Auto reconnect
    if (wsReconnectAttempts < maxReconnectAttempts) {
      wsReconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, wsReconnectAttempts), 30000)
      console.log(`Attempting reconnection in ${delay}ms (${wsReconnectAttempts}/${maxReconnectAttempts})`)
      
      wsReconnectTimer = setTimeout(() => {
        createWebSocketConnection(onMessage, onError, onClose)
      }, delay)
    } else {
      console.log('WebSocket reconnection attempts exceeded limit')
      ElMessage.error('Connection to server lost, please refresh the page and try again')
    }
  }
  
  return wsConnection
}

// Send WebSocket message
export const sendWebSocketMessage = (message) => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    wsConnection.send(JSON.stringify(message))
    return true
  }
  console.warn('WebSocket connection not established or closed')
  return false
}

// Close WebSocket connection
export const closeWebSocketConnection = () => {
  if (wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer)
    wsReconnectTimer = null
  }
  wsReconnectAttempts = 0
}

// Default export object containing all API methods
export default {
  searchPapers,
  getPaperDetail,
  downloadPaper,
  batchDownloadPapers,
  getDownloadList,
  getDownloadStatus,
  pauseDownload,
  resumeDownload,
  cancelDownload,
  deleteDownload,
  clearCompletedDownloads,
  getStatistics,
  getDownloadTrend,
  getCategoryStats,
  getSpeedDistribution,
  getSettings,
  saveSettings,
  resetSettings,
  getSystemInfo,
  clearCache,
  checkUpdates,
  getSearchHistory,
  saveSearchHistory,
  clearSearchHistory,
  exportData,
  importData,
  validateImportData,
  connectWebSocket,
  sendWebSocketMessage,
  closeWebSocketConnection
}