<!-- 现代化统计卡片组件 -->
<template>
  <div class="stat-card" :class="[`stat-card--${variant}`, { 'stat-card--loading': loading }]">
    <div v-if="loading" class="stat-card-loading">
      <el-skeleton animated>
        <template #template>
          <div class="stat-skeleton">
            <el-skeleton-item variant="circle" style="width: 48px; height: 48px;" />
            <div class="stat-skeleton-content">
              <el-skeleton-item variant="text" style="width: 60%; height: 20px;" />
              <el-skeleton-item variant="text" style="width: 40%; height: 16px; margin-top: 8px;" />
            </div>
          </div>
        </template>
      </el-skeleton>
    </div>
    
    <div v-else class="stat-card-content">
      <!-- 图标区域 -->
      <div class="stat-icon" :class="`stat-icon--${variant}`">
        <el-icon v-if="icon"><component :is="icon" /></el-icon>
        <div v-else class="stat-icon-placeholder">
          <el-icon><TrendCharts /></el-icon>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div class="stat-content">
        <div class="stat-header">
          <h3 class="stat-title">{{ title }}</h3>
          <div v-if="trend !== null" class="stat-trend" :class="trendClass">
            <el-icon><component :is="trendIcon" /></el-icon>
            <span class="stat-trend-value">{{ Math.abs(trend) }}%</span>
          </div>
        </div>
        
        <div class="stat-value-section">
          <div class="stat-value">{{ formattedValue }}</div>
          <div v-if="subtitle" class="stat-subtitle">{{ subtitle }}</div>
        </div>
        
        <div v-if="description" class="stat-description">
          {{ description }}
        </div>
      </div>
    </div>
    
    <!-- 底部操作区域 -->
    <div v-if="$slots.footer" class="stat-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendCharts, ArrowUp, ArrowDown } from '@element-plus/icons-vue'

// Props 定义
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  icon: {
    type: [String, Object],
    default: null,
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger'].includes(value),
  },
  trend: {
    type: Number,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  prefix: {
    type: String,
    default: '',
  },
  suffix: {
    type: String,
    default: '',
  },
  precision: {
    type: Number,
    default: 0,
  },
})

// 计算属性
const formattedValue = computed(() => {
  let value = props.value
  
  if (typeof value === 'number') {
    if (props.precision > 0) {
      value = value.toFixed(props.precision)
    }
    // 添加千分位分隔符
    value = value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  }
  
  return `${props.prefix}${value}${props.suffix}`
})

const trendClass = computed(() => {
  if (props.trend === null) return ''
  return props.trend >= 0 ? 'stat-trend--up' : 'stat-trend--down'
})

const trendIcon = computed(() => {
  if (props.trend === null) return null
  return props.trend >= 0 ? ArrowUp : ArrowDown
})
</script>

<style scoped>
@import '@/styles/design-system.css';

/* ========== 统计卡片基础样式 ========== */
.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  transition: var(--transition-all);
  overflow: hidden;
  position: relative;
}

.stat-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.stat-card--loading {
  pointer-events: none;
}

/* ========== 卡片变体样式 ========== */
.stat-card--primary {
  border-left: 4px solid var(--primary-500);
}

.stat-card--success {
  border-left: 4px solid var(--success-500);
}

.stat-card--warning {
  border-left: 4px solid var(--warning-500);
}

.stat-card--danger {
  border-left: 4px solid var(--error-500);
}

/* ========== 加载状态 ========== */
.stat-card-loading {
  padding: var(--space-6);
}

.stat-skeleton {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.stat-skeleton-content {
  flex: 1;
}

/* ========== 卡片内容 ========== */
.stat-card-content {
  padding: var(--space-6);
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
}

/* ========== 图标区域 ========== */
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.stat-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.1;
  border-radius: inherit;
}

.stat-icon--default {
  background: var(--neutral-100);
  color: var(--neutral-600);
}

.stat-icon--default::before {
  background: var(--neutral-500);
}

.stat-icon--primary {
  background: var(--primary-100);
  color: var(--primary-600);
}

.stat-icon--primary::before {
  background: var(--primary-500);
}

.stat-icon--success {
  background: var(--success-100);
  color: var(--success-600);
}

.stat-icon--success::before {
  background: var(--success-500);
}

.stat-icon--warning {
  background: var(--warning-100);
  color: var(--warning-600);
}

.stat-icon--warning::before {
  background: var(--warning-500);
}

.stat-icon--danger {
  background: var(--error-100);
  color: var(--error-600);
}

.stat-icon--danger::before {
  background: var(--error-500);
}

.stat-icon-placeholder {
  opacity: 0.6;
}

/* ========== 内容区域 ========== */
.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.stat-title {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--neutral-600);
  line-height: var(--leading-tight);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
}

.stat-trend--up {
  background: var(--success-100);
  color: var(--success-700);
}

.stat-trend--down {
  background: var(--error-100);
  color: var(--error-700);
}

.stat-trend-value {
  line-height: 1;
}

.stat-value-section {
  margin-bottom: var(--space-2);
}

.stat-value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-1);
}

.stat-subtitle {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  line-height: var(--leading-normal);
}

.stat-description {
  font-size: var(--text-xs);
  color: var(--neutral-500);
  line-height: var(--leading-relaxed);
}

/* ========== 底部区域 ========== */
.stat-footer {
  padding: var(--space-3) var(--space-6);
  border-top: 1px solid var(--neutral-100);
  background: var(--neutral-50);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .stat-card-content {
    padding: var(--space-4);
    gap: var(--space-3);
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .stat-value {
    font-size: var(--text-2xl);
  }

  .stat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }

  .stat-footer {
    padding: var(--space-3) var(--space-4);
  }
}

/* ========== 动画效果 ========== */
@keyframes stat-value-animate {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-value {
  animation: stat-value-animate 0.3s ease-out;
}

/* ========== 特殊效果 ========== */
.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-400), transparent);
  opacity: 0;
  transition: var(--transition-base);
}

.stat-card:hover::after {
  opacity: 1;
}

/* ========== 工具类 ========== */
.stat-card.compact .stat-card-content {
  padding: var(--space-4);
}

.stat-card.compact .stat-icon {
  width: 36px;
  height: 36px;
  font-size: 18px;
}

.stat-card.compact .stat-value {
  font-size: var(--text-2xl);
}
</style>
