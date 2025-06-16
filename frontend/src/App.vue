<template>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
          </svg>
          <h1 class="app-title">ArXiv Paper Downloader</h1>
        </div>
        
        <div class="connection-status">
          <div class="status-indicator">
            <span class="status-dot" :class="{
              'success': appStore.connectionStatus === 'connected',
              'danger': appStore.connectionStatus === 'disconnected',
              'warning': appStore.connectionStatus === 'connecting'
            }"></span>
            <span class="status-text">
              {{ appStore.connectionStatus === 'connected' ? '已连接' : 
                 appStore.connectionStatus === 'connecting' ? '连接中...' : '未连接' }}
            </span>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Search Section -->
      <SearchForm 
        @search="handleSearch"
        :loading="appStore.loading.search"
      />
      
      <!-- Search Results -->
      <SearchResultsList 
        v-if="appStore.hasSearchResults"
        :papers="appStore.searchResults"
        :loading="appStore.loading.search"
        @download="handleDownload"
      />
      
      <!-- Downloads Section -->
      <DownloadManager 
        :downloads="appStore.downloads"
        :loading="appStore.loading.downloads"
        @refresh="handleRefreshDownloads"
        @openFile="handleOpenFile"
        @pauseResume="handlePauseResume"
        @retry="handleRetry"
        @remove="handleRemove"
        @clearCompleted="handleClearCompleted"
      />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAppStore } from './stores/index'
import SearchForm from './components/SearchForm.vue'
import SearchResultsList from './components/SearchResultsList.vue'
import DownloadManager from './components/DownloadManager.vue'

const appStore = useAppStore()

// Event handlers for template


function handleSearch(params) {
  appStore.searchPapers(params)
}

async function handleDownload(paper) {
  try {
    const downloadPath = './arxiv_papers'
    await appStore.downloadPaper(paper, downloadPath)
    ElMessage.success(`Starting download: ${paper.title}`)
  } catch (error) {
    ElMessage.error('Download failed')
    console.error('Download error:', error)
  }
}



function handleRefreshDownloads() {
  appStore.loadDownloads()
}

function handleOpenFile(download) {
  appStore.openFile(download.id)
}

function handlePauseResume(download) {
  if (download.paused) {
    appStore.resumeDownload(download.id)
  } else {
    appStore.pauseDownload(download.id)
  }
}

function handleRetry(download) {
  appStore.retryDownload(download.id)
}

function handleRemove(download) {
  appStore.removeDownload(download.id)
}

function handleClearCompleted() {
  appStore.clearCompletedDownloads()
}

// Initialize app
onMounted(async () => {
  await appStore.testConnection()
  await appStore.loadDownloads()
})
</script>

<style scoped>
/* Main Layout */
#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow-x: hidden;
}

#app::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
  position: relative;
  z-index: 1;
}

.main-content {
  padding: 2rem;
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Header Styles */
.app-header {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem 0;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  animation: slideDown 0.6s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.logo-section:hover {
  transform: scale(1.02);
}

.app-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  letter-spacing: -0.025em;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.logo:hover {
  transform: scale(1.02);
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #667eea;
  filter: drop-shadow(0 2px 8px rgba(102, 126, 234, 0.3));
  transition: all 0.3s ease;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.logo-section:hover .logo-icon {
  transform: rotate(5deg);
  filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.4));
}

.logo-text h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.logo-text .subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
  letter-spacing: 0.025em;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-indicator:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.status-indicator.connected {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(21, 128, 61, 0.1) 100%);
  color: #059669;
  border-color: rgba(34, 197, 94, 0.3);
}

.status-indicator.disconnected {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(185, 28, 28, 0.1) 100%);
  color: #dc2626;
  border-color: rgba(239, 68, 68, 0.3);
}

.status-indicator.connecting {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
  color: #d97706;
  border-color: rgba(251, 191, 36, 0.3);
}

.status-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  background-color: #6b7280;
  position: relative;
  transition: all 0.3s ease;
}

.status-dot.success {
  background-color: #67c23a !important;
}

.status-dot.warning {
  background-color: #e6a23c !important;
}

.status-dot.danger {
  background-color: #f56c6c !important;
}

.status-dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: inherit;
  opacity: 0.6;
}

.status-indicator.connected .status-dot::after {
  animation: pulse-green 2s infinite;
}

.status-indicator.connecting .status-dot::after {
  animation: pulse-yellow 1s infinite;
}

@keyframes pulse-green {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
}

@keyframes pulse-yellow {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.3);
    opacity: 0.2;
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
}



/* Section Styles */
.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.75rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  letter-spacing: -0.025em;
}

.section-icon {
  width: 2rem;
  height: 2rem;
  filter: drop-shadow(0 2px 4px rgba(255, 255, 255, 0.3));
}

.section-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.125rem;
  margin: 0;
  font-weight: 400;
  line-height: 1.6;
}

/* Card Styles */
.search-card, .downloads-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  border-radius: 1.5rem;
  padding: 2.5rem;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.3);
  margin-bottom: 2rem;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.search-card::before, .downloads-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.search-card:hover, .downloads-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 8px 20px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.search-card:hover::before, .downloads-card:hover::before {
  opacity: 1;
}

.status-bar {
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-bar.connected {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}

.status-bar.disconnected {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

/* Search Form Styles */
.search-form {
  display: grid;
  gap: 20px;
}

.search-input-group {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.input-wrapper {
  flex: 1;
  position: relative;
  min-width: 180px;
}

.input-wrapper.small {
  flex: 0 0 80px;
  min-width: 80px;
  margin-right: 8px;
}

/* Responsive design for search form */
@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .input-wrapper,
  .input-wrapper.small {
    flex: none;
    min-width: auto;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .search-input-group {
    gap: 12px;
  }
  
  .search-btn {
    padding: 16px 20px;
    font-size: 16px;
  }
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 44px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.number-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
  text-align: center;
}

/* 隐藏数字输入框的滑轮控件 */
.number-input::-webkit-outer-spin-button,
.number-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
.number-input[type=number] {
  -moz-appearance: textfield;
}

.number-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 52px;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 10px;
}

.search-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.advanced-filters {
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.filter-icon {
  width: 16px;
  height: 16px;
  color: #667eea;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-input {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
}

.date-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.date-separator {
  color: #6b7280;
  font-weight: 500;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.date-range label {
  font-weight: bold;
  color: #555;
}

.date-range input {
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.date-range span {
  color: #666;
}

/* Search Results Styles */
.results-section {
  margin-bottom: 40px;
}

.results-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 400;
  margin-left: 8px;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.paper-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  height: fit-content;
}

.paper-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.paper-header {
  margin-bottom: 16px;
}

.paper-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.meta-icon {
  width: 16px;
  height: 16px;
  color: #94a3b8;
  flex-shrink: 0;
}

.authors {
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.publish-date {
  color: #94a3b8;
}

.paper-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.category-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.paper-abstract {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 20px;
}

.paper-abstract p {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-actions {
  display: flex;
  gap: 12px;
}

.action-link {
  flex: 1;
  padding: 10px 16px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  text-decoration: none;
}

.action-link:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.download-btn {
  flex: 1;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-icon {
  width: 16px;
  height: 16px;
}

/* Downloads Section Styles */
.downloads-section {
  margin-bottom: 40px;
}

.downloads-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 0 4px;
}

.refresh-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.refresh-btn:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.downloads-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.download-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.download-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.download-info {
  flex: 1;
  min-width: 0;
}

.download-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.download-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.download-date {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 14px;
}

.meta-icon {
  width: 14px;
  height: 14px;
}

.download-status {
  flex-shrink: 0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.status-badge.downloading {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.status-icon {
  width: 16px;
  height: 16px;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #cbd5e1;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.keywords-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.keywords-header {
  margin-bottom: 1rem;
}

.keywords-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
}

.keywords-description {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.keywords-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #3b82f6;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.keyword-item {
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 20px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.keyword-item:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .search-input-group {
    flex-direction: column;
    gap: 16px;
  }
  
  .input-wrapper.small {
    flex: 1;
  }
  
  .papers-grid {
    grid-template-columns: 1fr;
  }
  
  .paper-actions {
    flex-direction: column;
  }
  
  .date-inputs {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px;
  }
  
  .search-card, .downloads-card {
    padding: 20px;
  }
  
  .paper-card {
    padding: 20px;
  }
}
</style>