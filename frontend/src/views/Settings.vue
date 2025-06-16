<template>
  <div class="settings-page">
    <!-- Page title -->
    <el-card class="title-card" shadow="hover">
      <div class="title-header">
        <el-icon><Setting /></el-icon>
        <span class="title">System Settings</span>
        <div class="title-actions">
          <el-button @click="resetToDefaults" type="warning">
            <el-icon><RefreshLeft /></el-icon>
            Reset to Default
          </el-button>
          <el-button @click="saveSettings" type="primary">
            <el-icon><Check /></el-icon>
            Save Settings
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- Left settings panel -->
      <el-col :span="18">
        <!-- Download settings -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>Download Settings</span>
            </div>
          </template>
          
          <el-form :model="downloadSettings" label-width="140px" label-position="left">
            <el-form-item label="Default Download Directory">
              <el-input
                v-model="downloadSettings.downloadDir"
                placeholder="Please select download directory"
                readonly
              >
                <template #append>
                  <el-button @click="selectDownloadDir">
                    <el-icon><FolderOpened /></el-icon>
                    Select
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="Max Concurrent Downloads">
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
            
            <el-form-item label="Download Retry Count">
              <el-input-number
                v-model="downloadSettings.retryCount"
                :min="0"
                :max="10"
                :step="1"
                style="width: 150px;"
              />
            </el-form-item>
            
            <el-form-item label="Connection Timeout">
              <el-input-number
                v-model="downloadSettings.timeout"
                :min="5"
                :max="300"
                :step="5"
                style="width: 150px;"
              />
              <span style="margin-left: 10px; color: #909399;">seconds</span>
            </el-form-item>
            
            <el-form-item label="Auto Rename">
              <el-switch
                v-model="downloadSettings.autoRename"
                active-text="Enable"
                inactive-text="Disable"
              />
              <div class="setting-description">
                Automatically add sequence number when filename conflicts
              </div>
            </el-form-item>
            
            <el-form-item label="Download Completion Notification">
              <el-switch
                v-model="downloadSettings.notification"
                active-text="Enable"
                inactive-text="Disable"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Search Settings -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>Search Settings</span>
            </div>
          </template>
          
          <el-form :model="searchSettings" label-width="140px" label-position="left">
            <el-form-item label="Default Search Results">
              <el-input-number
                v-model="searchSettings.defaultMaxResults"
                :min="1"
                :max="1000"
                :step="10"
                style="width: 150px;"
              />
            </el-form-item>
            
            <el-form-item label="Default Sort Order">
              <el-select v-model="searchSettings.defaultSortBy" style="width: 200px;">
                <el-option label="Relevance" value="relevance" />
                <el-option label="Submission Date" value="submittedDate" />
                <el-option label="Last Updated" value="lastUpdatedDate" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Default Categories">
              <el-select
                v-model="searchSettings.defaultCategories"
                multiple
                placeholder="Please select default categories"
                style="width: 300px;"
              >
                <el-option label="Computer Science" value="cs" />
                <el-option label="Mathematics" value="math" />
                <el-option label="Physics" value="physics" />
                <el-option label="Statistics" value="stat" />
                <el-option label="Biology" value="q-bio" />
                <el-option label="Economics" value="econ" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Save Search History">
              <el-switch
                v-model="searchSettings.saveHistory"
                active-text="Enable"
                inactive-text="Disable"
              />
              <div class="setting-description">
                Save search keyword history
              </div>
            </el-form-item>
            
            <el-form-item label="Auto Complete">
              <el-switch
                v-model="searchSettings.autoComplete"
                active-text="Enable"
                inactive-text="Disable"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Interface Settings -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>Interface Settings</span>
            </div>
          </template>
          
          <el-form :model="uiSettings" label-width="140px" label-position="left">
            <el-form-item label="Theme Mode">
              <el-radio-group v-model="uiSettings.theme">
                <el-radio label="light">Light Theme</el-radio>
                <el-radio label="dark">Dark Theme</el-radio>
                <el-radio label="auto">Follow System</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="Language">
              <el-select v-model="uiSettings.language" style="width: 150px;">
                <el-option label="Chinese" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="List Display Mode">
              <el-radio-group v-model="uiSettings.listViewMode">
                <el-radio label="list">List Mode</el-radio>
                <el-radio label="grid">Grid Mode</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="Items Per Page">
              <el-select v-model="uiSettings.pageSize" style="width: 150px;">
                <el-option label="10" :value="10" />
                <el-option label="20" :value="20" />
                <el-option label="50" :value="50" />
                <el-option label="100" :value="100" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Show Thumbnails">
              <el-switch
                v-model="uiSettings.showThumbnails"
                active-text="Show"
                inactive-text="Hide"
              />
            </el-form-item>
            
            <el-form-item label="Compact Mode">
              <el-switch
                v-model="uiSettings.compactMode"
                active-text="Enable"
                inactive-text="Disable"
              />
              <div class="setting-description">
                Reduce interface spacing to show more content
              </div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- Advanced Settings -->
        <el-card class="settings-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>Advanced Settings</span>
            </div>
          </template>
          
          <el-form :model="advancedSettings" label-width="140px" label-position="left">
            <el-form-item label="API Endpoint">
              <el-input
                v-model="advancedSettings.apiEndpoint"
                placeholder="http://export.arxiv.org/api/query"
              />
            </el-form-item>
            
            <el-form-item label="Proxy Settings">
              <el-input
                v-model="advancedSettings.proxyUrl"
                placeholder="http://proxy.example.com:8080"
              >
                <template #prepend>
                  <el-switch v-model="advancedSettings.useProxy" />
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="User Agent">
              <el-input
                v-model="advancedSettings.userAgent"
                placeholder="ArxivDownloader/1.0"
              />
            </el-form-item>
            
            <el-form-item label="Cache Settings">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-switch
                    v-model="advancedSettings.enableCache"
                    active-text="Enable Cache"
                    inactive-text="Disable Cache"
                  />
                </el-col>
                <el-col :span="12">
                  <el-button @click="clearCache" :disabled="!advancedSettings.enableCache">
                    <el-icon><Delete /></el-icon>
                    Clear Cache
                  </el-button>
                </el-col>
              </el-row>
            </el-form-item>
            
            <el-form-item label="Log Level">
              <el-select v-model="advancedSettings.logLevel" style="width: 150px;">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Developer Mode">
              <el-switch
                v-model="advancedSettings.developerMode"
                active-text="Enable"
                inactive-text="Disable"
              />
              <div class="setting-description">
                Show debug information and additional development tools
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right info panel -->
      <el-col :span="6">
        <!-- System Information -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>System Information</span>
            </div>
          </template>
          
          <div class="info-item">
            <span class="info-label">Version:</span>
            <span class="info-value">v1.2.3</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Build Date:</span>
            <span class="info-value">2024-01-15</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Python Version:</span>
            <span class="info-value">3.9.7</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Cache Size:</span>
            <span class="info-value">{{ formatFileSize(cacheSize) }}</span>
          </div>
          
          <div class="info-item">
            <span class="info-label">Download Directory:</span>
            <span class="info-value">{{ formatPath(downloadSettings.downloadDir) }}</span>
          </div>
        </el-card>

        <!-- Quick Actions -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>Quick Actions</span>
            </div>
          </template>
          
          <div class="quick-actions">
            <el-button @click="openDownloadDir" style="width: 100%; margin-bottom: 10px;">
              <el-icon><FolderOpened /></el-icon>
              Open Download Directory
            </el-button>
            
            <el-button @click="exportSettings" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Upload /></el-icon>
              Export Settings
            </el-button>
            
            <el-button @click="importSettings" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Download /></el-icon>
              Import Settings
            </el-button>
            
            <el-button @click="checkUpdates" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Refresh /></el-icon>
              Check Updates
            </el-button>
            
            <el-button @click="showAbout" style="width: 100%;">
              <el-icon><QuestionFilled /></el-icon>
              About Software
            </el-button>
          </div>
        </el-card>

        <!-- Usage Statistics -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>Usage Statistics</span>
            </div>
          </template>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.totalSearches }}</div>
            <div class="stats-label">Total Searches</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.totalDownloads }}</div>
            <div class="stats-label">Total Downloads</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ formatFileSize(usageStats.totalSize) }}</div>
            <div class="stats-label">Total Download Size</div>
          </div>
          
          <div class="stats-item">
            <div class="stats-number">{{ usageStats.daysUsed }}</div>
            <div class="stats-label">Days Used</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- About Dialog -->
    <el-dialog v-model="aboutDialogVisible" title="About ArXiv Paper Downloader" width="500px">
      <div class="about-content">
        <div class="about-logo">
          <el-icon size="60"><Document /></el-icon>
        </div>
        
        <h3>ArXiv Paper Downloader</h3>
        <p>Version: v1.2.3</p>
        <p>A powerful ArXiv paper search and download tool</p>
        
        <div class="about-features">
          <h4>Main Features:</h4>
          <ul>
            <li>Intelligent paper search</li>
            <li>Batch download management</li>
            <li>Multiple format support</li>
            <li>Download statistics analysis</li>
          </ul>
        </div>
        
        <div class="about-links">
          <el-button link>GitHub Repository</el-button>
          <el-button link>Documentation</el-button>
          <el-button link>Issue Feedback</el-button>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="aboutDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Dialog state
const aboutDialogVisible = ref(false)

// Download settings
const downloadSettings = reactive({
  downloadDir: './arxiv_papers',
  maxConcurrent: 3,
  retryCount: 3,
  timeout: 30,
  autoRename: true,
  notification: true
})

// Search settings
const searchSettings = reactive({
  defaultMaxResults: 50,
  defaultSortBy: 'relevance',
  defaultCategories: ['cs'],
  saveHistory: true,
  autoComplete: true
})

// UI settings
const uiSettings = reactive({
  theme: 'light',
  language: 'zh-CN',
  listViewMode: 'list',
  pageSize: 20,
  showThumbnails: true,
  compactMode: false
})

// Advanced settings
const advancedSettings = reactive({
  apiEndpoint: 'http://export.arxiv.org/api/query',
  useProxy: false,
  proxyUrl: '',
  userAgent: 'ArxivDownloader/1.0',
  enableCache: true,
  logLevel: 'info',
  developerMode: false
})

// System information
const cacheSize = ref(52428800) // 50MB

// Usage statistics
const usageStats = reactive({
  totalSearches: 1234,
  totalDownloads: 567,
  totalSize: 15728640000, // 15GB
  daysUsed: 45
})

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Format path
const formatPath = (path) => {
  if (path.length > 30) {
    return '...' + path.slice(-27)
  }
  return path
}

// Select download directory
const selectDownloadDir = () => {
  ElMessage.info('File selector requires backend support')
}

// Save settings
const saveSettings = async () => {
  try {
    // Should call API to save settings here
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Settings saved')
  } catch (error) {
    ElMessage.error('Failed to save settings')
  }
}

// Restore default settings
const resetToDefaults = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to restore all settings to default values? This operation cannot be undone.',
      'Confirm Restore Default Settings',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    // Reset all settings to default values
    Object.assign(downloadSettings, {
      downloadDir: './arxiv_papers',
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
    
    ElMessage.success('Default settings restored')
  } catch {
    // User cancelled operation
  }
}

// Clear cache
const clearCache = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to clear all cache data?',
      'Confirm Clear Cache',
      {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    // Should call API to clear cache here
    await new Promise(resolve => setTimeout(resolve, 1000))
    cacheSize.value = 0
    ElMessage.success('Cache cleared')
  } catch {
    // User cancelled operation
  }
}

// Open download directory
const openDownloadDir = () => {
  ElMessage.info('Open folder feature requires backend support')
}

// Export settings
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
  ElMessage.success('Settings exported')
}

// Import settings
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
        
        ElMessage.success('Settings imported')
      } catch (error) {
        ElMessage.error('Failed to import settings: Invalid file format')
      }
    }
    
    reader.readAsText(file)
  }
  
  input.click()
}

// Check updates
const checkUpdates = async () => {
  try {
    ElMessage.info('Checking for updates...')
    // Simulate update check
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('Already the latest version')
  } catch (error) {
    ElMessage.error('Failed to check updates')
  }
}

// Show about dialog
const showAbout = () => {
  aboutDialogVisible.value = true
}

onMounted(() => {
  // Load settings
  console.log('Settings page loaded')
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

/* Dark theme adaptation */
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