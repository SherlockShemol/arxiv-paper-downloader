// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// Paper Types
export interface Paper {
  id: string
  title: string
  authors: string[]
  abstract: string
  published: string
  updated: string
  categories: string[]
  pdf_url: string
  entry_id: string
  summary: string
  links: PaperLink[]
}

export interface PaperLink {
  href: string
  rel: string
  type?: string
  title?: string
}

// Search Types
export interface SearchParams {
  query: string
  max_results: number
  date_from?: string
  date_to?: string
  categories?: string[]
}

export interface SearchResponse {
  papers: Paper[]
  total_results: number
  start_index: number
}

// Download Types
export interface DownloadItem {
  id: string
  paper_id: string
  title: string
  status: DownloadStatus
  progress: number
  file_path?: string
  file_size?: number
  download_speed?: number
  error_message?: string
  created_at: string
  updated_at: string
  paused?: boolean
  retry_count?: number
}

export type DownloadStatus = 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled' | 'paused'

// Statistics Types
export interface DownloadStats {
  total_downloads: number
  successful_downloads: number
  failed_downloads: number
  total_size: number
  downloads_by_date: Record<string, number>
  downloads_by_category: Record<string, number>
}

// Settings Types
export interface AppSettings {
  download_path: string
  max_concurrent_downloads: number
  auto_download: boolean
  notification_enabled: boolean
  theme: 'light' | 'dark' | 'auto'
  language: string
}

// Component Props Types
export interface SearchFormProps {
  modelValue?: SearchParams
  loading?: boolean
}

export interface PaperCardProps {
  paper: Paper
  showDownloadButton?: boolean
  compact?: boolean
}

export interface DownloadManagerProps {
  downloads: DownloadItem[]
  showCompleted?: boolean
}

// Event Types
export interface SearchFormEmits {
  (e: 'update:modelValue', value: SearchParams): void
  (e: 'search', params: SearchParams): void
}

export interface PaperCardEmits {
  (e: 'download', paper: Paper): void
  (e: 'view-details', paper: Paper): void
}

export interface DownloadManagerEmits {
  (e: 'refresh'): void
  (e: 'openFile', download: DownloadItem): void
  (e: 'pauseResume', download: DownloadItem): void
  (e: 'retry', download: DownloadItem): void
  (e: 'remove', download: DownloadItem): void
  (e: 'clearCompleted'): void
}

// Additional Types for Enhanced Components
export interface SortOption {
  field: string
  label: string
  order: 'asc' | 'desc'
}

export interface ViewMode {
  type: 'list' | 'grid'
}

export interface SearchResultsListProps {
  papers: Paper[]
  loading?: boolean
  hasMore?: boolean
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  viewMode?: 'list' | 'grid'
}

export interface SearchResultsListEmits {
  (e: 'download', paper: Paper): void
  (e: 'loadMore'): void
  (e: 'sort', field: string, order: 'asc' | 'desc'): void
  (e: 'viewModeChange', mode: 'list' | 'grid'): void
}

export interface DebugCollector {
  addLog: (level: 'info' | 'warn' | 'error', message: string, data?: any) => void
  getLogs: () => DebugLog[]
  clearLogs: () => void
  exportLogs: () => string
}

export interface DebugLog {
  id: string
  timestamp: string
  level: 'info' | 'warn' | 'error'
  message: string
  data?: any
  source?: string
}

// Store Types
export interface AppState {
  backendConnected: boolean
  searchResults: Paper[]
  downloads: DownloadItem[]
  settings: AppSettings
  loading: {
    search: boolean
    download: boolean
    connection: boolean
  }
}