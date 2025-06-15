<template>
  <section v-if="papers.length > 0" class="results-section">
    <div class="section-header">
      <h2 class="section-title">
        <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
        </svg>
        Search Results
        <span class="results-count">({{ papers.length }})</span>
      </h2>
      <p class="section-description">Found {{ papers.length }} papers matching your search</p>
    </div>
    
    <!-- Sort and Filter Controls -->
    <div class="controls-bar">
      <div class="sort-controls">
        <label class="control-label">
          <svg class="control-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 21L14 17H17V7H14L18 3L22 7H19V17H22M2 19V17H12V19M2 13V11H9V13M2 7V5H6V7H2Z" />
          </svg>
          Sort by:
        </label>
        <select v-model="sortBy" @change="handleSort" class="sort-select">
          <option value="relevance">Relevance</option>
          <option value="date">Publication Date</option>
          <option value="title">Title</option>
          <option value="authors">Authors</option>
        </select>
        <button @click="toggleSortOrder" class="sort-order-btn" :title="sortOrder === 'asc' ? 'Ascending' : 'Descending'">
          <svg v-if="sortOrder === 'asc'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19,17H22L18,21L14,17H17V3H19V17M2,17V15H10V17H2M6,5V3H10V5H6M2,11V9H8V11H2Z" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor">
            <path d="M19,7H22L18,3L14,7H17V21H19V7M2,17V15H10V17H2M6,5V3H10V5H6M2,11V9H8V11H2Z" />
          </svg>
        </button>
      </div>
      
      <div class="view-controls">
        <label class="control-label">View:</label>
        <div class="view-toggle">
          <button 
            @click="viewMode = 'grid'" 
            :class="{ active: viewMode === 'grid' }"
            class="view-btn"
            title="Grid View"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M3,11H11V3H3M3,21H11V13H3M13,21H21V13H13M13,3V11H21V3" />
            </svg>
          </button>
          <button 
            @click="viewMode = 'list'" 
            :class="{ active: viewMode === 'list' }"
            class="view-btn"
            title="List View"
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9,5V9H21V5M9,19H21V15H9M9,14H21V10H9M4,9H8V5H4M4,19H8V15H4M4,14H8V10H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Papers Grid/List -->
    <div :class="['papers-container', `view-${viewMode}`]">
      <PaperCard 
        v-for="paper in sortedPapers" 
        :key="paper.id"
        :paper="paper"
        :downloading="downloadingPapers.has(paper.id)"
        @download="handleDownload"
        :class="{ 'list-item': viewMode === 'list', 'grid-item': viewMode === 'grid' }"
      />
    </div>
    
    <!-- Load More Button -->
    <div v-if="hasMore" class="load-more-section">
      <button @click="handleLoadMore" :disabled="loading" class="load-more-btn">
        <svg v-if="loading" class="loading-icon" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
            <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
            <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
          </circle>
        </svg>
        <span>{{ loading ? 'Loading...' : 'Load More Papers' }}</span>
      </button>
    </div>
  </section>
  
  <!-- Empty State -->
  <section v-else-if="showEmptyState" class="empty-results">
    <div class="empty-content">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z" />
      </svg>
      <h3>No papers found</h3>
      <p>Try adjusting your search terms or filters</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import PaperCard from './PaperCard.vue'
import type { Paper } from '@/types'

// Props
interface Props {
  papers: Paper[]
  loading?: boolean
  hasMore?: boolean
  showEmptyState?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  hasMore: false,
  showEmptyState: false
})

// Emits
interface Emits {
  download: [paper: Paper]
  loadMore: []
}

const emit = defineEmits<Emits>()

// Reactive data
const sortBy = ref<'relevance' | 'date' | 'title' | 'authors'>('relevance')
const sortOrder = ref<'asc' | 'desc'>('desc')
const viewMode = ref<'grid' | 'list'>('list')
const downloadingPapers = ref(new Set<string>())

// Computed properties
const sortedPapers = computed(() => {
  if (sortBy.value === 'relevance') {
    return [...props.papers]
  }
  
  const sorted = [...props.papers].sort((a, b) => {
    let aValue: string | Date
    let bValue: string | Date
    
    switch (sortBy.value) {
      case 'date':
        aValue = new Date(a.published || '1970-01-01')
        bValue = new Date(b.published || '1970-01-01')
        break
      case 'title':
        aValue = a.title.toLowerCase()
        bValue = b.title.toLowerCase()
        break
      case 'authors':
        aValue = (a.authors?.[0] || '').toLowerCase()
        bValue = (b.authors?.[0] || '').toLowerCase()
        break
      default:
        return 0
    }
    
    if (aValue < bValue) return sortOrder.value === 'asc' ? -1 : 1
    if (aValue > bValue) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  
  return sorted
})

// Methods
const handleSort = () => {
  // Sort logic is handled by computed property
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const handleDownload = (paper: Paper) => {
  downloadingPapers.value.add(paper.id)
  emit('download', paper)
  
  // Remove from downloading set after a delay (will be managed by parent)
  setTimeout(() => {
    downloadingPapers.value.delete(paper.id)
  }, 5000)
}

const handleLoadMore = () => {
  emit('loadMore')
}
</script>

<style scoped>
.results-section {
  margin-bottom: 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.8rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.section-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.results-count {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
}

.section-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

/* Controls Bar */
.controls-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex-wrap: wrap;
  gap: 1rem;
}

.sort-controls,
.view-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.control-icon {
  width: 1rem;
  height: 1rem;
}

.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
}

.sort-order-btn {
  padding: 0.5rem;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-order-btn:hover {
  background: #e5e7eb;
}

.sort-order-btn svg {
  width: 1rem;
  height: 1rem;
}

.view-toggle {
  display: flex;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.view-btn {
  padding: 0.5rem;
  background: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn:hover {
  background: #f3f4f6;
}

.view-btn.active {
  background: #667eea;
  color: white;
}

.view-btn svg {
  width: 1rem;
  height: 1rem;
}

/* Papers Container */
.papers-container.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  max-width: 100%;
}

/* Responsive grid for better horizontal layout */
@media (min-width: 768px) {
  .papers-container.view-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .papers-container.view-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1400px) {
  .papers-container.view-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.papers-container.view-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.papers-container.view-list .list-item {
  max-width: none;
}

.papers-container.view-grid .grid-item {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Load More */
.load-more-section {
  text-align: center;
  margin-top: 2rem;
}

.load-more-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.load-more-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-icon {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-results {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-content {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 1rem;
}

.empty-results h3 {
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-results p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .controls-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .sort-controls,
  .view-controls {
    justify-content: space-between;
  }
  
  .papers-container.view-grid {
    grid-template-columns: 1fr;
  }
  
  .section-title {
    font-size: 1.5rem;
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .controls-bar {
    padding: 1rem;
  }
  
  .sort-controls,
  .view-controls {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .control-label {
    font-size: 0.9rem;
  }
}
</style>