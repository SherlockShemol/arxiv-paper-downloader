<template>
  <div class="search-page">
    <!-- Search form -->
    <el-card class="search-form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>Paper Search</span>
        </div>
      </template>
      
      <el-form :model="searchForm" :rules="rules" ref="searchFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Search Keywords" prop="query">
              <el-input
                v-model="searchForm.query"
                placeholder="Enter paper title, author or keywords"
                clearable
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="Max Results">
              <el-input-number
                v-model="searchForm.maxResults"
                :min="1"
                :max="100"
                :step="10"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="6">
            <el-form-item label="Sort By">
              <el-select v-model="searchForm.sortBy" style="width: 100%">
                <el-option label="Relevance" value="relevance" />
                <el-option label="Submitted Date" value="submittedDate" />
                <el-option label="Last Updated" value="lastUpdatedDate" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Subject Categories">
              <el-select v-model="searchForm.category" clearable style="width: 100%">
                <el-option label="Computer Science" value="cs" />
                <el-option label="Mathematics" value="math" />
                <el-option label="Physics" value="physics" />
                <el-option label="Statistics" value="stat" />
                <el-option label="Quantitative Biology" value="q-bio" />
                <el-option label="Quantitative Finance" value="q-fin" />
                <el-option label="Economics" value="econ" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="Start Date">
              <el-date-picker
                v-model="searchForm.dateFrom"
                type="date"
                placeholder="Select Start Date"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="End Date">
              <el-date-picker
                v-model="searchForm.dateTo"
                type="date"
                placeholder="Select End Date"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="searching">
            <el-icon><Search /></el-icon>
            Search Papers
          </el-button>
          <el-button @click="resetForm">
            <el-icon><Refresh /></el-icon>
            Reset
          </el-button>
          <el-button type="success" @click="handleBatchDownload" :disabled="selectedPapers.length === 0">
            <el-icon><Download /></el-icon>
            Batch Download ({{ selectedPapers.length }})
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Search results -->
    <el-card v-if="searchResults.length > 0 || searching" class="results-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><List /></el-icon>
          <span>Search Results ({{ searchResults.length }})</span>
          <div class="header-actions">
            <el-button-group>
              <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
                <el-icon><List /></el-icon>
              </el-button>
              <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'">
                <el-icon><Grid /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <!-- Loading state -->
      <div v-if="searching" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <!-- List view -->
      <div v-else-if="viewMode === 'list'" class="list-view">
        <el-table
          :data="searchResults"
          @selection-change="handleSelectionChange"
          stripe
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="Title" min-width="300">
            <template #default="{ row }">
              <div class="paper-title">
                <a :href="row.url" target="_blank" class="title-link">
                  {{ row.title }}
                </a>
                <div class="paper-meta">
                  <el-tag size="small" type="info">{{ row.category }}</el-tag>
                  <span class="date">{{ formatDate(row.published) }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Authors" width="200">
            <template #default="{ row }">
              <div class="authors">
                <span v-for="(author, index) in row.authors.slice(0, 2)" :key="index">
                  {{ author }}<span v-if="index < Math.min(row.authors.length, 2) - 1">, </span>
                </span>
                <span v-if="row.authors.length > 2"> et al.</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Abstract" min-width="300">
            <template #default="{ row }">
              <div class="abstract">
                {{ row.summary.substring(0, 150) }}...
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Actions" width="150" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button size="small" @click="viewPaperDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button size="small" type="primary" @click="downloadPaper(row)">
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- Grid view -->
      <div v-else class="grid-view">
        <el-row :gutter="20">
          <el-col :span="8" v-for="paper in searchResults" :key="paper.id">
            <el-card class="paper-card" shadow="hover" @click="selectPaper(paper)">
              <div class="paper-header">
                <el-checkbox
                  v-model="paper.selected"
                  @change="updateSelection"
                  @click.stop
                />
                <el-tag size="small" type="info">{{ paper.category }}</el-tag>
              </div>
              
              <h3 class="paper-title-grid">
                <a :href="paper.url" target="_blank" @click.stop>
                  {{ paper.title }}
                </a>
              </h3>
              
              <div class="paper-authors">
                <span v-for="(author, index) in paper.authors.slice(0, 3)" :key="index">
                  {{ author }}<span v-if="index < Math.min(paper.authors.length, 3) - 1">, </span>
                </span>
                <span v-if="paper.authors.length > 3"> et al.</span>
              </div>
              
              <p class="paper-abstract">{{ paper.summary.substring(0, 120) }}...</p>
              
              <div class="paper-footer">
                <span class="paper-date">{{ formatDate(paper.published) }}</span>
                <el-button size="small" type="primary" @click.stop="downloadPaper(paper)">
                  <el-icon><Download /></el-icon>
                  Download
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- Pagination -->
      <div class="pagination-container" v-if="searchResults.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalResults"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Paper details dialog -->
<el-dialog v-model="detailDialogVisible" title="Paper Details" width="80%" top="5vh">
      <div v-if="selectedPaper" class="paper-detail">
        <h2>{{ selectedPaper.title }}</h2>
        
        <div class="detail-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ArXiv ID">{{ selectedPaper.id }}</el-descriptions-item>
            <el-descriptions-item label="Category">{{ selectedPaper.category }}</el-descriptions-item>
        <el-descriptions-item label="Published Date">{{ formatDate(selectedPaper.published) }}</el-descriptions-item>
        <el-descriptions-item label="Updated Date">{{ formatDate(selectedPaper.updated) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-authors">
          <h3>Authors</h3>
          <el-tag v-for="author in selectedPaper.authors" :key="author" class="author-tag">
            {{ author }}
          </el-tag>
        </div>
        
        <div class="detail-abstract">
          <h3>Abstract</h3>
          <p>{{ selectedPaper.summary }}</p>
        </div>
        
        <div class="detail-links">
          <h3>Links</h3>
          <el-button-group>
            <el-button @click="openLink(selectedPaper.url)">
              <el-icon><Link /></el-icon>
              ArXiv Page
            </el-button>
            <el-button @click="openLink(selectedPaper.pdfUrl)">
              <el-icon><Document /></el-icon>
              PDF Link
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadPaper(selectedPaper)">
          <el-icon><Download /></el-icon>
          Download Paper
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// Form data
const searchForm = reactive({
  query: '',
  maxResults: 20,
  sortBy: 'relevance',
  category: '',
  dateFrom: '',
  dateTo: ''
})

// Form validation rules
const rules = {
  query: [
    { required: true, message: 'Please enter search keywords', trigger: 'blur' }
  ]
}

// Component references
const searchFormRef = ref()

// State variables
const searching = ref(false)
const searchResults = ref([])
const selectedPapers = ref([])
const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(20)
const totalResults = ref(0)
const detailDialogVisible = ref(false)
const selectedPaper = ref(null)

// Search papers
const handleSearch = async () => {
  try {
    await searchFormRef.value.validate()
    searching.value = true
    
    // Prepare search parameters
    const searchParams = {
      query: searchForm.query,
      max_results: searchForm.maxResults,
      date_from: searchForm.dateFrom || undefined,
      date_to: searchForm.dateTo || undefined
    }
    
    // Call real API
    const response = await fetch('http://localhost:5001/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(searchParams)
    })
    
    const data = await response.json()
    
    if (data.success && data.papers) {
      // Transform API response to match frontend format
      searchResults.value = data.papers.map(paper => ({
        id: paper.id,
        title: paper.title,
        authors: paper.authors,
        summary: paper.abstract || paper.summary,
        abstract: paper.abstract || paper.summary,
        published: paper.published,
        categories: paper.categories,
        pdf_url: paper.pdf_url,
        arxiv_url: paper.arxiv_url,
        url: paper.arxiv_url,
        category: paper.categories?.[0] || 'Unknown',
        downloading: false,
        selected: false
      }))
      totalResults.value = data.total || searchResults.value.length
      ElMessage.success(`Found ${searchResults.value.length} related papers`)
    } else {
      searchResults.value = []
      totalResults.value = 0
      ElMessage.error(data.error || 'Search failed')
    }
    
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
    totalResults.value = 0
    ElMessage.error('Search request failed')
  } finally {
    searching.value = false
  }
}

// Generate mock search results
const generateMockResults = () => {
  const mockPapers = []
  for (let i = 1; i <= 20; i++) {
    mockPapers.push({
      id: `2024.0001${i.toString().padStart(2, '0')}`,
      title: `Attention Is All You Need: A Comprehensive Study ${i}`,
      authors: ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
      summary: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism.',
      category: 'cs.LG',
      published: '2024-01-15',
      updated: '2024-01-16',
      url: `https://arxiv.org/abs/2024.0001${i.toString().padStart(2, '0')}`,
      pdfUrl: `https://arxiv.org/pdf/2024.0001${i.toString().padStart(2, '0')}.pdf`,
      selected: false
    })
  }
  return mockPapers
}

// Reset form
const resetForm = () => {
  searchFormRef.value.resetFields()
  searchResults.value = []
  selectedPapers.value = []
}

// Handle selection change
const handleSelectionChange = (selection) => {
  selectedPapers.value = selection
}

// Update selection state
const updateSelection = () => {
  selectedPapers.value = searchResults.value.filter(paper => paper.selected)
}

// Select paper
const selectPaper = (paper) => {
  paper.selected = !paper.selected
  updateSelection()
}

// View paper details
const viewPaperDetail = (paper) => {
  selectedPaper.value = paper
  detailDialogVisible.value = true
}

// Download single paper
const downloadPaper = async (paper) => {
  try {
    ElMessage.success(`Starting download: ${paper.title}`)
    // Should call actual download API here
  } catch (error) {
    ElMessage.error('Download failed')
  }
}

// Batch download
const handleBatchDownload = async () => {
  try {
    const result = await ElMessageBox.confirm(
      `Are you sure you want to download the selected ${selectedPapers.value.length} papers?`,
      'Batch Download Confirmation',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      ElMessage.success(`Starting batch download of ${selectedPapers.value.length} papers`)
      // Should call actual batch download API here
    }
  } catch (error) {
    // User cancelled
  }
}

// Pagination handling
const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}

// Format date
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

// Open link
const openLink = (url) => {
  window.open(url, '_blank')
}

onMounted(() => {
  // Initialize
})
</script>

<style scoped>
.search-page {
  max-width: 1400px;
  margin: 0 auto;
}

.search-form-card {
  margin-bottom: 20px;
}

.results-card {
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

.loading-container {
  padding: 20px;
}

.list-view {
  margin-bottom: 20px;
}

.paper-title {
  line-height: 1.5;
}

.title-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
}

.title-link:hover {
  text-decoration: underline;
}

.paper-meta {
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.date {
  color: #909399;
  font-size: 12px;
}

.authors {
  color: #606266;
  font-size: 14px;
}

.abstract {
  color: #909399;
  font-size: 13px;
  line-height: 1.4;
}

.grid-view {
  margin-bottom: 20px;
}

.paper-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.paper-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.paper-title-grid {
  margin: 10px 0;
  font-size: 16px;
  line-height: 1.4;
}

.paper-title-grid a {
  color: #303133;
  text-decoration: none;
}

.paper-title-grid a:hover {
  color: #409EFF;
}

.paper-authors {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.paper-abstract {
  color: #909399;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: 15px;
}

.paper-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.paper-date {
  color: #909399;
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.paper-detail h2 {
  margin-bottom: 20px;
  color: #303133;
}

.detail-meta {
  margin-bottom: 20px;
}

.detail-authors {
  margin-bottom: 20px;
}

.author-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.detail-abstract {
  margin-bottom: 20px;
}

.detail-abstract p {
  line-height: 1.6;
  color: #606266;
}

.detail-links {
  margin-bottom: 20px;
}

/* Dark theme adaptation */
:global(.dark) .paper-title-grid a {
  color: #e5eaf3;
}

:global(.dark) .paper-detail h2 {
  color: #e5eaf3;
}
</style>