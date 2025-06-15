import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    // 对请求错误做些什么
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 调试信息收集器（从window获取，如果App.vue已加载）
const getDebugCollector = () => {
  return window.debugCollector || {
    addApiCall: () => {},
    addNetworkLog: () => {}
  }
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    const debugCollector = getDebugCollector()
    config.metadata = { startTime: Date.now() }
    debugCollector.addNetworkLog('info', `发起API请求: ${config.method?.toUpperCase()} ${config.url}`, config.params || config.data)
    return config
  },
  error => {
    const debugCollector = getDebugCollector()
    debugCollector.addNetworkLog('error', '请求配置错误', error.message)
    return Promise.reject(error)
  }
)

// 响应拦截器
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
      `API请求成功: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`,
      `状态码: ${response.status}`
    )
    
    return response.data
  },
  error => {
    const debugCollector = getDebugCollector()
    const duration = Date.now() - (error.config?.metadata?.startTime || 0)
    
    console.error('API请求错误:', error)
    
    let errorMessage = '未知错误'
    let statusCode = 0
    
    if (error.response) {
      // 服务器返回错误状态码
      statusCode = error.response.status
      errorMessage = error.response.data?.message || error.response.data?.error || '服务器错误'
      
      debugCollector.addApiCall(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        statusCode,
        duration,
        errorMessage
      )
      
      debugCollector.addNetworkLog('error', 
        `API请求失败: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
        `状态码: ${statusCode}, 错误: ${errorMessage}`
      )
      
      ElMessage.error(`请求失败: ${errorMessage}`)
    } else if (error.request) {
      // 请求发出但没有收到响应
      errorMessage = '网络连接失败'
      
      debugCollector.addApiCall(
        error.config?.method?.toUpperCase() || 'GET',
        error.config?.url || '',
        0,
        duration,
        errorMessage
      )
      
      debugCollector.addNetworkLog('error', 
        `网络连接失败: ${error.config?.method?.toUpperCase()} ${error.config?.url} (${duration}ms)`,
        '请求发出但没有收到响应'
      )
      
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // 其他错误
      errorMessage = '请求配置错误'
      
      debugCollector.addNetworkLog('error', '请求配置错误', error.message)
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 论文搜索 API
export const searchPapers = async (params) => {
  return api.get('/papers/search', { params })
}

// 获取论文详情
export const getPaperDetail = async (paperId) => {
  return api.get(`/papers/${paperId}`)
}

// 下载论文
export const downloadPaper = async (paperId, options = {}) => {
  return api.post('/papers/download', {
    paper_id: paperId,
    ...options
  })
}

// 批量下载论文
export const batchDownloadPapers = async (paperIds, options = {}) => {
  return api.post('/papers/batch-download', {
    paper_ids: paperIds,
    ...options
  })
}

// 获取下载列表
export const getDownloadList = async (params = {}) => {
  return api.get('/downloads', { params })
}

// 获取下载状态
export const getDownloadStatus = async (downloadId) => {
  return api.get(`/downloads/${downloadId}/status`)
}

// 暂停下载
export const pauseDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/pause`)
}

// 恢复下载
export const resumeDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/resume`)
}

// 取消下载
export const cancelDownload = async (downloadId) => {
  return api.post(`/downloads/${downloadId}/cancel`)
}

// 删除下载记录
export const deleteDownload = async (downloadId) => {
  return api.delete(`/downloads/${downloadId}`)
}

// 清除已完成的下载
export const clearCompletedDownloads = async () => {
  return api.post('/downloads/clear-completed')
}

// 获取统计数据
export const getStatistics = async (timeRange = '30d') => {
  return api.get('/statistics', {
    params: { time_range: timeRange }
  })
}

// 获取下载趋势数据
export const getDownloadTrend = async (timeRange = '30d') => {
  return api.get('/statistics/download-trend', {
    params: { time_range: timeRange }
  })
}

// 获取学科分类统计
export const getCategoryStats = async (timeRange = '30d') => {
  return api.get('/statistics/categories', {
    params: { time_range: timeRange }
  })
}

// 获取下载速度分布
export const getSpeedDistribution = async (timeRange = '30d') => {
  return api.get('/statistics/speed-distribution', {
    params: { time_range: timeRange }
  })
}

// 获取系统设置
export const getSettings = async () => {
  return api.get('/settings')
}

// 保存系统设置
export const saveSettings = async (settings) => {
  return api.post('/settings', settings)
}

// 重置设置到默认值
export const resetSettings = async () => {
  return api.post('/settings/reset')
}

// 获取系统信息
export const getSystemInfo = async () => {
  return api.get('/system/info')
}

// 清除缓存
export const clearCache = async () => {
  return api.post('/system/clear-cache')
}

// 检查更新
export const checkUpdates = async () => {
  return api.get('/system/check-updates')
}

// 获取搜索历史
export const getSearchHistory = async (limit = 20) => {
  return api.get('/search/history', {
    params: { limit }
  })
}

// 保存搜索历史
export const saveSearchHistory = async (query, filters = {}) => {
  return api.post('/search/history', {
    query,
    filters
  })
}

// 清除搜索历史
export const clearSearchHistory = async () => {
  return api.delete('/search/history')
}

// 获取搜索建议
export const getSearchSuggestions = async (query) => {
  return api.get('/search/suggestions', {
    params: { q: query }
  })
}

// 获取热门搜索
export const getPopularSearches = async (limit = 10) => {
  return api.get('/search/popular', {
    params: { limit }
  })
}

// 文件操作 API
export const openFile = async (filePath) => {
  return api.post('/files/open', { file_path: filePath })
}

// 打开文件夹
export const openFolder = async (folderPath) => {
  return api.post('/files/open-folder', { folder_path: folderPath })
}

// 获取文件信息
export const getFileInfo = async (filePath) => {
  return api.get('/files/info', {
    params: { file_path: filePath }
  })
}

// 删除文件
export const deleteFile = async (filePath) => {
  return api.delete('/files', {
    params: { file_path: filePath }
  })
}

// 重命名文件
export const renameFile = async (oldPath, newPath) => {
  return api.post('/files/rename', {
    old_path: oldPath,
    new_path: newPath
  })
}

// 获取目录列表
export const getDirectoryList = async (dirPath = '') => {
  return api.get('/files/directory', {
    params: { dir_path: dirPath }
  })
}

// 创建目录
export const createDirectory = async (dirPath) => {
  return api.post('/files/directory', { dir_path: dirPath })
}

// 导出数据
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

// 健康检查
export const healthCheck = async () => {
  return api.get('/health')
}

// WebSocket 连接管理
let wsConnection = null
let wsReconnectTimer = null
let wsReconnectAttempts = 0
const maxReconnectAttempts = 5

// 创建 WebSocket 连接
export const createWebSocketConnection = (onMessage, onError, onClose) => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    return wsConnection
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws`
  
  wsConnection = new WebSocket(wsUrl)
  
  wsConnection.onopen = () => {
    console.log('WebSocket 连接已建立')
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
      console.error('WebSocket 消息解析错误:', error)
    }
  }
  
  wsConnection.onerror = (error) => {
    console.error('WebSocket 错误:', error)
    onError && onError(error)
  }
  
  wsConnection.onclose = (event) => {
    console.log('WebSocket 连接已关闭:', event.code, event.reason)
    onClose && onClose(event)
    
    // 自动重连
    if (wsReconnectAttempts < maxReconnectAttempts) {
      wsReconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, wsReconnectAttempts), 30000)
      console.log(`${delay}ms 后尝试重连 (${wsReconnectAttempts}/${maxReconnectAttempts})`)
      
      wsReconnectTimer = setTimeout(() => {
        createWebSocketConnection(onMessage, onError, onClose)
      }, delay)
    } else {
      console.log('WebSocket 重连次数已达上限')
      ElMessage.error('与服务器的连接已断开，请刷新页面重试')
    }
  }
  
  return wsConnection
}

// 发送 WebSocket 消息
export const sendWebSocketMessage = (message) => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    wsConnection.send(JSON.stringify(message))
    return true
  }
  console.warn('WebSocket 连接未建立或已关闭')
  return false
}

// 关闭 WebSocket 连接
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

// 默认导出包含所有API方法的对象
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