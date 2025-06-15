<template>
  <section class="downloads-section">
    <div class="section-header">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2M15,18V16H6V18H15M18,14V12H6V14H18Z" />
        </svg>
        Download Manager
        <span v-if="downloads.length > 0" class="downloads-count">({{ downloads.length }})</span>
      </h2>
      <p class="section-description">Track and manage your downloaded papers</p>
    </div>
    
    <div class="downloads-card">
      <!-- Controls Header -->
      <div class="downloads-header">
        <div class="header-left">
          <button @click="handleRefresh" :disabled="loading" class="refresh-btn">
            <svg class="action-icon" :class="{ 'spinning': loading }" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" />
            </svg>
            {{ loading ? 'Refreshing...' : 'Refresh' }}
          </button>
          
          <div class="filter-controls">
            <select v-model="statusFilter" class="status-filter">
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="downloading">Downloading</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
        
        <div class="header-right">
          <button 
            v-if="hasCompletedDownloads" 
            @click="handleClearCompleted" 
            class="clear-btn"
          >
            <svg class="action-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
            </svg>
            Clear Completed
          </button>
          
          <div class="view-toggle">
            <button 
              @click="viewMode = 'list'" 
              :class="{ active: viewMode === 'list' }"
              class="view-btn"
              title="List View"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9,5V9H21V5M9,19H21V15H9M9,14H21V10H9M4,9H8V5H4M4,19H8V15H4M4,14H8V10H4" />
              </svg>
            </button>
            <button 
              @click="viewMode = 'grid'" 
              :class="{ active: viewMode === 'grid' }"
              class="view-btn"
              title="Grid View"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M3,11H11V3H3M3,21H11V13H3M13,21H21V13H13M13,3V11H21V3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Downloads List -->
      <div v-if="filteredDownloads.length > 0" :class="['downloads-container', `view-${viewMode}`]">
        <div 
          v-for="download in filteredDownloads" 
          :key="download.id" 
          :class="['download-item', `status-${download.status}`, { 'grid-item': viewMode === 'grid' }]"
        >
          <div class="download-content">
            <div class="download-info">
              <h4 class="download-title">{{ download.title }}</h4>
              <div class="download-meta">
                <span class="download-date">
                  <svg class="meta-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" />
                  </svg>
                  {{ formatDate(download.created_at) }}
                </span>
                <span v-if="download.file_size" class="file-size">
                  <svg class="meta-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
                  </svg>
                  {{ formatFileSize(download.file_size) }}
                </span>
              </div>
              
              <!-- Progress Bar for downloading items -->
              <div v-if="download.status === 'downloading' && download.progress !== undefined" class="progress-container">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: `${download.progress}%` }"></div>
                </div>
                <span class="progress-text">{{ download.progress }}%</span>
              </div>
            </div>
            
            <div class="download-status">
              <span class="status-badge" :class="download.status">
                <svg v-if="download.status === 'completed'" class="status-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z" />
                </svg>
                <svg v-else-if="download.status === 'downloading'" class="status-icon loading-icon" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                    <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                    <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                  </circle>
                </svg>
                <svg v-else-if="download.status === 'failed'" class="status-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
                </svg>
                <svg v-else class="status-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17Z" />
                </svg>
                {{ getStatusText(download.status) }}
              </span>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="download-actions">
            <button 
              v-if="download.status === 'completed' && download.file_path"
              @click="handleOpenFile(download)"
              class="action-btn open-btn"
              title="Open File"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z" />
              </svg>
            </button>
            
            <button 
              v-if="download.status === 'downloading'"
              @click="handlePauseResume(download)"
              class="action-btn pause-btn"
              :title="download.paused ? 'Resume' : 'Pause'"
            >
              <svg v-if="download.paused" class="action-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8,5.14V19.14L19,12.14L8,5.14Z" />
              </svg>
              <svg v-else class="action-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M14,19H18V5H14M6,19H10V5H6V19Z" />
              </svg>
            </button>
            
            <button 
              v-if="download.status === 'failed'"
              @click="handleRetry(download)"
              class="action-btn retry-btn"
              title="Retry Download"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z" />
              </svg>
            </button>
            
            <button 
              @click="handleRemove(download)"
              class="action-btn remove-btn"
              title="Remove from List"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-else class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="currentColor">
          <path v-if="statusFilter === 'all'" d="M13,9H18.5L13,3.5V9M6,2H14L20,8V20A2,2 0 0,1 18,22H6C4.89,22 4,21.1 4,20V4C4,2.89 4.89,2 6,2Z" />
          <path v-else d="M12,2C13.1,2 14,2.9 14,4C14,5.1 13.1,6 12,6C10.9,6 10,5.1 10,4C10,2.9 10.9,2 12,2M21,9V7L15,1H5C3.89,1 3,1.89 3,3V19A2,2 0 0,0 5,21H11V19H5V3H13V9H21Z" />
        </svg>
        <h3>{{ getEmptyStateTitle() }}</h3>
        <p>{{ getEmptyStateDescription() }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { DownloadItem } from '@/types'

// Props
interface Props {
  downloads: DownloadItem[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

// Emits
interface Emits {
  refresh: []
  openFile: [download: DownloadItem]
  pauseResume: [download: DownloadItem]
  retry: [download: DownloadItem]
  remove: [download: DownloadItem]
  clearCompleted: []
}

const emit = defineEmits<Emits>()

// Reactive data
const statusFilter = ref<'all' | 'completed' | 'downloading' | 'failed' | 'pending'>('all')
const viewMode = ref<'list' | 'grid'>('list')

// Computed properties
const filteredDownloads = computed(() => {
  if (statusFilter.value === 'all') {
    return props.downloads
  }
  return props.downloads.filter(download => download.status === statusFilter.value)
})

const hasCompletedDownloads = computed(() => {
  return props.downloads.some(download => download.status === 'completed')
})

// Methods
const handleRefresh = () => {
  emit('refresh')
}

const handleOpenFile = (download: DownloadItem) => {
  emit('openFile', download)
}

const handlePauseResume = (download: DownloadItem) => {
  emit('pauseResume', download)
}

const handleRetry = (download: DownloadItem) => {
  emit('retry', download)
}

const handleRemove = (download: DownloadItem) => {
  emit('remove', download)
}

const handleClearCompleted = () => {
  emit('clearCompleted')
}

const formatDate = (dateString: string): string => {
  if (!dateString) return 'Unknown'
  try {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Unknown'
  }
}

const formatFileSize = (bytes: number): string => {
  if (!bytes) return 'Unknown'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    completed: 'Completed',
    downloading: 'Downloading',
    failed: 'Failed',
    pending: 'Pending',
    paused: 'Paused'
  }
  return statusMap[status] || status
}

const getEmptyStateTitle = (): string => {
  if (statusFilter.value === 'all') {
    return 'No download records'
  }
  return `No ${statusFilter.value} downloads`
}

const getEmptyStateDescription = (): string => {
  if (statusFilter.value === 'all') {
    return 'Your downloaded papers will appear here'
  }
  return `No downloads with ${statusFilter.value} status found`
}
</script>

<style scoped>
.downloads-section {
  margin-bottom: 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.8rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.section-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.downloads-count {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.section-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

.downloads-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

/* Header */
.downloads-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn,
.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover,
.clear-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.clear-btn {
  color: #dc2626;
  border-color: #fecaca;
}

.clear-btn:hover {
  background: #fef2f2;
  border-color: #fca5a5;
}

.action-icon {
  width: 1rem;
  height: 1rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-filter {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.view-btn {
  padding: 0.5rem;
  background: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn:hover {
  background: #f3f4f6;
}

.view-btn.active {
  background: #667eea;
  color: white;
}

.view-btn svg {
  width: 1rem;
  height: 1rem;
}

/* Downloads Container */
.downloads-container.view-list {
  display: flex;
  flex-direction: column;
}

.downloads-container.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.download-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  transition: all 0.2s ease;
}

.download-item:hover {
  background: #f9fafb;
}

.download-item:last-child {
  border-bottom: none;
}

.download-item.grid-item {
  flex-direction: column;
  align-items: stretch;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.download-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  gap: 1rem;
}

.grid-item .download-content {
  flex-direction: column;
  align-items: stretch;
}

.download-info {
  flex: 1;
}

.download-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.download-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.download-date,
.file-size {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.meta-icon {
  width: 0.875rem;
  height: 0.875rem;
}

/* Progress Bar */
.progress-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  font-weight: 500;
  color: #374151;
  min-width: 3rem;
  text-align: right;
}

/* Status Badge */
.status-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.downloading {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.failed {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-icon {
  width: 0.875rem;
  height: 0.875rem;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

/* Action Buttons */
.download-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.grid-item .download-actions {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.action-btn {
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: #f3f4f6;
}

.open-btn:hover {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.pause-btn:hover {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #f59e0b;
}

.retry-btn:hover {
  background: #ecfdf5;
  border-color: #10b981;
  color: #10b981;
}

.remove-btn:hover {
  background: #fef2f2;
  border-color: #ef4444;
  color: #ef4444;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #374151;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .downloads-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    justify-content: space-between;
  }
  
  .downloads-container.view-grid {
    grid-template-columns: 1fr;
  }
  
  .download-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .download-meta {
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .downloads-header {
    padding: 1rem;
  }
  
  .download-item {
    padding: 1rem;
  }
  
  .download-title {
    font-size: 0.9rem;
  }
  
  .download-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>