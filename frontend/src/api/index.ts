import axios from 'axios'
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse, SearchParams, SearchResponse, Paper, DownloadItem, AppSettings, DownloadStats } from '@/types'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor (removed duplicate - using the one below with debug collector)

// Debug information collector interface
interface DebugCollector {
  addApiCall: (method: string, url: string, status: number, duration: number, error?: string) => void
  addNetworkLog: (level: string, message: string, details?: any) => void
}

// Get debug collector from window
const getDebugCollector = (): DebugCollector => {
  return (window as any).debugCollector || {
    addApiCall: () => {},
    addNetworkLog: () => {},
  }
}

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    const debugCollector = getDebugCollector()
    ;(config as any).metadata = { startTime: Date.now() }
    debugCollector.addNetworkLog(
      'info',
      `Initiating API request: ${config.method?.toUpperCase()} ${config.url}`,
      config.params || config.data
    )
    console.log('Sending request:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    const debugCollector = getDebugCollector()
    debugCollector.addNetworkLog('error', 'Request configuration error', error.message)
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const debugCollector = getDebugCollector()
    const duration = Date.now() - ((response.config as any).metadata?.startTime || 0)

    debugCollector.addApiCall(
      response.config.method?.toUpperCase() || 'GET',
      response.config.url || '',
      response.status,
      duration
    )

    debugCollector.addNetworkLog(
      'success',
      `API request successful: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`,
      `Status code: ${response.status}`
    )

    return response.data
  },
  (error: AxiosError) => {
    const debugCollector = getDebugCollector()
    const duration = Date.now() - ((error.config as any)?.metadata?.startTime || 0)

    console.error('API request error:', error)

    let errorMessage = 'Unknown error'
    let statusCode = 0

    if (error.response) {
      // Server returned error status code
      statusCode = error.response.status
      const responseData = error.response.data as any
      errorMessage = responseData?.message || responseData?.error || 'Server error'

      debugCollector.addApiCall(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        statusCode,
        duration,
        errorMessage
      )

      debugCollector.addNetworkLog(
        'error',
        `API request failed: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
        `Status code: ${statusCode}, Error: ${errorMessage}`
      )

      ElMessage.error(`Request failed: ${errorMessage}`)
    } else if (error.request) {
      // Request sent but no response received
      errorMessage = 'Network connection failed, please check network settings'
      debugCollector.addNetworkLog('error', 'Network connection failed', error.message)
      ElMessage.error(errorMessage)
    } else {
      // Something else happened
      errorMessage = error.message || 'Request configuration error'
      debugCollector.addNetworkLog('error', 'Request setup error', error.message)
      ElMessage.error(errorMessage)
    }

    return Promise.reject({
      success: false,
      error: errorMessage,
      statusCode,
    })
  }
)

// API methods
export const api = {
  // Connection test
  async testConnection(): Promise<ApiResponse<{ status: string }>> {
    try {
      const response = await apiClient.get('/health')
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Connection failed',
      }
    }
  },

  // Search papers
  async searchPapers(params: SearchParams): Promise<ApiResponse<SearchResponse>> {
    try {
      const response = await apiClient.post('/search', params)
      console.log('Raw API response:', response) // Debug log
      // Backend returns the data directly, not wrapped in another data property
      return {
        success: response.success || true,
        data: response, // Use response directly since backend returns {success, papers, total}
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Search failed',
      }
    }
  },

  // Download paper
  async downloadPaper(paperId: string): Promise<ApiResponse<{ download_id: string }>> {
    try {
      const response = await apiClient.post('/download', { paper_id: paperId })
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Download failed',
      }
    }
  },

  // Get downloads
  async getDownloads(): Promise<ApiResponse<DownloadItem[]>> {
    try {
      const response = await apiClient.get('/downloads')
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to fetch downloads',
      }
    }
  },

  // Cancel download
  async cancelDownload(downloadId: string): Promise<ApiResponse<void>> {
    try {
      await apiClient.delete(`/downloads/${downloadId}`)
      return {
        success: true,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to cancel download',
      }
    }
  },

  // Get download status
  async getDownloadStatus(downloadId: string): Promise<ApiResponse<DownloadItem>> {
    try {
      const response = await apiClient.get(`/downloads/${downloadId}/status`)
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to get download status',
      }
    }
  },

  // Get settings
  async getSettings(): Promise<ApiResponse<AppSettings>> {
    try {
      const response = await apiClient.get('/settings')
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to fetch settings',
      }
    }
  },

  // Update settings
  async updateSettings(settings: Partial<AppSettings>): Promise<ApiResponse<AppSettings>> {
    try {
      const response = await apiClient.put('/settings', settings)
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to update settings',
      }
    }
  },

  // Get statistics
  async getStatistics(): Promise<ApiResponse<DownloadStats>> {
    try {
      const response = await apiClient.get('/statistics')
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to fetch statistics',
      }
    }
  },

  // Get paper details
  async getPaperDetails(paperId: string): Promise<ApiResponse<Paper>> {
    try {
      const response = await apiClient.get(`/papers/${paperId}`)
      return {
        success: true,
        data: response.data,
      }
    } catch (error) {
      return {
        success: false,
        error: (error as any).error || 'Failed to fetch paper details',
      }
    }
  },
}

export default api