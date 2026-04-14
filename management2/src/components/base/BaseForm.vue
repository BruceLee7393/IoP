<template>
  <el-form
    ref="formRef"
    :model="localFormData"
    :rules="rules"
    :label-width="labelWidth"
    :label-position="labelPosition"
    :size="size"
    :disabled="disabled"
    @submit.prevent
  >
    <el-row :gutter="gutter">
      <el-col v-for="field in visibleFields" :key="field.prop" :span="field.span || defaultColSpan">
        <el-form-item :label="field.label" :prop="field.prop" :required="field.required">
          <!-- Input -->
          <el-input
            v-if="field.type === 'input' || !field.type"
            v-model="localFormData[field.prop]"
            :type="field.inputType || 'text'"
            :placeholder="field.placeholder || `请输入${field.label}`"
            :disabled="field.disabled || disabled"
            :clearable="field.clearable !== false"
            :show-password="field.showPassword"
            :maxlength="field.maxlength"
            :show-word-limit="field.showWordLimit"
          />

          <!-- Textarea -->
          <el-input
            v-else-if="field.type === 'textarea'"
            v-model="localFormData[field.prop]"
            type="textarea"
            :placeholder="field.placeholder || `请输入${field.label}`"
            :disabled="field.disabled || disabled"
            :rows="field.rows || 3"
            :maxlength="field.maxlength"
            :show-word-limit="field.showWordLimit"
          />

          <!-- Number Input -->
          <el-input-number
            v-else-if="field.type === 'number'"
            v-model="localFormData[field.prop]"
            :placeholder="field.placeholder || `请输入${field.label}`"
            :disabled="field.disabled || disabled"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :precision="field.precision"
            style="width: 100%"
          />

          <!-- Select -->
          <el-select
            v-else-if="field.type === 'select'"
            v-model="localFormData[field.prop]"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :disabled="field.disabled || disabled"
            :clearable="field.clearable !== false"
            :multiple="field.multiple"
            :filterable="field.filterable"
            style="width: 100%"
            @change="(value) => updateFieldValue(field.prop, value)"
          >
            <el-option
              v-for="option in field.options"
              :key="option.value"
              :label="option.label"
              :value="option.value"
              :disabled="option.disabled"
            />
          </el-select>

          <!-- Radio Group -->
          <el-radio-group
            v-else-if="field.type === 'radio'"
            v-model="localFormData[field.prop]"
            :disabled="field.disabled || disabled"
          >
            <el-radio
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </el-radio>
          </el-radio-group>

          <!-- Checkbox Group -->
          <el-checkbox-group
            v-else-if="field.type === 'checkbox'"
            v-model="localFormData[field.prop]"
            :disabled="field.disabled || disabled"
          >
            <el-checkbox
              v-for="option in field.options"
              :key="option.value"
              :value="option.value"
              :disabled="option.disabled"
            >
              {{ option.label }}
            </el-checkbox>
          </el-checkbox-group>

          <!-- Switch -->
          <el-switch
            v-else-if="field.type === 'switch'"
            v-model="localFormData[field.prop]"
            :disabled="field.disabled || disabled"
            :active-text="field.activeText"
            :inactive-text="field.inactiveText"
          />

          <!-- Date Picker -->
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="localFormData[field.prop]"
            :type="field.dateType || 'date'"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :disabled="field.disabled || disabled"
            :clearable="field.clearable !== false"
            style="width: 100%"
          />

          <!-- Time Picker -->
          <el-time-picker
            v-else-if="field.type === 'time'"
            v-model="localFormData[field.prop]"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :disabled="field.disabled || disabled"
            :clearable="field.clearable !== false"
            style="width: 100%"
          />

          <!-- Tree Select -->
          <el-tree-select
            v-else-if="field.type === 'tree-select'"
            v-model="localFormData[field.prop]"
            :data="field.data"
            :props="field.treeProps"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :disabled="field.disabled || disabled"
            :clearable="field.clearable !== false"
            :check-strictly="field.checkStrictly"
            :filterable="field.filterable"
            style="width: 100%"
            @change="(value) => updateFieldValue(field.prop, value)"
          />

          <!-- Upload -->
          <el-upload
            v-else-if="field.type === 'upload'"
            :action="field.action"
            :headers="field.headers"
            :data="field.data"
            :name="field.name || 'file'"
            :accept="field.accept"
            :multiple="field.multiple"
            :limit="field.limit"
            :file-list="localFormData[field.prop] || []"
            :disabled="field.disabled || disabled"
            @change="(file, fileList) => handleFileChange(field.prop, file, fileList)"
          >
            <el-button :disabled="field.disabled || disabled">
              {{ field.uploadText || '选择文件' }}
            </el-button>
          </el-upload>

          <!-- Custom Slot -->
          <slot
            v-else-if="field.type === 'slot'"
            :name="`field-${field.prop}`"
            :field="field"
            :value="localFormData[field.prop]"
            :disabled="field.disabled || disabled"
            :update-value="(val) => updateFieldValue(field.prop, val)"
          />
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'

// Props定义
const props = defineProps({
  formData: {
    type: Object,
    required: true,
  },
  fields: {
    type: Array,
    required: true,
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
  labelWidth: {
    type: String,
    default: '100px',
  },
  labelPosition: {
    type: String,
    default: 'right',
  },
  size: {
    type: String,
    default: 'default',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  gutter: {
    type: Number,
    default: 20,
  },
  defaultColSpan: {
    type: Number,
    default: 24,
  },
})

// Emits定义
const emit = defineEmits(['update:formData', 'field-change'])

// 响应式数据
const formRef = ref(null)

// 创建一个本地的、可修改的副本，以避免直接修改prop
const localFormData = reactive({})

// 监听props.formData的变化，从父组件同步到本地副本
watch(
  () => props.formData,
  (newVal) => {
    // 先清空本地对象的所有键
    Object.keys(localFormData).forEach((key) => {
      delete localFormData[key]
    })
    // 然后将新数据赋值过来
    Object.assign(localFormData, newVal)
  },
  { immediate: true, deep: true },
)

// 监听本地副本的变化，同步回父组件
watch(
  localFormData,
  (newVal) => {
    emit('update:formData', newVal)
  },
  { deep: true },
)

// 计算属性
const visibleFields = computed(() => {
  return props.fields.filter((field) => !field.hidden)
})

// 方法
const updateFieldValue = (prop, value) => {
  localFormData[prop] = value
  emit('field-change', { prop, value })
}

const handleFileChange = (prop, file, fileList) => {
  updateFieldValue(prop, fileList)
}

// 暴露方法给父组件
defineExpose({
  validate: () => formRef.value?.validate(),
  validateField: (props) => formRef.value?.validateField(props),
  resetFields: () => {
    if (formRef.value) {
      formRef.value.resetFields()
      // resetFields 可能不会触发 watch，需要手动emit
      emit('update:formData', localFormData)
    }
  },
  clearValidate: (props) => formRef.value?.clearValidate(props),
})
</script>

<style scoped>
/* 表单样式可以根据需要自定义 */
</style>
