<template>
  <div id="app">
    <div class="container">
      <h1>ArXiv 论文下载器</h1>
      
      <!-- 后端连接状态 -->
      <div class="status-bar" :class="{ 'connected': backendConnected, 'disconnected': !backendConnected }">
        <span v-if="backendConnected">✅ 后端已连接</span>
        <span v-else>❌ 后端未连接</span>
        <button @click="testConnection" :disabled="testing">测试连接</button>
      </div>

      <!-- 搜索表单 -->
      <div class="search-section">
        <h2>搜索论文</h2>
        <div class="search-form">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="输入搜索关键词..."
            @keyup.enter="searchPapers"
          />
          <input 
            v-model="maxResults" 
            type="number" 
            placeholder="最大结果数"
            min="1"
            max="50"
          />
          <button @click="searchPapers" :disabled="searching">搜索</button>
        </div>
        
        <!-- 时间范围选择 -->
        <div class="date-range">
          <label>时间范围:</label>
          <input 
            v-model="dateFrom" 
            type="date" 
            placeholder="开始日期"
          />
          <span>至</span>
          <input 
            v-model="dateTo" 
            type="date" 
            placeholder="结束日期"
          />
        </div>
        
        <!-- 关键词推荐 -->
        <div class="keywords-section">
          <h3>推荐关键词</h3>
          <div class="keywords-grid">
            <button 
              v-for="keyword in recommendedKeywords" 
              :key="keyword"
              @click="useKeyword(keyword)"
              class="keyword-btn"
            >
              {{ keyword }}
            </button>
          </div>
        </div>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="results-section">
        <h2>搜索结果 ({{ searchResults.length }})</h2>
        <div class="papers-list">
          <div v-for="paper in searchResults" :key="paper.id" class="paper-item">
            <h3>{{ paper.title }}</h3>
            <p><strong>作者:</strong> {{ paper.authors.join(', ') }}</p>
            <p><strong>发布时间:</strong> {{ formatDate(paper.published) }}</p>
            <p><strong>分类:</strong> {{ paper.categories.join(', ') }}</p>
            <p class="abstract">{{ paper.summary.substring(0, 200) }}...</p>
            <div class="paper-actions">
              <a :href="paper.arxiv_url" target="_blank">查看原文</a>
              <button @click="downloadPaper(paper)" :disabled="paper.downloading">
                {{ paper.downloading ? '下载中...' : '下载PDF' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 下载历史 -->
      <div class="downloads-section">
        <h2>下载历史</h2>
        <button @click="loadDownloads">刷新</button>
        <div v-if="downloads.length > 0" class="downloads-list">
          <div v-for="download in downloads" :key="download.id" class="download-item">
            <span>{{ download.title }}</span>
            <span class="status" :class="download.status">{{ download.status }}</span>
            <span>{{ formatDate(download.created_at) }}</span>
          </div>
        </div>
        <p v-else>暂无下载记录</p>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 响应式数据
const backendConnected = ref(false)
const testing = ref(false)
const searchQuery = ref('')
const maxResults = ref(10)
const dateFrom = ref('')
const dateTo = ref('')
const searching = ref(false)
const searchResults = ref([])
const downloads = ref([])
const recommendedKeywords = ref([])

// API基础URL
const API_BASE = '/api'

// 测试后端连接
const testConnection = async () => {
  testing.value = true
  try {
    const response = await fetch(`${API_BASE}/system/info`)
    const data = await response.json()
    backendConnected.value = data.success || false
    console.log('后端连接测试:', data)
  } catch (error) {
    console.error('连接测试失败:', error)
    backendConnected.value = false
  } finally {
    testing.value = false
  }
}

// 搜索论文
const searchPapers = async () => {
  if (!searchQuery.value.trim()) {
    alert('请输入搜索关键词')
    return
  }
  
  searching.value = true
  try {
    const params = new URLSearchParams({
      query: searchQuery.value,
      max_results: maxResults.value
    })
    
    // 添加时间参数
    if (dateFrom.value) {
      params.append('date_from', dateFrom.value)
    }
    if (dateTo.value) {
      params.append('date_to', dateTo.value)
    }
    
    const response = await fetch(`${API_BASE}/papers/search?${params}`)
    const data = await response.json()
    
    if (data.success) {
      searchResults.value = data.papers
      console.log('搜索成功:', data)
    } else {
      alert('搜索失败: ' + data.error)
    }
  } catch (error) {
    console.error('搜索失败:', error)
    alert('搜索失败: ' + error.message)
  } finally {
    searching.value = false
  }
}

// 选择下载目录
const selectDownloadPath = () => {
  return new Promise((resolve) => {
    // 获取用户的默认下载路径
    const defaultPath = localStorage.getItem('arxiv_download_path') || '/Users/shemol/Downloads/ArXiv_Papers'
    
    // 提示用户输入下载路径
    const path = prompt('请输入下载路径:', defaultPath)
    
    if (path && path.trim()) {
      // 保存用户选择的路径
      localStorage.setItem('arxiv_download_path', path.trim())
      resolve(path.trim())
    } else {
      resolve(null)
    }
  })
}

// 下载论文
const downloadPaper = async (paper) => {
  paper.downloading = true
  
  try {
    // 让用户选择下载路径
    const selectedPath = await selectDownloadPath()
    
    if (!selectedPath) {
      alert('请选择下载目录')
      return
    }
    
    const response = await fetch(`${API_BASE}/papers/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        paper_id: paper.id,
        title: paper.title,
        download_path: selectedPath
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      alert(`下载成功！文件保存到: ${selectedPath}`)
      loadDownloads() // 刷新下载列表
    } else {
      alert('下载失败: ' + data.error)
    }
  } catch (error) {
    console.error('下载失败:', error)
    alert('下载失败: ' + error.message)
  } finally {
    paper.downloading = false
  }
}

// 加载下载历史
const loadDownloads = async () => {
  try {
    const response = await fetch(`${API_BASE}/downloads`)
    const data = await response.json()
    
    if (data.success) {
      downloads.value = data.downloads
    }
  } catch (error) {
    console.error('加载下载历史失败:', error)
  }
}

// 加载推荐关键词
const loadRecommendedKeywords = async () => {
  try {
    const response = await fetch(`${API_BASE}/keywords/recommendations`)
    const data = await response.json()
    
    if (data.success) {
      recommendedKeywords.value = data.keywords
    }
  } catch (error) {
    console.error('加载推荐关键词失败:', error)
  }
}

// 使用推荐关键词
const useKeyword = (keyword) => {
  searchQuery.value = keyword
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 组件挂载时测试连接
onMounted(() => {
  testConnection()
  loadDownloads()
  loadRecommendedKeywords()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

h2 {
  color: #555;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
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

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-form input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-form button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-form button:hover {
  background-color: #0056b3;
}

.search-form button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
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

.papers-list {
  display: grid;
  gap: 20px;
}

.paper-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background-color: #f9f9f9;
}

.paper-item h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.paper-item p {
  margin: 5px 0;
  color: #666;
}

.abstract {
  font-style: italic;
  color: #777;
}

.paper-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.paper-actions a {
  color: #007bff;
  text-decoration: none;
}

.paper-actions a:hover {
  text-decoration: underline;
}

.paper-actions button {
  padding: 5px 15px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.paper-actions button:hover {
  background-color: #218838;
}

.paper-actions button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.downloads-list {
  margin-top: 10px;
}

.download-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.completed {
  background-color: #d4edda;
  color: #155724;
}

.status.downloading {
  background-color: #fff3cd;
  color: #856404;
}

.status.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.status.pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.keywords-section {
  margin-top: 30px;
}

.keywords-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 15px;
}

.keyword-btn {
  padding: 8px 12px;
  background-color: #e9ecef;
  color: #495057;
  border: 1px solid #ced4da;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  text-align: center;
}

.keyword-btn:hover {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  transform: translateY(-1px);
}

.keyword-btn:active {
  transform: translateY(0);
}
</style>