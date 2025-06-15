<template>
  <div class="downloads-page">
    <!-- 下载统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-total"><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ downloadStats.total }}</div>
              <div class="stat-label">总下载数</div>
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
              <div class="stat-label">成功下载</div>
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
              <div class="stat-label">下载中</div>
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
              <div class="stat-label">下载失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作工具栏 -->
    <el-card class="toolbar-card" shadow="hover">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button-group>
            <el-button @click="refreshDownloads">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button @click="clearCompleted">
              <el-icon><Delete /></el-icon>
              清除已完成
            </el-button>
            <el-button @click="pauseAll">
              <el-icon><VideoPause /></el-icon>
              暂停全部
            </el-button>
            <el-button @click="resumeAll">
              <el-icon><VideoPlay /></el-icon>
              恢复全部
            </el-button>
          </el-button-group>
        </div>
        
        <div class="toolbar-right">
          <el-select v-model="filterStatus" placeholder="筛选状态" style="width: 120px; margin-right: 10px;">
            <el-option label="全部" value="" />
            <el-option label="下载中" value="downloading" />
            <el-option label="已完成" value="completed" />
            <el-option label="已暂停" value="paused" />
            <el-option label="失败" value="failed" />
          </el-select>
          
          <el-input
            v-model="searchKeyword"
            placeholder="搜索论文标题"
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

    <!-- 下载列表 -->
    <el-card class="downloads-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Download /></el-icon>
          <span>下载列表 ({{ filteredDownloads.length }})</span>
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
      
      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'">
        <el-table :data="filteredDownloads" stripe style="width: 100%">
          <el-table-column label="论文信息" min-width="300">
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
          
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="进度" width="200">
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
          
          <el-table-column label="速度" width="100">
            <template #default="{ row }">
              <span v-if="row.status === 'downloading'" class="download-speed">
                {{ formatSpeed(row.speed) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="开始时间" width="150">
            <template #default="{ row }">
              {{ formatDateTime(row.startTime) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
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
      
      <!-- 卡片视图 -->
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
                    暂停
                  </el-button>
                  
                  <el-button
                    v-if="download.status === 'paused' || download.status === 'failed'"
                    size="small"
                    type="primary"
                    @click="resumeDownload(download)"
                  >
                    <el-icon><VideoPlay /></el-icon>
                    恢复
                  </el-button>
                  
                  <el-button
                    v-if="download.status === 'completed'"
                    size="small"
                    type="success"
                    @click="openFile(download)"
                  >
                    <el-icon><FolderOpened /></el-icon>
                    打开
                  </el-button>
                  
                  <el-button
                    size="small"
                    type="danger"
                    @click="removeDownload(download)"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </el-button-group>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 空状态 -->
      <el-empty v-if="filteredDownloads.length === 0" description="暂无下载任务" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 状态变量
const downloads = ref([])
const filterStatus = ref('')
const searchKeyword = ref('')
const viewMode = ref('list')
const refreshTimer = ref(null)

// 下载统计
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

// 过滤后的下载列表
const filteredDownloads = computed(() => {
  let filtered = downloads.value
  
  // 状态筛选
  if (filterStatus.value) {
    filtered = filtered.filter(download => download.status === filterStatus.value)
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(download => 
      download.title.toLowerCase().includes(keyword) ||
      download.arxivId.toLowerCase().includes(keyword)
    )
  }
  
  return filtered
})

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'downloading': 'primary',
    'completed': 'success',
    'paused': 'warning',
    'failed': 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'downloading': '下载中',
    'completed': '已完成',
    'paused': '已暂停',
    'failed': '失败'
  }
  return textMap[status] || '未知'
}

// 获取进度条状态
const getProgressStatus = (status) => {
  const statusMap = {
    'downloading': '',
    'completed': 'success',
    'paused': 'warning',
    'failed': 'exception'
  }
  return statusMap[status] || ''
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化下载速度
const formatSpeed = (bytesPerSecond) => {
  return formatFileSize(bytesPerSecond) + '/s'
}

// 格式化日期时间
const formatDateTime = (datetime) => {
  return dayjs(datetime).format('MM-DD HH:mm')
}

// 刷新下载列表
const refreshDownloads = async () => {
  try {
    // 模拟API调用
    downloads.value = generateMockDownloads()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

// 生成模拟下载数据
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

// 暂停下载
const pauseDownload = async (download) => {
  try {
    download.status = 'paused'
    ElMessage.success(`已暂停: ${download.title}`)
  } catch (error) {
    ElMessage.error('暂停失败')
  }
}

// 恢复下载
const resumeDownload = async (download) => {
  try {
    download.status = 'downloading'
    ElMessage.success(`已恢复: ${download.title}`)
  } catch (error) {
    ElMessage.error('恢复失败')
  }
}

// 删除下载
const removeDownload = async (download) => {
  try {
    const result = await ElMessageBox.confirm(
      `确定要删除下载任务 "${download.title}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      const index = downloads.value.findIndex(d => d.id === download.id)
      if (index > -1) {
        downloads.value.splice(index, 1)
        ElMessage.success('删除成功')
      }
    }
  } catch (error) {
    // 用户取消
  }
}

// 打开文件
const openFile = (download) => {
  ElMessage.success(`打开文件: ${download.filePath}`)
  // 这里应该调用系统API打开文件
}

// 清除已完成的下载
const clearCompleted = async () => {
  try {
    const completedCount = downloads.value.filter(d => d.status === 'completed').length
    if (completedCount === 0) {
      ElMessage.info('没有已完成的下载任务')
      return
    }
    
    const result = await ElMessageBox.confirm(
      `确定要清除 ${completedCount} 个已完成的下载任务吗？`,
      '清除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      downloads.value = downloads.value.filter(d => d.status !== 'completed')
      ElMessage.success(`已清除 ${completedCount} 个已完成的任务`)
    }
  } catch (error) {
    // 用户取消
  }
}

// 暂停全部
const pauseAll = () => {
  const downloadingTasks = downloads.value.filter(d => d.status === 'downloading')
  downloadingTasks.forEach(task => {
    task.status = 'paused'
  })
  ElMessage.success(`已暂停 ${downloadingTasks.length} 个下载任务`)
}

// 恢复全部
const resumeAll = () => {
  const pausedTasks = downloads.value.filter(d => d.status === 'paused')
  pausedTasks.forEach(task => {
    task.status = 'downloading'
  })
  ElMessage.success(`已恢复 ${pausedTasks.length} 个下载任务`)
}

// 模拟进度更新
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
  
  // 定时更新进度
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

/* 暗色主题适配 */
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