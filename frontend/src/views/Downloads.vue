<template>
  <div class="downloads-page">
    <!-- Download statistics cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-total"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ downloadStats.total }}</div>
              <div class="stat-label">Total Downloads</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-success"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ downloadStats.success }}</div>
              <div class="stat-label">Successful Downloads</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-downloading"><Loading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ downloadStats.downloading }}</div>
              <div class="stat-label">Downloading</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-failed"><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ downloadStats.failed }}</div>
              <div class="stat-label">Failed Downloads</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Toolbar -->
    <el-card class="toolbar-card" shadow="hover">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button-group>
            <el-button @click="refreshDownloads">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
            <el-button @click="clearCompleted">
              <el-icon><Delete /></el-icon>
              Clear Completed
            </el-button>
            <el-button @click="pauseAll">
              <el-icon><VideoPause /></el-icon>
              Pause All
            </el-button>
            <el-button @click="resumeAll">
              <el-icon><VideoPlay /></el-icon>
              Resume All
            </el-button>
          </el-button-group>
        </div>
        
        <div class="toolbar-right">
          <el-select v-model="filterStatus" placeholder="Filter Status" style="width: 120px; margin-right: 10px;">
            <el-option label="All" value="" />
            <el-option label="Downloading" value="downloading" />
            <el-option label="Completed" value="completed" />
            <el-option label="Paused" value="paused" />
            <el-option label="Failed" value="failed" />
          </el-select>
          
          <el-input
            v-model="searchKeyword"
            placeholder="Search paper title"
            style="width: 200px;"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>

    <!-- Download list -->
    <el-card class="downloads-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Download /></el-icon>
          <span>Download List ({{ filteredDownloads.length }})</span>
          <div class="header-actions">
            <el-button-group>
              <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
                <el-icon><List /></el-icon>
              </el-button>
              <el-button :type="viewMode === 'card' ? 'primary' : ''" @click="viewMode = 'card'">
                <el-icon><Grid /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <!-- List view -->
      <div v-if="viewMode === 'list'">
        <el-table :data="filteredDownloads" stripe style="width: 100%">
          <el-table-column label="Paper Info" min-width="300">
            <template #default="{ row }">
              <div class="paper-info">
                <div class="paper-title">{{ row.title }}</div>
                <div class="paper-meta">
                  <el-tag size="small" type="info">{{ row.arxivId }}</el-tag>
                  <span class="file-size">{{ formatFileSize(row.fileSize) }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Progress" width="200">
            <template #default="{ row }">
              <div class="progress-container">
                <el-progress
                  :percentage="row.progress"
                  :status="getProgressStatus(row.status)"
                  :stroke-width="8"
                />
                <span class="progress-text">{{ row.progress }}%</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Speed" width="100">
            <template #default="{ row }">
              <span v-if="row.status === 'downloading'" class="download-speed">
                {{ formatSpeed(row.speed) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="Start Time" width="150">
            <template #default="{ row }">
              {{ formatDateTime(row.startTime) }}
            </template>
          </el-table-column>
          
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button
                  v-if="row.status === 'downloading'"
                  size="small"
                  @click="pauseDownload(row)"
                >
                  <el-icon><VideoPause /></el-icon>
                </el-button>
                
                <el-button
                  v-if="row.status === 'paused' || row.status === 'failed'"
                  size="small"
                  type="primary"
                  @click="resumeDownload(row)"
                >
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
                
                <el-button
                  v-if="row.status === 'completed'"
                  size="small"
                  type="success"
                  @click="openFile(row)"
                >
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
                
                <el-button
                  size="small"
                  type="danger"
                  @click="removeDownload(row)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- Card view -->
      <div v-else class="card-view">
        <el-row :gutter="20">
          <el-col :span="8" v-for="download in filteredDownloads" :key="download.id">
            <el-card class="download-card" shadow="hover">
              <div class="download-header">
                <el-tag :type="getStatusType(download.status)" size="small">
                  {{ getStatusText(download.status) }}
                </el-tag>
                <span class="file-size">{{ formatFileSize(download.fileSize) }}</span>
              </div>
              
              <h3 class="download-title">{{ download.title }}</h3>
              
              <div class="download-meta">
                <el-tag size="small" type="info">{{ download.arxivId }}</el-tag>
                <span class="start-time">{{ formatDateTime(download.startTime) }}</span>
              </div>
              
              <div class="download-progress">
                <el-progress
                  :percentage="download.progress"
                  :status="getProgressStatus(download.status)"
                  :stroke-width="8"
                />
                <div class="progress-info">
                  <span>{{ download.progress }}%</span>
                  <span v-if="download.status === 'downloading'">
                    {{ formatSpeed(download.speed) }}
                  </span>
                </div>
              </div>
              
              <div class="download-actions">
                <el-button-group>
                  <el-button
                    v-if="download.status === 'downloading'"
                    size="small"
                    @click="pauseDownload(download)"
                  >
                    <el-icon><VideoPause /></el-icon>
                    Pause
                  </el-button>
                  
                  <el-button
                    v-if="download.status === 'paused' || download.status === 'failed'"
                    size="small"
                    type="primary"
                    @click="resumeDownload(download)"
                  >
                    <el-icon><VideoPlay /></el-icon>
                    Resume
                  </el-button>
                  
                  <el-button
                    v-if="download.status === 'completed'"
                    size="small"
                    type="success"
                    @click="openFile(download)"
                  >
                    <el-icon><FolderOpened /></el-icon>
                    Open
                  </el-button>
                  
                  <el-button
                    size="small"
                    type="danger"
                    @click="removeDownload(download)"
                  >
                    <el-icon><Delete /></el-icon>
                    Delete
                  </el-button>
                </el-button-group>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- Empty state -->
      <el-empty v-if="filteredDownloads.length === 0" description="No download tasks" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// State variables
const downloads = ref([])
const filterStatus = ref('')
const searchKeyword = ref('')
const viewMode = ref('list')
const refreshTimer = ref(null)

// Download statistics
const downloadStats = computed(() => {
  const stats = {
    total: downloads.value.length,
    success: 0,
    downloading: 0,
    failed: 0
  }
  
  downloads.value.forEach(download => {
    switch (download.status) {
      case 'completed':
        stats.success++
        break
      case 'downloading':
        stats.downloading++
        break
      case 'failed':
        stats.failed++
        break
    }
  })
  
  return stats
})

// Filtered download list
const filteredDownloads = computed(() => {
  let filtered = downloads.value
  
  // Status filtering
  if (filterStatus.value) {
    filtered = filtered.filter(download => download.status === filterStatus.value)
  }
  
  // Keyword search
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(download => 
      download.title.toLowerCase().includes(keyword) ||
      download.arxivId.toLowerCase().includes(keyword)
    )
  }
  
  return filtered
})

// Get status type
const getStatusType = (status) => {
  const typeMap = {
    'downloading': 'primary',
    'completed': 'success',
    'paused': 'warning',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

// Get status text
const getStatusText = (status) => {
  const textMap = {
    'downloading': 'Downloading',
    'completed': 'Completed',
    'paused': 'Paused',
    'failed': 'Failed'
  }
  return textMap[status] || 'Unknown'
}

// Get progress bar status
const getProgressStatus = (status) => {
  const statusMap = {
    'downloading': '',
    'completed': 'success',
    'paused': 'warning',
    'failed': 'exception'
  }
  return statusMap[status] || ''
}

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format download speed
const formatSpeed = (bytesPerSecond) => {
  return formatFileSize(bytesPerSecond) + '/s'
}

// Format date time
const formatDateTime = (datetime) => {
  return dayjs(datetime).format('MM-DD HH:mm')
}

// Refresh download list
const refreshDownloads = async () => {
  try {
    // Mock API call
    downloads.value = generateMockDownloads()
    ElMessage.success('Refresh successful')
  } catch (error) {
    ElMessage.error('Refresh failed')
  }
}

// Generate mock download data
const generateMockDownloads = () => {
  const statuses = ['downloading', 'completed', 'paused', 'failed']
  const mockDownloads = []
  
  for (let i = 1; i <= 15; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const progress = status === 'completed' ? 100 : 
                    status === 'failed' ? Math.floor(Math.random() * 50) :
                    Math.floor(Math.random() * 90) + 10
    
    mockDownloads.push({
      id: i,
      title: `Attention Is All You Need: A Comprehensive Study ${i}`,
      arxivId: `2024.0001${i.toString().padStart(2, '0')}`,
      status: status,
      progress: progress,
      fileSize: Math.floor(Math.random() * 10000000) + 1000000, // 1-10MB
      speed: status === 'downloading' ? Math.floor(Math.random() * 1000000) + 100000 : 0,
      startTime: dayjs().subtract(Math.floor(Math.random() * 24), 'hour').toISOString(),
      filePath: `/downloads/paper_${i}.pdf`
    })
  }
  
  return mockDownloads
}

// Pause download
const pauseDownload = async (download) => {
  try {
    download.status = 'paused'
    ElMessage.success(`Paused: ${download.title}`)
  } catch (error) {
    ElMessage.error('Pause failed')
  }
}

// Resume download
const resumeDownload = async (download) => {
  try {
    download.status = 'downloading'
    ElMessage.success(`Resumed: ${download.title}`)
  } catch (error) {
    ElMessage.error('Resume failed')
  }
}

// Remove download
const removeDownload = async (download) => {
  try {
    const result = await ElMessageBox.confirm(
      `Are you sure you want to delete download task "${download.title}"?`,
      'Delete Confirmation',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      const index = downloads.value.findIndex(d => d.id === download.id)
      if (index > -1) {
        downloads.value.splice(index, 1)
        ElMessage.success('Delete successful')
      }
    }
  } catch (error) {
    // User cancelled
  }
}

// Open file
const openFile = (download) => {
  ElMessage.success(`Open file: ${download.filePath}`)
  // Should call system API to open file here
}

// Clear completed downloads
const clearCompleted = async () => {
  try {
    const completedCount = downloads.value.filter(d => d.status === 'completed').length
    if (completedCount === 0) {
      ElMessage.info('No completed download tasks')
      return
    }
    
    const result = await ElMessageBox.confirm(
      `Are you sure you want to clear ${completedCount} completed download tasks?`,
      'Clear Confirmation',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      downloads.value = downloads.value.filter(d => d.status !== 'completed')
      ElMessage.success(`Cleared ${completedCount} completed tasks`)
    }
  } catch (error) {
    // User cancelled
  }
}

// Pause all
const pauseAll = () => {
  const downloadingTasks = downloads.value.filter(d => d.status === 'downloading')
  downloadingTasks.forEach(task => {
    task.status = 'paused'
  })
  ElMessage.success(`Paused ${downloadingTasks.length} download tasks`)
}

// Resume all
const resumeAll = () => {
  const pausedTasks = downloads.value.filter(d => d.status === 'paused')
  pausedTasks.forEach(task => {
    task.status = 'downloading'
  })
  ElMessage.success(`Resumed ${pausedTasks.length} download tasks`)
}

// Mock progress update
const updateProgress = () => {
  downloads.value.forEach(download => {
    if (download.status === 'downloading' && download.progress < 100) {
      download.progress = Math.min(100, download.progress + Math.floor(Math.random() * 5) + 1)
      if (download.progress === 100) {
        download.status = 'completed'
        download.speed = 0
      }
    }
  })
}

onMounted(() => {
  refreshDownloads()
  
  // Timer for progress update
  refreshTimer.value = setInterval(updateProgress, 2000)
})

onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
})
</script>

<style scoped>
.downloads-page {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 32px;
  margin-right: 15px;
}

.icon-total { color: #409EFF; }
.icon-success { color: #67C23A; }
.icon-downloading { color: #E6A23C; }
.icon-failed { color: #F56C6C; }

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.toolbar-card {
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.downloads-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header span {
  margin-left: 8px;
  font-weight: bold;
}

.paper-info {
  line-height: 1.5;
}

.paper-title {
  font-weight: 500;
  margin-bottom: 5px;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-size {
  color: #909399;
  font-size: 12px;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 35px;
}

.download-speed {
  color: #67C23A;
  font-size: 12px;
}

.card-view {
  margin-bottom: 20px;
}

.download-card {
  margin-bottom: 20px;
  height: 280px;
}

.download-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.download-title {
  margin: 10px 0;
  font-size: 16px;
  line-height: 1.4;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.download-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.start-time {
  color: #909399;
  font-size: 12px;
}

.download-progress {
  margin-bottom: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
}

.download-actions {
  display: flex;
  justify-content: center;
}

/* Dark theme adaptation */
:global(.dark) .stat-number {
  color: #e5eaf3;
}

:global(.dark) .paper-title {
  color: #e5eaf3;
}

:global(.dark) .download-title {
  color: #e5eaf3;
}
</style>