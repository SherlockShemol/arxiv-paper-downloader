<template>
  <div class="statistics-page">
    <!-- Time range selection -->
    <el-card class="time-range-card" shadow="hover">
      <div class="time-range-selector">
        <div class="selector-left">
          <el-icon><DataAnalysis /></el-icon>
          <span class="title">Statistical Analysis</span>
        </div>
        
        <div class="selector-right">
          <el-radio-group v-model="timeRange" @change="updateCharts">
            <el-radio-button label="7d">Last 7 Days</el-radio-button>
            <el-radio-button label="30d">Last 30 Days</el-radio-button>
            <el-radio-button label="90d">Last 90 Days</el-radio-button>
            <el-radio-button label="1y">Last 1 Year</el-radio-button>
          </el-radio-group>
          
          <el-date-picker
            v-model="customDateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleCustomDateChange"
            style="margin-left: 15px;"
          />
          
          <el-button @click="exportData" style="margin-left: 15px;">
            <el-icon><Download /></el-icon>
            Export Data
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Statistics cards -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card class="overview-card" shadow="hover">
          <div class="overview-content">
            <div class="overview-icon">
              <el-icon class="icon-downloads"><Download /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-number">{{ overviewStats.totalDownloads }}</div>
              <div class="overview-label">Total Downloads</div>
              <div class="overview-trend" :class="overviewStats.downloadsTrend > 0 ? 'positive' : 'negative'">
                <el-icon><CaretTop v-if="overviewStats.downloadsTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overviewStats.downloadsTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card" shadow="hover">
          <div class="overview-content">
            <div class="overview-icon">
              <el-icon class="icon-success"><CircleCheck /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-number">{{ overviewStats.successRate }}%</div>
              <div class="overview-label">Success Rate</div>
              <div class="overview-trend" :class="overviewStats.successTrend > 0 ? 'positive' : 'negative'">
                <el-icon><CaretTop v-if="overviewStats.successTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overviewStats.successTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card" shadow="hover">
          <div class="overview-content">
            <div class="overview-icon">
              <el-icon class="icon-speed"><Timer /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-number">{{ overviewStats.avgSpeed }}</div>
              <div class="overview-label">Average Speed</div>
              <div class="overview-trend" :class="overviewStats.speedTrend > 0 ? 'positive' : 'negative'">
                <el-icon><CaretTop v-if="overviewStats.speedTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overviewStats.speedTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="overview-card" shadow="hover">
          <div class="overview-content">
            <div class="overview-icon">
              <el-icon class="icon-storage"><FolderOpened /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-number">{{ formatFileSize(overviewStats.totalSize) }}</div>
              <div class="overview-label">Storage Usage</div>
              <div class="overview-trend" :class="overviewStats.sizeTrend > 0 ? 'positive' : 'negative'">
                <el-icon><CaretTop v-if="overviewStats.sizeTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overviewStats.sizeTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart area -->
    <el-row :gutter="20" class="charts-row">
      <!-- Download trend chart -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>Download Trends</span>
              <el-button-group>
                <el-button :type="downloadChartType === 'line' ? 'primary' : ''" size="small" @click="downloadChartType = 'line'">
                  Line Chart
                </el-button>
                <el-button :type="downloadChartType === 'bar' ? 'primary' : ''" size="small" @click="downloadChartType = 'bar'">
                  Bar Chart
                </el-button>
              </el-button-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="downloadTrendOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
      
      <!-- Success rate statistics -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>Download Status Distribution</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="statusDistributionOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- Subject classification statistics -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataBoard /></el-icon>
              <span>Subject Classification Statistics</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="categoryStatsOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
      
      <!-- Download speed distribution -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Histogram /></el-icon>
              <span>Download Speed Distribution</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="speedDistributionOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Detailed statistics table -->
    <el-card class="data-table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><List /></el-icon>
          <span>Detailed Data</span>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      
      <el-table :data="detailData" stripe style="width: 100%">
        <el-table-column label="Date" prop="date" width="120" />
        <el-table-column label="Downloads" prop="downloads" width="100" />
        <el-table-column label="Success" prop="success" width="100" />
        <el-table-column label="Failed" prop="failed" width="100" />
        <el-table-column label="Success Rate" width="100">
          <template #default="{ row }">
            {{ ((row.success / row.downloads) * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="Avg Speed" prop="avgSpeed" width="120" />
        <el-table-column label="Total Size" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.totalSize) }}
          </template>
        </el-table-column>
        <el-table-column label="Top Category" prop="topCategory" width="120" />
        <el-table-column label="Notes" prop="notes" min-width="200" />
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

// Register ECharts components
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// State variables
const timeRange = ref('30d')
const customDateRange = ref([])
const downloadChartType = ref('line')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

// Overview statistics data
const overviewStats = reactive({
  totalDownloads: 1234,
  downloadsTrend: 12.5,
  successRate: 94.2,
  successTrend: 2.1,
  avgSpeed: '2.3 MB/s',
  speedTrend: -5.2,
  totalSize: 15728640000, // 15GB
  sizeTrend: 18.7
})

// Detailed data
const detailData = ref([])

// Download trend chart configuration
const downloadTrendOption = computed(() => {
  const dates = []
  const downloads = []
  const success = []
  
  // Generate mock data
  for (let i = 29; i >= 0; i--) {
    const date = dayjs().subtract(i, 'day')
    dates.push(date.format('MM-DD'))
    downloads.push(Math.floor(Math.random() * 50) + 10)
    success.push(Math.floor(Math.random() * 45) + 8)
  }
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['Total Downloads', 'Successful Downloads']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'Total Downloads',
        type: downloadChartType.value,
        data: downloads,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: 'Successful Downloads',
        type: downloadChartType.value,
        data: success,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
})

// Status distribution chart configuration
const statusDistributionOption = computed(() => {
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: 'Download Status',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 890, name: 'Success', itemStyle: { color: '#67C23A' } },
          { value: 234, name: 'Failed', itemStyle: { color: '#F56C6C' } },
          { value: 110, name: 'In Progress', itemStyle: { color: '#409EFF' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
})

// Subject classification statistics configuration
const categoryStatsOption = computed(() => {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: ['Computer Science', 'Mathematics', 'Physics', 'Statistics', 'Biology', 'Economics']
    },
    series: [
      {
        name: 'Download Count',
        type: 'bar',
        data: [520, 332, 301, 234, 190, 130],
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
})

// Download speed distribution configuration
const speedDistributionOption = computed(() => {
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['0-0.5MB/s', '0.5-1MB/s', '1-2MB/s', '2-5MB/s', '5-10MB/s', '>10MB/s']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: 'Download Count',
        type: 'bar',
        data: [45, 123, 234, 345, 189, 67],
        itemStyle: {
          color: '#E6A23C'
        }
      }
    ]
  }
})

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Update charts
const updateCharts = () => {
  ElMessage.success(`Switched to ${timeRange.value === '7d' ? 'last 7 days' : timeRange.value === '30d' ? 'last 30 days' : timeRange.value === '90d' ? 'last 90 days' : 'last year'} data`)
  loadDetailData()
}

// Handle custom date range changes
const handleCustomDateChange = (dates) => {
  if (dates && dates.length === 2) {
    timeRange.value = 'custom'
    ElMessage.success(`Switched to custom time range: ${dates[0]} to ${dates[1]}`)
    loadDetailData()
  }
}

// Export data
const exportData = () => {
  ElMessage.success('Data export feature under development...')
}

// Refresh data
const refreshData = () => {
  loadDetailData()
  ElMessage.success('Data refreshed')
}

// Load detailed data
const loadDetailData = () => {
  const data = []
  for (let i = 29; i >= 0; i--) {
    const date = dayjs().subtract(i, 'day')
    const downloads = Math.floor(Math.random() * 50) + 10
    const success = Math.floor(Math.random() * downloads * 0.9) + Math.floor(downloads * 0.8)
    const failed = downloads - success
    
    data.push({
      date: date.format('YYYY-MM-DD'),
      downloads: downloads,
      success: success,
      failed: failed,
      avgSpeed: (Math.random() * 5 + 0.5).toFixed(1) + ' MB/s',
      totalSize: Math.floor(Math.random() * 1000000000) + 100000000,
      topCategory: ['cs.LG', 'math.ST', 'physics.AI', 'stat.ML'][Math.floor(Math.random() * 4)],
      notes: i === 0 ? 'Today\'s data' : i === 1 ? 'Yesterday\'s data' : ''
    })
  }
  
  detailData.value = data
  totalRecords.value = data.length
}

onMounted(() => {
  loadDetailData()
})
</script>

<style scoped>
.statistics-page {
  max-width: 1400px;
  margin: 0 auto;
}

.time-range-card {
  margin-bottom: 20px;
}

.time-range-selector {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-left {
  display: flex;
  align-items: center;
}

.selector-left .title {
  margin-left: 8px;
  font-size: 18px;
  font-weight: bold;
}

.selector-right {
  display: flex;
  align-items: center;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  height: 120px;
}

.overview-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.overview-icon {
  font-size: 40px;
  margin-right: 20px;
}

.icon-downloads { color: #409EFF; }
.icon-success { color: #67C23A; }
.icon-speed { color: #E6A23C; }
.icon-storage { color: #F56C6C; }

.overview-info {
  flex: 1;
}

.overview-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.overview-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.overview-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
}

.overview-trend.positive {
  color: #67C23A;
}

.overview-trend.negative {
  color: #F56C6C;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
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

.chart-container {
  padding: 10px 0;
}

.data-table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* Dark theme adaptation */
:global(.dark) .overview-number {
  color: #e5eaf3;
}

:global(.dark) .selector-left .title {
  color: #e5eaf3;
}
</style>