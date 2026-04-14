<template>
  <div class="chart-display">
    <div class="chart-header">
      <div class="chart-title">
        <h3>{{ title }}</h3>
        <p class="chart-subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-controls">
        <el-select v-model="chartType" @change="updateChart" style="width: 120px" size="small">
          <el-option label="柱状图" value="bar" />
          <el-option label="饼图" value="pie" />
          <el-option label="折线图" value="line" />
          <el-option label="散点图" value="scatter" />
        </el-select>
        <el-button type="primary" size="small" @click="exportChart">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
        <el-button type="default" size="small" @click="refreshChart">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div class="chart-container" :style="{ height: chartHeight + 'px' }">
      <div ref="chartRef" class="chart-content"></div>

      <!-- 数据加载状态 -->
      <div v-if="loading" class="chart-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>正在加载图表数据...</p>
      </div>

      <!-- 无数据状态 -->
      <div v-else-if="!hasData" class="chart-empty">
        <el-empty description="暂无数据" />
      </div>
    </div>

    <!-- 图表说明 -->
    <div class="chart-legend" v-if="showLegend && hasData">
      <div class="legend-item" v-for="(item, index) in legendData" :key="index">
        <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
        <span class="legend-text">{{ item.name }} ({{ item.value }})</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="chart-table" v-if="showTable && hasData">
      <el-table :data="tableData" size="small" border>
        <el-table-column
          v-for="column in tableColumns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
          :align="column.align || 'center'"
          :formatter="column.formatter"
        />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '数据图表',
  },
  subtitle: {
    type: String,
    default: '',
  },
  chartType: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'pie', 'line', 'scatter'].includes(value),
  },
  data: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  height: {
    type: Number,
    default: 400,
  },
  showLegend: {
    type: Boolean,
    default: true,
  },
  showTable: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  colors: {
    type: Array,
    default: () => ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399'],
  },
})

// Emits
const emit = defineEmits(['chart-ready', 'chart-click', 'export-chart'])

// Reactive data
const chartRef = ref(null)
const chartInstance = ref(null)
const chartType = ref(props.chartType)
const chartHeight = ref(props.height)

// Computed properties
const hasData = computed(() => {
  return Array.isArray(props.data) && props.data.length > 0
})

const legendData = computed(() => {
  if (!hasData.value) return []

  switch (chartType.value) {
    case 'pie':
      return props.data.map((item, index) => ({
        name: item.name,
        value: item.value,
        color: props.colors[index % props.colors.length],
      }))
    case 'bar':
    case 'line':
    default:
      return props.data.map((item, index) => ({
        name: item.name || `系列${index + 1}`,
        value: Array.isArray(item.data) ? item.data.reduce((sum, val) => sum + val, 0) : item.value,
        color: props.colors[index % props.colors.length],
      }))
  }
})

const tableData = computed(() => {
  if (!hasData.value) return []

  switch (chartType.value) {
    case 'pie':
      return props.data.map((item, index) => ({
        序号: index + 1,
        名称: item.name,
        数值: item.value,
        百分比: `${((item.value / props.data.reduce((sum, i) => sum + i.value, 0)) * 100).toFixed(2)}%`,
      }))
    case 'bar':
    case 'line':
    default:
      const maxLength = Math.max(...props.data.map((item) => item.data?.length || 0))
      const result = []
      for (let i = 0; i < maxLength; i++) {
        const row = { 序号: i + 1 }
        props.data.forEach((series) => {
          row[series.name] = series.data?.[i] || 0
        })
        result.push(row)
      }
      return result
  }
})

const tableColumns = computed(() => {
  if (!hasData.value) return []

  switch (chartType.value) {
    case 'pie':
      return [
        { prop: '序号', label: '序号', width: 60 },
        { prop: '名称', label: '名称', width: 120 },
        { prop: '数值', label: '数值', width: 100 },
        { prop: '百分比', label: '百分比', width: 100 },
      ]
    case 'bar':
    case 'line':
    default:
      const columns = [{ prop: '序号', label: '序号', width: 60 }]
      props.data.forEach((series) => {
        columns.push({
          prop: series.name,
          label: series.name,
          width: 100,
          formatter: (row) =>
            typeof row[series.name] === 'number'
              ? row[series.name].toLocaleString()
              : row[series.name],
        })
      })
      return columns
  }
})

// Chart configuration
const getChartOption = () => {
  const baseOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (chartType.value === 'pie') {
          return `${params.name}: ${params.value} (${params.percent}%)`
        }
        return `${params.seriesName || ''}<br/>${params.name}: ${params.value}`
      },
    },
    legend: {
      show: props.showLegend,
      top: 'bottom',
    },
    color: props.colors,
    animationDuration: 1000,
    animationEasing: 'cubicOut',
  }

  switch (chartType.value) {
    case 'pie':
      return {
        ...baseOption,
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '50%'],
            data: props.data,
            label: {
              show: true,
              formatter: '{b}: {c} ({d}%)',
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      }

    case 'line':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: props.data[0]?.categories || [],
          boundaryGap: false,
        },
        yAxis: {
          type: 'value',
        },
        series: props.data.map((series) => ({
          name: series.name,
          type: 'line',
          data: series.data,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 2,
          },
          areaStyle: {
            opacity: 0.3,
          },
        })),
      }

    case 'scatter':
      return {
        ...baseOption,
        xAxis: {
          type: 'value',
          scale: true,
        },
        yAxis: {
          type: 'value',
          scale: true,
        },
        series: props.data.map((series) => ({
          name: series.name,
          type: 'scatter',
          data: series.data,
          symbolSize: 8,
        })),
      }

    case 'bar':
    default:
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: props.data[0]?.categories || [],
          axisTick: {
            alignWithLabel: true,
          },
        },
        yAxis: {
          type: 'value',
        },
        series: props.data.map((series) => ({
          name: series.name,
          type: 'bar',
          data: series.data,
          barWidth: '60%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
          },
        })),
      }
  }
}

// Chart methods
const initChart = () => {
  if (!chartRef.value) return

  chartInstance.value = echarts.init(chartRef.value)
  updateChart()

  // 绑定点击事件
  chartInstance.value.on('click', (params) => {
    emit('chart-click', params)
  })

  // 窗口大小变化时重新渲染
  window.addEventListener('resize', resizeChart)

  emit('chart-ready', chartInstance.value)
}

const updateChart = () => {
  if (!chartInstance.value || !hasData.value) return

  try {
    const option = {
      ...getChartOption(),
      ...props.options,
    }

    chartInstance.value.setOption(option, true)
  } catch (error) {
    console.error('更新图表失败:', error)
    ElMessage.error('图表更新失败')
  }
}

const resizeChart = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

const refreshChart = () => {
  if (chartInstance.value) {
    chartInstance.value.clear()
    updateChart()
  }
}

const exportChart = () => {
  if (!chartInstance.value) return

  try {
    const dataURL = chartInstance.value.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })

    const link = document.createElement('a')
    link.download = `${props.title}_${new Date().toISOString().slice(0, 10)}.png`
    link.href = dataURL
    link.click()

    emit('export-chart', dataURL)
    ElMessage.success('图表导出成功')
  } catch (error) {
    console.error('导出图表失败:', error)
    ElMessage.error('图表导出失败')
  }
}

// Watch for data changes
watch(
  () => props.data,
  () => {
    nextTick(() => {
      updateChart()
    })
  },
  { deep: true },
)

watch(
  () => props.options,
  () => {
    nextTick(() => {
      updateChart()
    })
  },
  { deep: true },
)

watch(
  () => props.height,
  (newHeight) => {
    chartHeight.value = newHeight
    nextTick(() => {
      resizeChart()
    })
  },
)

// Lifecycle hooks
onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
    chartInstance.value = null
  }
  window.removeEventListener('resize', resizeChart)
})

// Expose methods
defineExpose({
  updateChart,
  exportChart,
  refreshChart,
  getChartInstance: () => chartInstance.value,
})
</script>

<style scoped>
.chart-display {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.chart-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chart-subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.chart-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chart-container {
  position: relative;
  width: 100%;
  min-height: 300px;
}

.chart-content {
  width: 100%;
  height: 100%;
}

.chart-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #909399;
}

.chart-loading .el-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.chart-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  display: inline-block;
}

.legend-text {
  color: #606266;
}

.chart-table {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 16px;
  }

  .chart-controls {
    justify-content: flex-start;
  }

  .chart-legend {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
