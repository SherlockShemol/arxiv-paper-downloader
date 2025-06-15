<template>
  <div class="statistics-page">
    <!-- 时间范围选择 -->
    <el-card class="time-range-card" shadow="hover">
      <div class="time-range-selector">
        <div class="selector-left">
          <el-icon><DataAnalysis /></el-icon>
          <span class="title">统计分析</span>
        </div>
        
        <div class="selector-right">
          <el-radio-group v-model="timeRange" @change="updateCharts">
            <el-radio-button label="7d">最近7天</el-radio-button>
            <el-radio-button label="30d">最近30天</el-radio-button>
            <el-radio-button label="90d">最近90天</el-radio-button>
            <el-radio-button label="1y">最近1年</el-radio-button>
          </el-radio-group>
          
          <el-date-picker
            v-model="customDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleCustomDateChange"
            style="margin-left: 15px;"
          />
          
          <el-button @click="exportData" style="margin-left: 15px;">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 概览统计卡片 -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <el-card class="overview-card" shadow="hover">
          <div class="overview-content">
            <div class="overview-icon">
              <el-icon class="icon-downloads"><Download /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-number">{{ overviewStats.totalDownloads }}</div>
              <div class="overview-label">总下载量</div>
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
              <div class="overview-label">成功率</div>
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
              <div class="overview-label">平均速度</div>
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
              <div class="overview-label">存储使用</div>
              <div class="overview-trend" :class="overviewStats.sizeTrend > 0 ? 'positive' : 'negative'">
                <el-icon><CaretTop v-if="overviewStats.sizeTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overviewStats.sizeTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 下载趋势图 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>下载趋势</span>
              <el-button-group>
                <el-button :type="downloadChartType === 'line' ? 'primary' : ''" size="small" @click="downloadChartType = 'line'">
                  线图
                </el-button>
                <el-button :type="downloadChartType === 'bar' ? 'primary' : ''" size="small" @click="downloadChartType = 'bar'">
                  柱图
                </el-button>
              </el-button-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="downloadTrendOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 成功率统计 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>下载状态分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="statusDistributionOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- 学科分类统计 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataBoard /></el-icon>
              <span>学科分类统计</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="categoryStatsOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
      
      <!-- 下载速度分布 -->
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Histogram /></el-icon>
              <span>下载速度分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="speedDistributionOption" :autoresize="true" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="data-table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><List /></el-icon>
          <span>详细数据</span>
          <el-button @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="detailData" stripe style="width: 100%">
        <el-table-column label="日期" prop="date" width="120" />
        <el-table-column label="下载数量" prop="downloads" width="100" />
        <el-table-column label="成功数量" prop="success" width="100" />
        <el-table-column label="失败数量" prop="failed" width="100" />
        <el-table-column label="成功率" width="100">
          <template #default="{ row }">
            {{ ((row.success / row.downloads) * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="平均速度" prop="avgSpeed" width="120" />
        <el-table-column label="总大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.totalSize) }}
          </template>
        </el-table-column>
        <el-table-column label="最热门分类" prop="topCategory" width="120" />
        <el-table-column label="备注" prop="notes" min-width="200" />
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

// 注册 ECharts 组件
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

// 状态变量
const timeRange = ref('30d')
const customDateRange = ref([])
const downloadChartType = ref('line')
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)

// 概览统计数据
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

// 详细数据
const detailData = ref([])

// 下载趋势图配置
const downloadTrendOption = computed(() => {
  const dates = []
  const downloads = []
  const success = []
  
  // 生成模拟数据
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
      data: ['总下载', '成功下载']
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
        name: '总下载',
        type: downloadChartType.value,
        data: downloads,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '成功下载',
        type: downloadChartType.value,
        data: success,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
})

// 状态分布图配置
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
        name: '下载状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 890, name: '成功', itemStyle: { color: '#67C23A' } },
          { value: 234, name: '失败', itemStyle: { color: '#F56C6C' } },
          { value: 110, name: '进行中', itemStyle: { color: '#409EFF' } }
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

// 学科分类统计配置
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
      data: ['计算机科学', '数学', '物理', '统计学', '生物学', '经济学']
    },
    series: [
      {
        name: '下载数量',
        type: 'bar',
        data: [520, 332, 301, 234, 190, 130],
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
})

// 下载速度分布配置
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
        name: '下载次数',
        type: 'bar',
        data: [45, 123, 234, 345, 189, 67],
        itemStyle: {
          color: '#E6A23C'
        }
      }
    ]
  }
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 更新图表
const updateCharts = () => {
  ElMessage.success(`已切换到${timeRange.value === '7d' ? '最近7天' : timeRange.value === '30d' ? '最近30天' : timeRange.value === '90d' ? '最近90天' : '最近1年'}的数据`)
  loadDetailData()
}

// 处理自定义日期范围变化
const handleCustomDateChange = (dates) => {
  if (dates && dates.length === 2) {
    timeRange.value = 'custom'
    ElMessage.success(`已切换到自定义时间范围: ${dates[0]} 至 ${dates[1]}`)
    loadDetailData()
  }
}

// 导出数据
const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

// 刷新数据
const refreshData = () => {
  loadDetailData()
  ElMessage.success('数据已刷新')
}

// 加载详细数据
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
      notes: i === 0 ? '今日数据' : i === 1 ? '昨日数据' : ''
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

/* 暗色主题适配 */
:global(.dark) .overview-number {
  color: #e5eaf3;
}

:global(.dark) .selector-left .title {
  color: #e5eaf3;
}
</style>