<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <el-card class="title-card" shadow="hover">
      <div class="title-header">
        <el-icon><Setting /></el-icon>
        <span class="title">系统设置</span>
        <div class="title-actions">
          <el-button @click="resetToDefaults" type="warning">
            <el-icon><RefreshLeft /></el-icon>
            恢复默认
          </el-button>
          <el-button @click="saveSettings" type="primary">
            <el-icon><Check /></el-icon>
            保存设置
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧设置面板 -->
      <el-col :span="18">
        <!-- 下载设置 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>下载设置</span>
            </div>
          </template>
          
          <el-form :model="downloadSettings" label-width="140px" label-position="left">
            <el-form-item label="默认下载目录">
              <el-input
                v-model="downloadSettings.downloadDir"
                placeholder="请选择下载目录"
                readonly
              >
                <template #append>
                  <el-button @click="selectDownloadDir">
                    <el-icon><FolderOpened /></el-icon>
                    选择
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="最大并发下载数">
              <el-slider
                v-model="downloadSettings.maxConcurrent"
                :min="1"
                :max="10"
                :step="1"
                show-stops
                show-input
                style="width: 300px;"
              />
            </el-form-item>
            
            <el-form-item label="下载重试次数">
              <el-input-number
                v-model="downloadSettings.retryCount"
                :min="0"
                :max="10"
                :step="1"
                style="width: 150px;"
              />
            </el-form-item>
            
            <el-form-item label="连接超时时间">
              <el-input-number
                v-model="downloadSettings.timeout"
                :min="5"
                :max="300"
                :step="5"
                style="width: 150px;"
              />
              <span style="margin-left: 10px; color: #909399;">秒</span>
            </el-form-item>
            
            <el-form-item label="自动重命名">
              <el-switch
                v-model="downloadSettings.autoRename"
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="setting-description">
                当文件名冲突时自动添加序号
              </div>
            </el-form-item>
            
            <el-form-item label="下载完成提醒">
              <el-switch
                v-model="downloadSettings.notification"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 搜索设置 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>搜索设置</span>
            </div>
          </template>
          
          <el-form :model="searchSettings" label-width="140px" label-position="left">
            <el-form-item label="默认搜索结果数">
              <el-input-number
                v-model="searchSettings.defaultMaxResults"
                :min="1"
                :max="1000"
                :step="10"
                style="width: 150px;"
              />
            </el-form-item>
            
            <el-form-item label="默认排序方式">
              <el-select v-model="searchSettings.defaultSortBy" style="width: 200px;">
                <el-option label="相关性" value="relevance" />
                <el-option label="提交日期" value="submittedDate" />
                <el-option label="最后更新" value="lastUpdatedDate" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="默认学科分类">
              <el-select
                v-model="searchSettings.defaultCategories"
                multiple
                placeholder="请选择默认学科分类"
                style="width: 300px;"
              >
                <el-option label="计算机科学" value="cs" />
                <el-option label="数学" value="math" />
                <el-option label="物理" value="physics" />
                <el-option label="统计学" value="stat" />
                <el-option label="生物学" value="q-bio" />
                <el-option label="经济学" value="econ" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="搜索历史保存">
              <el-switch
                v-model="searchSettings.saveHistory"
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="setting-description">
                保存搜索关键词历史记录
              </div>
            </el-form-item>
            
            <el-form-item label="自动补全">
              <el-switch
                v-model="searchSettings.autoComplete"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 界面设置 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>界面设置</span>
            </div>
          </template>
          
          <el-form :model="uiSettings" label-width="140px" label-position="left">
            <el-form-item label="主题模式">
              <el-radio-group v-model="uiSettings.theme">
                <el-radio label="light">浅色主题</el-radio>
                <el-radio label="dark">深色主题</el-radio>
                <el-radio label="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="uiSettings.language" style="width: 150px;">
                <el-option label="中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="列表显示模式">
              <el-radio-group v-model="uiSettings.listViewMode">
                <el-radio label="list">列表模式</el-radio>
                <el-radio label="grid">网格模式</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="每页显示数量">
              <el-select v-model="uiSettings.pageSize" style="width: 150px;">
                <el-option label="10" :value="10" />
                <el-option label="20" :value="20" />
                <el-option label="50" :value="50" />
                <el-option label="100" :value="100" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="显示缩略图">
              <el-switch
                v-model="uiSettings.showThumbnails"
                active-text="显示"
                inactive-text="隐藏"
              />
            </el-form-item>
            
            <el-form-item label="紧凑模式">
              <el-switch
                v-model="uiSettings.compactMode"
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="setting-description">
                减少界面元素间距，显示更多内容
              </div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 高级设置 -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>高级设置</span>
            </div>
          </template>
          
          <el-form :model="advancedSettings" label-width="140px" label-position="left">
            <el-form-item label="API 端点">
              <el-input
                v-model="advancedSettings.apiEndpoint"
                placeholder="http://export.arxiv.org/api/query"
              />
            </el-form-item>
            
            <el-form-item label="代理设置">
              <el-input
                v-model="advancedSettings.proxyUrl"
                placeholder="http://proxy.example.com:8080"
              >
                <template #prepend>
                  <el-switch v-model="advancedSettings.useProxy" />
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="用户代理">
              <el-input
                v-model="advancedSettings.userAgent"
                placeholder="ArxivDownloader/1.0"
              />
            </el-form-item>
            
            <el-form-item label="缓存设置">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-switch
                    v-model="advancedSettings.enableCache"
                    active-text="启用缓存"
                    inactive-text="禁用缓存"
                  />
                </el-col>
                <el-col :span="12">
                  <el-button @click="clearCache" :disabled="!advancedSettings.enableCache">
                    <el-icon><Delete /></el-icon>
                    清除缓存
                  </el-button>
                </el-col>
              </el-row>
            </el-form-item>
            
            <el-form-item label="日志级别">
              <el-select v-model="advancedSettings.logLevel" style="width: 150px;">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="开发者模式">
              <el-switch
                v-model="advancedSettings.developerMode"
                active-text="启用"
                inactive-text="禁用"
              />
              <div class="setting-description">
                显示调试信息和额外的开发工具
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧信息面板 -->
      <el-col :span="6">
        <!-- 系统信息 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          
          <div class="info-item">
            <span class="info-label">版本号:</span>
            <span class="info-value">v1.2.3</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">构建日期:</span>
            <span class="info-value">2024-01-15</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Python版本:</span>
            <span class="info-value">3.9.7</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">缓存大小:</span>
            <span class="info-value">{{ formatFileSize(cacheSize) }}</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">下载目录:</span>
            <span class="info-value">{{ formatPath(downloadSettings.downloadDir) }}</span>
          </div>
        </el-card>

        <!-- 快捷操作 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>快捷操作</span>
            </div>
          </template>
          
          <div class="quick-actions">
            <el-button @click="openDownloadDir" style="width: 100%; margin-bottom: 10px;">
              <el-icon><FolderOpened /></el-icon>
              打开下载目录
            </el-button>
            
            <el-button @click="exportSettings" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Upload /></el-icon>
              导出设置
            </el-button>
            
            <el-button @click="importSettings" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Download /></el-icon>
              导入设置
            </el-button>
            
            <el-button @click="checkUpdates" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Refresh /></el-icon>
              检查更新
            </el-button>
            
            <el-button @click="showAbout" style="width: 100%;">
              <el-icon><QuestionFilled /></el-icon>
              关于软件
            </el-button>
          </div>
        </el-card>

        <!-- 使用统计 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>使用统计</span>
            </div>
          </template>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.totalSearches }}</div>
            <div class="stats-label">总搜索次数</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.totalDownloads }}</div>
            <div class="stats-label">总下载次数</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ formatFileSize(usageStats.totalSize) }}</div>
            <div class="stats-label">累计下载大小</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.daysUsed }}</div>
            <div class="stats-label">使用天数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 关于对话框 -->
    <el-dialog v-model="aboutDialogVisible" title="关于 ArXiv 论文下载器" width="500px">
      <div class="about-content">
        <div class="about-logo">
          <el-icon size="60"><Document /></el-icon>
        </div>
        
        <h3>ArXiv 论文下载器</h3>
        <p>版本: v1.2.3</p>
        <p>一个功能强大的 ArXiv 论文搜索和下载工具</p>
        
        <div class="about-features">
          <h4>主要功能:</h4>
          <ul>
            <li>智能论文搜索</li>
            <li>批量下载管理</li>
            <li>多格式支持</li>
            <li>下载统计分析</li>
          </ul>
        </div>
        
        <div class="about-links">
          <el-button link>GitHub 仓库</el-button>
          <el-button link>使用文档</el-button>
          <el-button link>问题反馈</el-button>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="aboutDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 对话框状态
const aboutDialogVisible = ref(false)

// 下载设置
const downloadSettings = reactive({
  downloadDir: '/Users/username/Downloads/arxiv_papers',
  maxConcurrent: 3,
  retryCount: 3,
  timeout: 30,
  autoRename: true,
  notification: true
})

// 搜索设置
const searchSettings = reactive({
  defaultMaxResults: 50,
  defaultSortBy: 'relevance',
  defaultCategories: ['cs'],
  saveHistory: true,
  autoComplete: true
})

// 界面设置
const uiSettings = reactive({
  theme: 'light',
  language: 'zh-CN',
  listViewMode: 'list',
  pageSize: 20,
  showThumbnails: true,
  compactMode: false
})

// 高级设置
const advancedSettings = reactive({
  apiEndpoint: 'http://export.arxiv.org/api/query',
  useProxy: false,
  proxyUrl: '',
  userAgent: 'ArxivDownloader/1.0',
  enableCache: true,
  logLevel: 'info',
  developerMode: false
})

// 系统信息
const cacheSize = ref(52428800) // 50MB

// 使用统计
const usageStats = reactive({
  totalSearches: 1234,
  totalDownloads: 567,
  totalSize: 15728640000, // 15GB
  daysUsed: 45
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化路径
const formatPath = (path) => {
  if (path.length > 30) {
    return '...' + path.slice(-27)
  }
  return path
}

// 选择下载目录
const selectDownloadDir = () => {
  ElMessage.info('文件选择器功能需要后端支持')
}

// 保存设置
const saveSettings = async () => {
  try {
    // 这里应该调用 API 保存设置
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('设置已保存')
  } catch (error) {
    ElMessage.error('保存设置失败')
  }
}

// 恢复默认设置
const resetToDefaults = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要恢复所有设置到默认值吗？此操作不可撤销。',
      '确认恢复默认设置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置所有设置到默认值
    Object.assign(downloadSettings, {
      downloadDir: '/Users/username/Downloads/arxiv_papers',
      maxConcurrent: 3,
      retryCount: 3,
      timeout: 30,
      autoRename: true,
      notification: true
    })
    
    Object.assign(searchSettings, {
      defaultMaxResults: 50,
      defaultSortBy: 'relevance',
      defaultCategories: ['cs'],
      saveHistory: true,
      autoComplete: true
    })
    
    Object.assign(uiSettings, {
      theme: 'light',
      language: 'zh-CN',
      listViewMode: 'list',
      pageSize: 20,
      showThumbnails: true,
      compactMode: false
    })
    
    Object.assign(advancedSettings, {
      apiEndpoint: 'http://export.arxiv.org/api/query',
      useProxy: false,
      proxyUrl: '',
      userAgent: 'ArxivDownloader/1.0',
      enableCache: true,
      logLevel: 'info',
      developerMode: false
    })
    
    ElMessage.success('已恢复默认设置')
  } catch {
    // 用户取消操作
  }
}

// 清除缓存
const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有缓存数据吗？',
      '确认清除缓存',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用 API 清除缓存
    await new Promise(resolve => setTimeout(resolve, 1000))
    cacheSize.value = 0
    ElMessage.success('缓存已清除')
  } catch {
    // 用户取消操作
  }
}

// 打开下载目录
const openDownloadDir = () => {
  ElMessage.info('打开文件夹功能需要后端支持')
}

// 导出设置
const exportSettings = () => {
  const settings = {
    download: downloadSettings,
    search: searchSettings,
    ui: uiSettings,
    advanced: advancedSettings
  }
  
  const dataStr = JSON.stringify(settings, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = 'arxiv_downloader_settings.json'
  link.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('设置已导出')
}

// 导入设置
const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  
  input.onchange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const settings = JSON.parse(e.target.result)
        
        if (settings.download) Object.assign(downloadSettings, settings.download)
        if (settings.search) Object.assign(searchSettings, settings.search)
        if (settings.ui) Object.assign(uiSettings, settings.ui)
        if (settings.advanced) Object.assign(advancedSettings, settings.advanced)
        
        ElMessage.success('设置已导入')
      } catch (error) {
        ElMessage.error('导入设置失败：文件格式错误')
      }
    }
    
    reader.readAsText(file)
  }
  
  input.click()
}

// 检查更新
const checkUpdates = async () => {
  try {
    ElMessage.info('正在检查更新...')
    // 模拟检查更新
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('当前已是最新版本')
  } catch (error) {
    ElMessage.error('检查更新失败')
  }
}

// 显示关于对话框
const showAbout = () => {
  aboutDialogVisible.value = true
}

onMounted(() => {
  // 加载设置
  console.log('设置页面已加载')
})
</script>

<style scoped>
.settings-page {
  max-width: 1400px;
  margin: 0 auto;
}

.title-card {
  margin-bottom: 20px;
}

.title-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-header .title {
  margin-left: 8px;
  font-size: 20px;
  font-weight: bold;
  flex: 1;
}

.title-actions {
  display: flex;
  gap: 10px;
}

.settings-card {
  margin-bottom: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-header span {
  margin-left: 8px;
  font-weight: bold;
}

.setting-description {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  color: #606266;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.quick-actions {
  display: flex;
  flex-direction: column;
}

.stats-item {
  text-align: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stats-item:last-child {
  border-bottom: none;
}

.stats-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stats-label {
  font-size: 12px;
  color: #909399;
}

.about-content {
  text-align: center;
}

.about-logo {
  margin-bottom: 20px;
  color: #409EFF;
}

.about-content h3 {
  margin: 10px 0;
  color: #303133;
}

.about-content p {
  margin: 5px 0;
  color: #606266;
}

.about-features {
  text-align: left;
  margin: 20px 0;
}

.about-features h4 {
  margin-bottom: 10px;
  color: #303133;
}

.about-features ul {
  margin: 0;
  padding-left: 20px;
}

.about-features li {
  margin: 5px 0;
  color: #606266;
}

.about-links {
  margin-top: 20px;
}

.about-links .el-button {
  margin: 0 5px;
}

/* 暗色主题适配 */
:global(.dark) .title-header .title {
  color: #e5eaf3;
}

:global(.dark) .info-item {
  border-bottom-color: #414243;
}

:global(.dark) .stats-item {
  border-bottom-color: #414243;
}

:global(.dark) .info-value,
:global(.dark) .about-content h3 {
  color: #e5eaf3;
}
</style>