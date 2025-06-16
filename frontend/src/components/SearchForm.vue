<template>
  <section class="search-section">
    <div class="section-header">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
        </svg>
        Search Papers
      </h2>
      <p class="section-description">Find academic papers from arXiv repository</p>
    </div>
    
    <div class="search-card">
      <div class="search-form">
        <div class="search-input-group">
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Enter search keywords (e.g., machine learning, quantum computing)..."
              @keyup.enter="handleSearch"
              class="search-input"
            />
          </div>
          <div class="input-wrapper small">
            <input 
              v-model="maxResults" 
              type="number" 
              placeholder="Max Results"
              min="1"
              max="50"
              class="number-input"
            />
          </div>
          <button @click="handleSearch" :disabled="searching" class="search-btn">
            <svg v-if="searching" class="action-icon loading-spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
              </circle>
            </svg>
            <svg v-else class="action-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
            </svg>
            {{ searching ? 'Searching...' : 'Search' }}
          </button>
        </div>
        
        <!-- Advanced filters -->
        <div class="advanced-filters">
          <div class="filter-row">
            <div class="filter-group">
              <label class="filter-label">
                <svg class="filter-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" />
                </svg>
                Date Range
              </label>
              <div class="date-inputs">
                <input 
                  v-model="dateFrom" 
                  type="date" 
                  class="date-input"
                  title="Start Date"
                />
                <span class="date-separator">to</span>
                <input 
                  v-model="dateTo" 
                  type="date" 
                  class="date-input"
                  title="End Date"
                />
              </div>
            </div>
            
            <div class="filter-group">
              <label class="filter-label">
                <svg class="filter-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z" />
                </svg>
                Search Field
              </label>
              <select v-model="searchField" class="select-input">
                <option value="all">All Fields</option>
                <option value="title">Title</option>
                <option value="author">Author</option>
                <option value="abstract">Abstract</option>
                <option value="category">Category</option>
              </select>
            </div>
          </div>
          
          <div class="filter-row">
            <div class="filter-group">
              <label class="filter-label">
                <svg class="filter-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,13H15V11H3M3,6V8H21V6M3,18H9V16H3V18Z" />
                </svg>
                Sort By
              </label>
              <select v-model="sortBy" class="select-input">
                <option value="relevance">Relevance</option>
                <option value="lastUpdatedDate">Last Updated</option>
                <option value="submittedDate">Submitted Date</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label class="filter-label">
                <svg class="filter-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3,13H15V11H3M3,6V8H21V6M3,18H9V16H3V18Z" />
                </svg>
                Sort Order
              </label>
              <select v-model="sortOrder" class="select-input">
                <option value="descending">Descending</option>
                <option value="ascending">Ascending</option>
              </select>
            </div>
          </div>
          
          <div class="filter-row">

          </div>
        </div>
      </div>
      
      <!-- Keyword recommendations -->
      <div class="keywords-section">
        <div class="keywords-header">
          <h3 class="keywords-title">
            <svg class="keywords-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9.5,12L2,19.5L4.5,22L12,14.5L19.5,22L22,19.5L14.5,12L22,4.5L19.5,2L12,9.5L4.5,2L2,4.5L9.5,12Z" />
            </svg>
            Popular Keywords
          </h3>
          <p class="keywords-description">Click to use these popular search terms</p>
        </div>
        <div class="keyword-list">
          <button 
            v-for="keyword in recommendedKeywords" 
            :key="keyword"
            @click="useKeyword(keyword)"
            class="keyword-item"
          >
            {{ keyword }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { SearchParams } from '@/types'
import api from '@/api'

// Props
interface Props {
  searching?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  searching: false
})

// Emits
interface Emits {
  search: [params: SearchParams]
}

const emit = defineEmits<Emits>()

// Reactive data
const searchQuery = ref('')
const maxResults = ref(10)
const dateFrom = ref('')
const dateTo = ref('')
const searchField = ref('all')
const sortBy = ref('relevance')
const sortOrder = ref('descending')

const recommendedKeywords = ref<string[]>([])

// Methods
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    alert('Please enter search keywords')
    return
  }
  
  const params: SearchParams = {
    query: searchQuery.value,
    max_results: maxResults.value
  }
  
  if (dateFrom.value) {
    params.date_from = dateFrom.value
  }
  if (dateTo.value) {
    params.date_to = dateTo.value
  }
  
  // Add enhanced search parameters (always enabled)
  if (searchField.value !== 'all') {
    params.search_field = searchField.value
  }
  params.sort_by = sortBy.value
  params.sort_order = sortOrder.value
  
  emit('search', params)
}

const useKeyword = (keyword: string) => {
  searchQuery.value = keyword
}

const loadRecommendedKeywords = async () => {
  // Load recommended keywords without making API call
  recommendedKeywords.value = [
    'machine learning',
    'deep learning',
    'neural networks',
    'computer vision',
    'natural language processing',
    'quantum computing',
    'artificial intelligence',
    'reinforcement learning'
  ]
}

// Lifecycle
onMounted(() => {
  loadRecommendedKeywords()
})
</script>

<style scoped>
/* Search Section */
.search-section {
  margin-bottom: 3rem;
  animation: fadeInUp 0.8s ease-out 0.3s both;
}

.section-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 2.25rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.75rem;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: -0.025em;
}

.section-icon {
  width: 2.25rem;
  height: 2.25rem;
  filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.3));
}

.section-description {
  color: #5a6c7d;
  font-size: 1.125rem;
  font-weight: 400;
  line-height: 1.6;
}

.search-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(25px);
  border-radius: 1.5rem;
  padding: 3rem;
  box-shadow: 
    0 12px 48px rgba(0, 0, 0, 0.12),
    0 6px 16px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  color: #2c3e50;
}

.search-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% {
    background-position: 200% 0;
  }
  50% {
    background-position: -200% 0;
  }
}

.search-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 20px 64px rgba(0, 0, 0, 0.15),
    0 8px 24px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.search-form {
  margin-bottom: 2.5rem;
}

.search-input-group {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: end;
}

@media (max-width: 768px) {
  .search-input-group {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}

.input-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-wrapper.small {
  min-width: 140px;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.input-icon {
  position: absolute;
  left: 1.25rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
  pointer-events: none;
  transition: all 0.3s ease;
}

.search-input,
.number-input,
.date-input {
  width: 100%;
  padding: 1.25rem 1.25rem 1.25rem 3.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 1rem;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.number-input,
.date-input {
  padding-left: 1.25rem;
}

.search-input:focus,
.number-input:focus,
.date-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 
    0 0 0 4px rgba(102, 126, 234, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.search-input:focus + .input-icon,
.number-input:focus + .input-icon,
.date-input:focus + .input-icon {
  color: #667eea;
  transform: translateY(-50%) scale(1.1);
}

.search-btn {
  padding: 1.25rem 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 1rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.3),
    0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  min-width: 140px;
}

.search-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 20px rgba(102, 126, 234, 0.4),
    0 4px 8px rgba(0, 0, 0, 0.15);
}

.search-btn:hover::before {
  left: 100%;
}

.search-btn:active {
  transform: translateY(0);
  box-shadow: 
    0 2px 8px rgba(102, 126, 234, 0.3),
    0 1px 2px rgba(0, 0, 0, 0.1);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-btn:disabled:hover {
  transform: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  white-space: nowrap;
  letter-spacing: 0.025em;
}

.action-icon {
  width: 1.2rem;
  height: 1.2rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Advanced Filters */
.advanced-filters {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.filter-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-group.full-width {
  flex: 1 1 100%;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.filter-icon {
  width: 1rem;
  height: 1rem;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.date-input {
  padding: 0.75rem;
  width: 150px;
}

.select-input {
  padding: 0.75rem;
  background: white;
  color: #2c3e50;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.3s ease;
  min-width: 150px;
}

.select-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-input option {
  background: white;
  color: #2c3e50;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: #3b82f6;
}

.checkbox-label {
  color: #2c3e50;
  font-size: 0.9rem;
  cursor: pointer;
  user-select: none;
}

.date-separator {
  color: #6b7280;
  font-weight: 500;
}

/* Keywords Section */
.keywords-section {
  border-top: 2px solid rgba(102, 126, 234, 0.1);
  padding-top: 2rem;
  margin-top: 2rem;
  position: relative;
}

.keywords-section::before {
  content: '';
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 1px;
}

.keywords-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.keywords-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.keywords-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #667eea;
}

.keywords-description {
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.5;
}

.keyword-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1rem;
}

.keyword-item {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.keyword-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.keyword-item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  transform: translateY(-2px) scale(1.05);
  box-shadow: 
    0 8px 20px rgba(102, 126, 234, 0.3),
    0 4px 8px rgba(0, 0, 0, 0.1);
}

.keyword-item:hover::before {
  left: 100%;
}

.keyword-item:active {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 
    0 4px 12px rgba(102, 126, 234, 0.2),
    0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
  }
  
  .input-wrapper.small {
    flex: 1;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .date-inputs {
    width: 100%;
  }
  
  .date-input {
    flex: 1;
    min-width: 120px;
  }
}
</style>