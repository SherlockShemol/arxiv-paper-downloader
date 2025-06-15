<template>
  <article class="paper-card">
    <div class="paper-header">
      <h3 class="paper-title">{{ paper.title }}</h3>
      <div class="paper-meta">
        <div class="meta-item">
          <svg class="meta-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
          </svg>
          <span class="authors">{{ formattedAuthors }}</span>
        </div>
        <div class="meta-item">
          <svg class="meta-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,5V19H5V5H19Z" />
          </svg>
          <span class="publish-date">{{ formattedDate }}</span>
        </div>
      </div>
    </div>
    
    <div class="paper-categories">
      <span v-for="category in paper.categories" :key="category" class="category-tag">
        {{ category }}
      </span>
    </div>
    
    <div class="paper-abstract">
      <p>{{ truncatedSummary }}</p>
      <button 
        v-if="paper.summary && paper.summary.length > 200" 
        @click="toggleExpanded" 
        class="expand-btn"
      >
        {{ isExpanded ? 'Show Less' : 'Show More' }}
      </button>
    </div>
    
    <div class="paper-actions">
      <a :href="paper.arxiv_url" target="_blank" class="action-link">
        <svg class="action-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z" />
        </svg>
        View Original
      </a>
      <button @click="handleDownload" :disabled="isDownloading" class="download-btn">
        <svg v-if="isDownloading" class="loading-icon" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
            <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
            <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
          </circle>
        </svg>
        <svg v-else class="action-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z" />
        </svg>
        {{ isDownloading ? 'Downloading...' : 'Download PDF' }}
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Paper } from '@/types'

// Props
interface Props {
  paper: Paper
  downloading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  downloading: false
})

// Emits
interface Emits {
  download: [paper: Paper]
}

const emit = defineEmits<Emits>()

// Reactive data
const isExpanded = ref(false)

// Computed properties
const formattedAuthors = computed(() => {
  if (!props.paper.authors || props.paper.authors.length === 0) {
    return 'Unknown Author'
  }
  
  if (props.paper.authors.length <= 3) {
    return props.paper.authors.join(', ')
  }
  
  return `${props.paper.authors.slice(0, 3).join(', ')} et al.`
})

const formattedDate = computed(() => {
  if (!props.paper.published) return 'Unknown Date'
  
  try {
    return new Date(props.paper.published).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return 'Unknown Date'
  }
})

const truncatedSummary = computed(() => {
  if (!props.paper.summary) return 'No summary available'
  
  if (isExpanded.value || props.paper.summary.length <= 200) {
    return props.paper.summary
  }
  
  return props.paper.summary.substring(0, 200) + '...'
})

const isDownloading = computed(() => {
  return props.downloading
})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const handleDownload = () => {
  emit('download', props.paper)
}
</script>

<style scoped>
.paper-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  height: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.paper-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.paper-header {
  margin-bottom: 1rem;
}

.paper-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.6rem;
}

.paper-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.9rem;
}

.meta-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.authors {
  line-height: 1.3;
}

.publish-date {
  font-weight: 500;
}

.paper-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.category-tag {
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.paper-abstract {
  flex: 1;
  margin-bottom: 1.5rem;
}

.paper-abstract p {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.expand-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  transition: color 0.2s ease;
}

.expand-btn:hover {
  color: #764ba2;
}

.paper-actions {
  display: flex;
  gap: 1rem;
  margin-top: auto;
}

.action-link,
.download-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  flex: 1;
  justify-content: center;
}

.action-link {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.action-link:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

.download-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  cursor: pointer;
}

.download-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.download-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-icon {
  width: 1rem;
  height: 1rem;
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

/* Responsive Design */
@media (max-width: 768px) {
  .paper-card {
    padding: 1rem;
  }
  
  .paper-title {
    font-size: 1.1rem;
  }
  
  .paper-actions {
    flex-direction: column;
  }
  
  .action-link,
  .download-btn {
    padding: 0.75rem 1rem;
  }
  
  .meta-item {
    font-size: 0.8rem;
  }
  
  .category-tag {
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
  }
}

@media (max-width: 480px) {
  .paper-meta {
    gap: 0.25rem;
  }
  
  .meta-item {
    flex-wrap: wrap;
  }
  
  .authors {
    word-break: break-word;
  }
}
</style>