<template>
  <div class="home">
    <!-- Welcome area -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>Welcome to ArXiv Paper Downloader</h1>
        <p>Professional tool for intelligent search, batch download, and efficient management of academic papers</p>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/search')">
              <el-icon><Search /></el-icon>
              Start Search
            </el-button>
            <el-button size="large" @click="$router.push('/downloads')">
              <el-icon><Download /></el-icon>
              View Downloads
            </el-button>
          </div>
        </div>
        <div class="welcome-image">
          <el-icon class="large-icon"><Document /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- Statistics cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-search"><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalSearches }}</div>
              <div class="stat-label">Total Searches</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-download"><Download /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalDownloads }}</div>
              <div class="stat-label">Downloaded Papers</div>
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
              <div class="stat-number">{{ stats.successRate }}%</div>
              <div class="stat-label">Success Rate</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-storage"><FolderOpened /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ formatFileSize(stats.totalSize) }}</div>
              <div class="stat-label">Storage Space</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Core features -->
    <el-row :gutter="20" class="features-row">
      <el-col :span="12">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>Core Features</span>
            </div>
          </template>
          <ul class="feature-list">
            <li><el-icon><Check /></el-icon> Intelligent Search & Filtering</li>
            <li><el-icon><Check /></el-icon> Batch Download Management</li>
            <li><el-icon><Check /></el-icon> Automatic File Naming</li>
            <li><el-icon><Check /></el-icon> Download Progress Tracking</li>
            <li><el-icon><Check /></el-icon> Error Retry Mechanism</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Lightning /></el-icon>
              <span>Advanced Features</span>
            </div>
          </template>
          <ul class="feature-list">
            <li><el-icon><Check /></el-icon> Asynchronous Concurrent Download</li>
            <li><el-icon><Check /></el-icon> Intelligent Cache System</li>
            <li><el-icon><Check /></el-icon> Plugin Extension Support</li>
            <li><el-icon><Check /></el-icon> Detailed Statistical Analysis</li>
            <li><el-icon><Check /></el-icon> Multi-format Export</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent activity -->
    <el-card class="recent-activity" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>Recent Activity</span>
          <el-button text @click="loadRecentActivity">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      
      <el-timeline v-if="recentActivity.length > 0">
        <el-timeline-item
          v-for="(activity, index) in recentActivity"
          :key="index"
          :timestamp="activity.timestamp"
          :type="activity.type"
        >
          {{ activity.description }}
        </el-timeline-item>
      </el-timeline>
      
      <el-empty v-else description="No recent activity" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Reactive data
const stats = ref({
  totalSearches: 0,
  totalDownloads: 0,
  successRate: 0,
  totalSize: 0
})

// Recent activity data
const recentActivity = ref([])

// Methods
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Load data
const loadStats = async () => {
  try {
    // Simulate API call
    stats.value = {
      totalSearches: 156,
      totalDownloads: 89,
      successRate: 94,
      totalSize: 2147483648 // 2GB
    }
  } catch (error) {
    ElMessage.error('Failed to load statistics data')
  }
}

// Load recent activity
const loadRecentActivity = async () => {
  try {
    // Simulate API call
    recentActivity.value = [
      {
        timestamp: '2024-01-15 14:30',
        type: 'success',
        description: 'Successfully downloaded paper: "Attention Is All You Need"'
      },
      {
        timestamp: '2024-01-15 14:25',
        type: 'primary',
        description: 'Started searching for keyword: "transformer neural network"'
      },
      {
        timestamp: '2024-01-15 14:20',
        type: 'success',
        description: 'Batch download completed, downloaded 5 papers in total'
      },
      {
        timestamp: '2024-01-15 14:15',
        type: 'warning',
        description: 'Download retry: "BERT: Pre-training of Deep Bidirectional Transformers"'
      }
    ]
  } catch (error) {
    ElMessage.error('Failed to load recent activities')
  }
}

onMounted(() => {
  loadStats()
  loadRecentActivity()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.welcome-text h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
}

.welcome-text p {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  gap: 15px;
}

.welcome-image {
  flex-shrink: 0;
}

.large-icon {
  font-size: 120px;
  color: #409EFF;
  opacity: 0.8;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 40px;
  margin-right: 15px;
}

.icon-search { color: #409EFF; }
.icon-download { color: #67C23A; }
.icon-success { color: #E6A23C; }
.icon-storage { color: #F56C6C; }

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.features-row {
  margin-bottom: 20px;
}

.feature-card {
  height: 280px;
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

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  display: flex;
  align-items: center;
  padding: 8px 0;
  color: #606266;
}

.feature-list li .el-icon {
  margin-right: 8px;
  color: #67C23A;
}

.recent-activity {
  margin-bottom: 20px;
}

/* Dark theme adaptation */
:global(.dark) .welcome-text h1 {
  color: #e5eaf3;
}

:global(.dark) .welcome-text p {
  color: #a3a6ad;
}

:global(.dark) .stat-number {
  color: #e5eaf3;
}

:global(.dark) .feature-list li {
  color: #a3a6ad;
}
</style>