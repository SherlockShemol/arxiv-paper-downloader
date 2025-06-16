import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Paper, DownloadItem, AppSettings, SearchParams, DownloadStats } from '@/types'
import api from '@/api'

export const useAppStore = defineStore('app', () => {
  // State
  const backendConnected = ref(false)
  const searchResults = ref<Paper[]>([])
  const downloads = ref<DownloadItem[]>([])
  const settings = ref<AppSettings>({
    download_path: '',
    max_concurrent_downloads: 3,
    auto_download: false,
    notification_enabled: true,
    theme: 'auto',
    language: 'en',
  })
  
  const loading = ref({
    search: false,
    download: false,
    connection: false,
  })

  // Getters
  const connectionStatus = computed(() => {
    if (loading.value.connection) return 'connecting'
    return backendConnected.value ? 'connected' : 'disconnected'
  })
  
  const hasSearchResults = computed(() => searchResults.value.length > 0)
  
  const activeDownloads = computed(() => 
    downloads.value.filter(d => d.status === 'downloading' || d.status === 'pending')
  )
  
  const completedDownloads = computed(() => 
    downloads.value.filter(d => d.status === 'completed')
  )
  
  const failedDownloads = computed(() => 
    downloads.value.filter(d => d.status === 'failed')
  )

  const downloadStats = computed((): DownloadStats => {
    const total = downloads.value.length
    const successful = completedDownloads.value.length
    const failed = failedDownloads.value.length
    
    // Group downloads by date
    const downloadsByDate: Record<string, number> = {}
    downloads.value.forEach(download => {
      const date = new Date(download.created_at).toISOString().split('T')[0]
      downloadsByDate[date] = (downloadsByDate[date] || 0) + 1
    })
    
    return {
      total_downloads: total,
      successful_downloads: successful,
      failed_downloads: failed,
      total_size: 0, // TODO: Calculate from actual file sizes
      downloads_by_date: downloadsByDate,
      downloads_by_category: {}, // TODO: Implement category grouping
    }
  })

  // Actions
  const testConnection = async (): Promise<boolean> => {
    loading.value.connection = true
    try {
      const response = await api.testConnection()
      backendConnected.value = response.success
      return response.success
    } catch (error) {
      console.error('Connection test failed:', error)
      backendConnected.value = false
      return false
    } finally {
      loading.value.connection = false
    }
  }

  const searchPapers = async (params: SearchParams): Promise<void> => {
    loading.value.search = true
    console.log('Store: Starting search with params:', params)
    try {
      const response = await api.searchPapersEnhanced(params)
      console.log('Store: Search response:', response)
      console.log('Store: Response success:', response.success)
      console.log('Store: Response data:', response.data)
      console.log('Store: Response data type:', typeof response.data)
      
      if (response.success && response.data) {
        console.log('Store: Success path - processing data')
        console.log('Store: response.data.papers:', response.data.papers)
        console.log('Store: response.data.papers type:', typeof response.data.papers)
        console.log('Store: response.data.papers length:', response.data.papers?.length)
        
        // Backend returns papers directly in response.data, not response.data.papers
        const papers = response.data.papers || response.data || []
        console.log('Store: Final papers array:', papers)
        console.log('Store: Final papers length:', papers.length)
        searchResults.value = papers
        console.log('Store: Updated searchResults.value:', searchResults.value)
      } else {
        console.error('Store: Search failed - error path')
        console.error('Store: Response error:', response.error)
        searchResults.value = []
      }
    } catch (error) {
      console.error('Store: Search failed - exception:', error)
      searchResults.value = []
    } finally {
      loading.value.search = false
      console.log('Store: Search completed, final searchResults.value:', searchResults.value)
    }
  }

  const downloadPaper = async (paper: Paper): Promise<void> => {
    loading.value.download = true
    try {
      const response = await api.downloadPaper(paper.id)
      if (response.success && response.data) {
        // Add to downloads list
        const downloadItem: DownloadItem = {
          id: response.data.download_id,
          paper_id: paper.id,
          title: paper.title,
          status: 'pending',
          progress: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        downloads.value.unshift(downloadItem)
      }
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      loading.value.download = false
    }
  }

  const updateDownloadStatus = (downloadId: string, status: DownloadItem['status'], progress?: number): void => {
    const download = downloads.value.find(d => d.id === downloadId)
    if (download) {
      download.status = status
      if (progress !== undefined) {
        download.progress = progress
      }
      download.updated_at = new Date().toISOString()
    }
  }

  const removeDownload = (downloadId: string): void => {
    const index = downloads.value.findIndex(d => d.id === downloadId)
    if (index !== -1) {
      downloads.value.splice(index, 1)
    }
  }

  const loadSettings = async (): Promise<void> => {
    try {
      const response = await api.getSettings()
      if (response.success && response.data) {
        settings.value = { ...settings.value, ...response.data }
      }
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const saveSettings = async (newSettings: Partial<AppSettings>): Promise<void> => {
    try {
      const response = await api.updateSettings(newSettings)
      if (response.success) {
        settings.value = { ...settings.value, ...newSettings }
      }
    } catch (error) {
      console.error('Failed to save settings:', error)
    }
  }

  const loadDownloads = async (): Promise<void> => {
    try {
      const response = await api.getDownloads()
      if (response.success && response.data) {
        downloads.value = response.data
      }
    } catch (error) {
      console.error('Failed to load downloads:', error)
    }
  }

  return {
    // State
    backendConnected,
    searchResults,
    downloads,
    settings,
    loading,
    
    // Getters
    connectionStatus,
    hasSearchResults,
    activeDownloads,
    completedDownloads,
    failedDownloads,
    downloadStats,
    
    // Actions
    testConnection,
    searchPapers,
    downloadPaper,
    updateDownloadStatus,
    removeDownload,
    loadSettings,
    saveSettings,
    loadDownloads,
  }
})