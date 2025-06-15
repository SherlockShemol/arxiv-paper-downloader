<template>
  <div id="app">
    <div class="container">
      <h1>ArXiv Paper Downloader</h1>
      
      <!-- Backend connection status -->
      <div class="status-bar" :class="{ 'connected': backendConnected, 'disconnected': !backendConnected }">
        <span v-if="backendConnected">✅ Backend Connected</span>
        <span v-else>❌ Backend Disconnected</span>
        <button @click="testConnection" :disabled="testing">Test Connection</button>
      </div>

      <!-- Search form -->
      <div class="search-section">
        <h2>Search Papers</h2>
        <div class="search-form">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Enter search keywords..."
            @keyup.enter="searchPapers"
          />
          <input 
            v-model="maxResults" 
            type="number" 
            placeholder="Max Results"
            min="1"
            max="50"
          />
          <button @click="searchPapers" :disabled="searching">Search</button>
        </div>
        
        <!-- Date range selection -->
        <div class="date-range">
          <label>Date Range:</label>
          <input 
            v-model="dateFrom" 
            type="date" 
            placeholder="Start Date"
          />
          <span>to</span>
          <input 
            v-model="dateTo" 
            type="date" 
            placeholder="End Date"
          />
        </div>
        
        <!-- Keyword recommendations -->
        <div class="keywords-section">
          <h3>Recommended Keywords</h3>
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

      <!-- Search results -->
      <div v-if="searchResults.length > 0" class="results-section">
        <h2>Search Results ({{ searchResults.length }})</h2>
        <div class="papers-list">
          <div v-for="paper in searchResults" :key="paper.id" class="paper-item">
            <h3>{{ paper.title }}</h3>
            <p><strong>Authors:</strong> {{ paper.authors.join(', ') }}</p>
            <p><strong>Published:</strong> {{ formatDate(paper.published) }}</p>
            <p><strong>Categories:</strong> {{ paper.categories.join(', ') }}</p>
            <p class="abstract">{{ paper.summary.substring(0, 200) }}...</p>
            <div class="paper-actions">
              <a :href="paper.arxiv_url" target="_blank">View Original</a>
              <button @click="downloadPaper(paper)" :disabled="paper.downloading">
                {{ paper.downloading ? 'Downloading...' : 'Download PDF' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Download history -->
      <div class="downloads-section">
        <h2>Download History</h2>
        <button @click="loadDownloads">Refresh</button>
        <div v-if="downloads.length > 0" class="downloads-list">
          <div v-for="download in downloads" :key="download.id" class="download-item">
            <span>{{ download.title }}</span>
            <span class="status" :class="download.status">{{ download.status }}</span>
            <span>{{ formatDate(download.created_at) }}</span>
          </div>
        </div>
        <p v-else>No download records</p>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Reactive data
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

// API base URL
const API_BASE = '/api'

// Test backend connection
const testConnection = async () => {
  testing.value = true
  try {
    const response = await fetch(`${API_BASE}/system/info`)
    const data = await response.json()
    backendConnected.value = data.success || false
    console.log('Backend connection test:', data)
  } catch (error) {
    console.error('Connection test failed:', error)
    backendConnected.value = false
  } finally {
    testing.value = false
  }
}

// Search papers
const searchPapers = async () => {
  if (!searchQuery.value.trim()) {
    alert('Please enter search keywords')
    return
  }
  
  searching.value = true
  try {
    const params = new URLSearchParams({
      query: searchQuery.value,
      max_results: maxResults.value
    })
    
    // Add time parameters
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
      console.log('Search successful:', data)
    } else {
      alert('Search failed: ' + data.error)
    }
  } catch (error) {
    console.error('Search failed:', error)
    alert('Search failed: ' + error.message)
  } finally {
    searching.value = false
  }
}

// Select download directory
const selectDownloadPath = () => {
  return new Promise((resolve) => {
    // Get user's default download path
    const defaultPath = localStorage.getItem('arxiv_download_path') || '~/Downloads/ArXiv_Papers'
    
    // Prompt user to enter download path
    const path = prompt('Please enter download path:', defaultPath)
    
    if (path && path.trim()) {
      // Save user selected path
      localStorage.setItem('arxiv_download_path', path.trim())
      resolve(path.trim())
    } else {
      resolve(null)
    }
  })
}

// Download paper
const downloadPaper = async (paper) => {
  paper.downloading = true
  
  try {
    // Let user select download path
    const selectedPath = await selectDownloadPath()
    
    if (!selectedPath) {
      alert('Please select download directory')
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
      alert(`Download successful! File saved to: ${selectedPath}`)
      loadDownloads() // Refresh download list
    } else {
      alert('Download failed: ' + data.error)
    }
  } catch (error) {
    console.error('Download failed:', error)
    alert('Download failed: ' + error.message)
  } finally {
    paper.downloading = false
  }
}

// Load download history
const loadDownloads = async () => {
  try {
    const response = await fetch(`${API_BASE}/downloads`)
    const data = await response.json()
    
    if (data.success) {
      downloads.value = data.downloads
    }
  } catch (error) {
    console.error('Failed to load download history:', error)
  }
}

// Load recommended keywords
const loadRecommendedKeywords = async () => {
  try {
    const response = await fetch(`${API_BASE}/keywords/recommendations`)
    const data = await response.json()
    
    if (data.success) {
      recommendedKeywords.value = data.keywords
    }
  } catch (error) {
    console.error('Failed to load recommended keywords:', error)
  }
}

// Use recommended keyword
const useKeyword = (keyword) => {
  searchQuery.value = keyword
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleString('zh-CN')
}

// Test connection when component mounts
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