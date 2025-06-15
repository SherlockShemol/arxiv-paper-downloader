<template>
  <div class="search-page">
    <!-- 搜索表单 -->
    <el-card class="search-form-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>论文搜索</span>
        </div>
      </template>
      
      <el-form :model="searchForm" :rules="rules" ref="searchFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="搜索关键词" prop="query">
              <el-input
                v-model="searchForm.query"
                placeholder="请输入论文标题、作者或关键词"
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
            <el-form-item label="最大结果数">
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
            <el-form-item label="排序方式">
              <el-select v-model="searchForm.sortBy" style="width: 100%">
                <el-option label="相关性" value="relevance" />
                <el-option label="提交日期" value="submittedDate" />
                <el-option label="最后更新" value="lastUpdatedDate" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学科分类">
              <el-select v-model="searchForm.category" clearable style="width: 100%">
                <el-option label="计算机科学" value="cs" />
                <el-option label="数学" value="math" />
                <el-option label="物理" value="physics" />
                <el-option label="统计学" value="stat" />
                <el-option label="量化生物学" value="q-bio" />
                <el-option label="量化金融" value="q-fin" />
                <el-option label="经济学" value="econ" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="searchForm.dateFrom"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="searchForm.dateTo"
                type="date"
                placeholder="选择结束日期"
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
            搜索论文
          </el-button>
          <el-button @click="resetForm">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="handleBatchDownload" :disabled="selectedPapers.length === 0">
            <el-icon><Download /></el-icon>
            批量下载 ({{ selectedPapers.length }})
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 搜索结果 -->
    <el-card v-if="searchResults.length > 0 || searching" class="results-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><List /></el-icon>
          <span>搜索结果 ({{ searchResults.length }})</span>
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
      
      <!-- 加载状态 -->
      <div v-if="searching" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      
      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list'" class="list-view">
        <el-table
          :data="searchResults"
          @selection-change="handleSelectionChange"
          stripe
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="标题" min-width="300">
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
          
          <el-table-column label="作者" width="200">
            <template #default="{ row }">
              <div class="authors">
                <span v-for="(author, index) in row.authors.slice(0, 2)" :key="index">
                  {{ author }}<span v-if="index < Math.min(row.authors.length, 2) - 1">, </span>
                </span>
                <span v-if="row.authors.length > 2"> 等</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="摘要" min-width="300">
            <template #default="{ row }">
              <div class="abstract">
                {{ row.summary.substring(0, 150) }}...
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" fixed="right">
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
      
      <!-- 网格视图 -->
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
                <span v-if="paper.authors.length > 3"> 等</span>
              </div>
              
              <p class="paper-abstract">{{ paper.summary.substring(0, 120) }}...</p>
              
              <div class="paper-footer">
                <span class="paper-date">{{ formatDate(paper.published) }}</span>
                <el-button size="small" type="primary" @click.stop="downloadPaper(paper)">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 分页 -->
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

    <!-- 论文详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="论文详情" width="80%" top="5vh">
      <div v-if="selectedPaper" class="paper-detail">
        <h2>{{ selectedPaper.title }}</h2>
        
        <div class="detail-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ArXiv ID">{{ selectedPaper.id }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ selectedPaper.category }}</el-descriptions-item>
            <el-descriptions-item label="发布日期">{{ formatDate(selectedPaper.published) }}</el-descriptions-item>
            <el-descriptions-item label="更新日期">{{ formatDate(selectedPaper.updated) }}</el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="detail-authors">
          <h3>作者</h3>
          <el-tag v-for="author in selectedPaper.authors" :key="author" class="author-tag">
            {{ author }}
          </el-tag>
        </div>
        
        <div class="detail-abstract">
          <h3>摘要</h3>
          <p>{{ selectedPaper.summary }}</p>
        </div>
        
        <div class="detail-links">
          <h3>链接</h3>
          <el-button-group>
            <el-button @click="openLink(selectedPaper.url)">
              <el-icon><Link /></el-icon>
              ArXiv 页面
            </el-button>
            <el-button @click="openLink(selectedPaper.pdfUrl)">
              <el-icon><Document /></el-icon>
              PDF 链接
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadPaper(selectedPaper)">
          <el-icon><Download /></el-icon>
          下载论文
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 表单数据
const searchForm = reactive({
  query: '',
  maxResults: 20,
  sortBy: 'relevance',
  category: '',
  dateFrom: '',
  dateTo: ''
})

// 表单验证规则
const rules = {
  query: [
    { required: true, message: '请输入搜索关键词', trigger: 'blur' }
  ]
}

// 组件引用
const searchFormRef = ref()

// 状态变量
const searching = ref(false)
const searchResults = ref([])
const selectedPapers = ref([])
const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(20)
const totalResults = ref(0)
const detailDialogVisible = ref(false)
const selectedPaper = ref(null)

// 搜索论文
const handleSearch = async () => {
  try {
    await searchFormRef.value.validate()
    searching.value = true
    
    // 模拟API调用
    setTimeout(() => {
      searchResults.value = generateMockResults()
      totalResults.value = searchResults.value.length
      searching.value = false
      ElMessage.success(`找到 ${searchResults.value.length} 篇相关论文`)
    }, 2000)
    
  } catch (error) {
    ElMessage.error('搜索失败，请检查输入参数')
  }
}

// 生成模拟搜索结果
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

// 重置表单
const resetForm = () => {
  searchFormRef.value.resetFields()
  searchResults.value = []
  selectedPapers.value = []
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedPapers.value = selection
}

// 更新选择状态
const updateSelection = () => {
  selectedPapers.value = searchResults.value.filter(paper => paper.selected)
}

// 选择论文
const selectPaper = (paper) => {
  paper.selected = !paper.selected
  updateSelection()
}

// 查看论文详情
const viewPaperDetail = (paper) => {
  selectedPaper.value = paper
  detailDialogVisible.value = true
}

// 下载单篇论文
const downloadPaper = async (paper) => {
  try {
    ElMessage.success(`开始下载: ${paper.title}`)
    // 这里应该调用实际的下载API
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 批量下载
const handleBatchDownload = async () => {
  try {
    const result = await ElMessageBox.confirm(
      `确定要下载选中的 ${selectedPapers.value.length} 篇论文吗？`,
      '批量下载确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    if (result === 'confirm') {
      ElMessage.success(`开始批量下载 ${selectedPapers.value.length} 篇论文`)
      // 这里应该调用实际的批量下载API
    }
  } catch (error) {
    // 用户取消
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

// 打开链接
const openLink = (url) => {
  window.open(url, '_blank')
}

onMounted(() => {
  // 初始化
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

/* 暗色主题适配 */
:global(.dark) .paper-title-grid a {
  color: #e5eaf3;
}

:global(.dark) .paper-detail h2 {
  color: #e5eaf3;
}
</style>