<template>
  <div class="home">
    <!-- 欢迎横幅 -->
    <el-card class="welcome-card" shadow="hover">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎使用 ArXiv 论文下载器</h1>
          <p>智能搜索、批量下载、高效管理学术论文的专业工具</p>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/search')">
              <el-icon><Search /></el-icon>
              开始搜索
            </el-button>
            <el-button size="large" @click="$router.push('/downloads')">
              <el-icon><Download /></el-icon>
              查看下载
            </el-button>
          </div>
        </div>
        <div class="welcome-image">
          <el-icon class="large-icon"><Document /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon class="icon-search"><Search /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalSearches }}</div>
              <div class="stat-label">总搜索次数</div>
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
              <div class="stat-label">已下载论文</div>
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
              <div class="stat-label">成功率</div>
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
              <div class="stat-label">存储空间</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能特性 -->
    <el-row :gutter="20" class="features-row">
      <el-col :span="12">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>核心功能</span>
            </div>
          </template>
          <ul class="feature-list">
            <li><el-icon><Check /></el-icon> 智能搜索与过滤</li>
            <li><el-icon><Check /></el-icon> 批量下载管理</li>
            <li><el-icon><Check /></el-icon> 自动文件命名</li>
            <li><el-icon><Check /></el-icon> 下载进度跟踪</li>
            <li><el-icon><Check /></el-icon> 错误重试机制</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Lightning /></el-icon>
              <span>高级特性</span>
            </div>
          </template>
          <ul class="feature-list">
            <li><el-icon><Check /></el-icon> 异步并发下载</li>
            <li><el-icon><Check /></el-icon> 智能缓存系统</li>
            <li><el-icon><Check /></el-icon> 插件扩展支持</li>
            <li><el-icon><Check /></el-icon> 详细统计分析</li>
            <li><el-icon><Check /></el-icon> 多格式导出</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card class="recent-activity" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>最近活动</span>
          <el-button text @click="loadRecentActivity">
            <el-icon><Refresh /></el-icon>
            刷新
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
      
      <el-empty v-else description="暂无最近活动" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 统计数据
const stats = ref({
  totalSearches: 0,
  totalDownloads: 0,
  successRate: 0,
  totalSize: 0
})

// 最近活动
const recentActivity = ref([])

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 模拟API调用
    stats.value = {
      totalSearches: 156,
      totalDownloads: 89,
      successRate: 94,
      totalSize: 2147483648 // 2GB
    }
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

// 加载最近活动
const loadRecentActivity = async () => {
  try {
    // 模拟API调用
    recentActivity.value = [
      {
        timestamp: '2024-01-15 14:30',
        type: 'success',
        description: '成功下载论文: "Attention Is All You Need"'
      },
      {
        timestamp: '2024-01-15 14:25',
        type: 'primary',
        description: '开始搜索关键词: "transformer neural network"'
      },
      {
        timestamp: '2024-01-15 14:20',
        type: 'success',
        description: '批量下载完成，共下载 5 篇论文'
      },
      {
        timestamp: '2024-01-15 14:15',
        type: 'warning',
        description: '下载重试: "BERT: Pre-training of Deep Bidirectional Transformers"'
      }
    ]
  } catch (error) {
    ElMessage.error('加载最近活动失败')
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

/* 暗色主题适配 */
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