<template>
  <el-card class="query-card" shadow="never">
    <el-form :model="localQueryParams" ref="queryFormRef" label-width="85px">
      <el-row :gutter="20" class="query-row-flex">
        <template v-for="field in visibleFields" :key="field.prop">
          <el-col :span="field.span || 6">
            <el-form-item :label="field.label" :prop="field.prop">
              <el-input
                v-if="field.type === 'input' || !field.type"
                v-model="localQueryParams[field.prop]"
                :placeholder="field.placeholder || `请输入${field.label}`"
                clearable
                @keyup.enter="handleSearch"
              />
              <el-select
                v-else-if="field.type === 'select'"
                v-model="localQueryParams[field.prop]"
                :placeholder="field.placeholder || `请选择${field.label}`"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <el-tree-select
                v-else-if="field.type === 'tree-select'"
                v-model="localQueryParams[field.prop]"
                :data="field.data"
                :props="field.props"
                :node-key="field.nodeKey"
                :check-strictly="field.checkStrictly"
                :placeholder="field.placeholder || `请选择${field.label}`"
                :clearable="field.clearable"
                :filterable="field.filterable"
                style="width: 100%"
              />
              <el-input-number
                v-else-if="field.type === 'number'"
                v-model="localQueryParams[field.prop]"
                :placeholder="field.placeholder || `请输入${field.label}`"
                :min="field.min"
                :max="field.max"
                :step="field.step"
                :precision="field.precision"
                controls-position="right"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.type === 'datetime'"
                v-model="localQueryParams[field.prop]"
                type="datetime"
                :placeholder="field.placeholder || '请选择时间'"
                :format="field.format || 'YYYY-MM-DD HH:mm:ss'"
                :value-format="field.valueFormat || 'YYYY-MM-DD HH:mm:ss'"
                :clearable="field.clearable !== false"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.type === 'datetimerange'"
                v-model="localQueryParams[field.prop]"
                type="datetimerange"
                :range-separator="field.rangeSeparator || '至'"
                :start-placeholder="field.startPlaceholder || '开始时间'"
                :end-placeholder="field.endPlaceholder || '结束时间'"
                :format="field.format || 'YYYY-MM-DD HH:mm:ss'"
                :value-format="field.valueFormat || 'YYYY-MM-DD HH:mm:ss'"
                :shortcuts="field.shortcuts"
                style="width: 100%"
              />
              <el-date-picker
                v-else-if="field.type === 'date'"
                v-model="localQueryParams[field.prop]"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </template>

        <div class="query-actions">
          <el-form-item label-width="0">
            <el-button v-if="hasAdvancedFields" type="primary" link @click="toggleAdvanced">
              {{ showAdvanced ? '收起筛选' : '更多筛选' }}
              <el-icon class="el-icon--right">
                <ArrowUp v-if="showAdvanced" />
                <ArrowDown v-else />
              </el-icon>
            </el-button>
            <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </el-form-item>
        </div>
      </el-row>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { ArrowDown, ArrowUp, Search, Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  queryParams: { type: Object, required: true },
  fields: { type: Array, required: true },
  initialQueryParams: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['search', 'reset'])
const queryFormRef = ref(null)
const showAdvanced = ref(false)
const localQueryParams = reactive({})

watch(
  () => props.queryParams,
  (newVal) => {
    Object.assign(localQueryParams, newVal)
  },
  { deep: true, immediate: true },
)

const hasAdvancedFields = computed(() => props.fields.some((f) => f.advanced))
const visibleFields = computed(() => {
  if (!hasAdvancedFields.value || showAdvanced.value) {
    return props.fields
  }
  return props.fields.filter((f) => !f.advanced)
})

const toggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}
const handleSearch = () => {
  emit('search', localQueryParams)
}

const handleReset = () => {
  const initial = JSON.parse(JSON.stringify(props.initialQueryParams))
  // 清空本地查询参数
  Object.keys(localQueryParams).forEach((key) => {
    delete localQueryParams[key]
  })
  // 重新赋值初始参数
  Object.assign(localQueryParams, initial)

  emit('reset', queryFormRef.value)
  emit('search', localQueryParams)
}
</script>

<style scoped>
.query-card {
  margin-bottom: 20px;
}

/* [核心修改] 新增/修改的样式 */
.query-row-flex {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
}

.query-actions {
  margin-left: auto; /* 关键样式：自动外边距将此元素推到行尾 */
  white-space: nowrap; /* 防止按钮内部换行 */
}

:deep(.el-form-item) {
  display: flex;
  align-items: center;
  margin-bottom: 18px;
}

/* 确保按钮组里的 el-form-item 没有下边距，使其垂直对齐 */
.query-actions .el-form-item {
  margin-bottom: 0;
}
</style>
