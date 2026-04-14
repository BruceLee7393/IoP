<!-- 现代化页面容器组件 -->
<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div v-if="showHeader" class="page-header">
      <div class="page-header-content">
        <div class="page-title-section">
          <div v-if="icon" class="page-icon">
            <el-icon><component :is="icon" /></el-icon>
          </div>
          <div class="page-title-content">
            <h1 class="page-title">{{ title }}</h1>
            <p v-if="description" class="page-description">{{ description }}</p>
          </div>
        </div>
        
        <div v-if="$slots.extra" class="page-extra">
          <slot name="extra" />
        </div>
      </div>
      
      <!-- 页面标签/面包屑 -->
      <div v-if="$slots.tabs || breadcrumbs.length > 0" class="page-nav">
        <div v-if="breadcrumbs.length > 0" class="page-breadcrumbs">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item 
              v-for="item in breadcrumbs" 
              :key="item.path" 
              :to="item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div v-if="$slots.tabs" class="page-tabs">
          <slot name="tabs" />
        </div>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="page-content" :class="{ 'no-header': !showHeader }">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineSlots } from 'vue'

// Props 定义
const props = defineProps({
  title: {
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
  showHeader: {
    type: Boolean,
    default: true,
  },
  breadcrumbs: {
    type: Array,
    default: () => [],
  },
})

// 插槽定义
defineSlots(['default', 'extra', 'tabs'])
</script>

<style scoped>
@import '@/styles/design-system.css';

/* ========== 页面容器 ========== */
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--content-bg);
}

/* ========== 页面头部 ========== */
.page-header {
  background: var(--card-bg);
  border-bottom: 1px solid var(--card-border);
  box-shadow: var(--shadow-sm);
}

.page-header-content {
  padding: var(--space-6) var(--space-6) var(--space-4);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-6);
}

.page-title-section {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  flex: 1;
  min-width: 0;
}

.page-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  flex-shrink: 0;
  box-shadow: var(--shadow-md);
}

.page-title-content {
  flex: 1;
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--neutral-900);
  line-height: var(--leading-tight);
  margin-bottom: var(--space-1);
}

.page-description {
  margin: 0;
  font-size: var(--text-base);
  color: var(--neutral-600);
  line-height: var(--leading-normal);
}

.page-extra {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

/* 页面导航区域 */
.page-nav {
  padding: 0 var(--space-6) var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--neutral-100);
  background: var(--neutral-50);
}

.page-breadcrumbs {
  flex: 1;
}

.page-tabs {
  flex-shrink: 0;
}

/* ========== 页面内容 ========== */
.page-content {
  flex: 1;
  padding: var(--space-6);
  overflow: auto;
  min-height: 0;
}

.page-content.no-header {
  padding-top: var(--space-4);
}

/* ========== 响应式设计 ========== */
@media (max-width: 768px) {
  .page-header-content {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-4);
    padding: var(--space-4);
  }

  .page-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .page-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .page-title {
    font-size: var(--text-2xl);
  }

  .page-nav {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-3);
    padding: var(--space-4);
  }

  .page-content {
    padding: var(--space-4);
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: var(--text-xl);
  }

  .page-description {
    font-size: var(--text-sm);
  }

  .page-content {
    padding: var(--space-3);
  }
}

/* ========== Element Plus 组件样式覆盖 ========== */
:deep(.el-breadcrumb) {
  font-size: var(--text-sm);
}

:deep(.el-breadcrumb__item) {
  color: var(--neutral-500);
}

:deep(.el-breadcrumb__item:last-child) {
  color: var(--neutral-700);
  font-weight: var(--font-medium);
}

:deep(.el-breadcrumb__separator) {
  color: var(--neutral-400);
}

/* ========== 工具类 ========== */
.page-container .card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
  padding: var(--card-padding);
  margin-bottom: var(--space-6);
  transition: var(--transition-all);
}

.page-container .card:hover {
  box-shadow: var(--card-shadow-hover);
}

.page-container .card:last-child {
  margin-bottom: 0;
}

.page-container .section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--neutral-800);
  margin: 0 0 var(--space-4) 0;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--neutral-200);
}

.page-container .section-subtitle {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--neutral-700);
  margin: 0 0 var(--space-3) 0;
}

.page-container .text-muted {
  color: var(--neutral-500);
}

.page-container .text-primary {
  color: var(--primary-600);
}

.page-container .text-success {
  color: var(--success-600);
}

.page-container .text-warning {
  color: var(--warning-600);
}

.page-container .text-danger {
  color: var(--error-600);
}
</style>
