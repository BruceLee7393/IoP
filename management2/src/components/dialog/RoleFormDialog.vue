<template>
  <el-dialog
    :title="dialog.title"
    v-model="dialog.visible"
    width="600px"
    v-if="dialog.visible"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="computedRules" label-width="80px" :hide-required-asterisk="dialog.isEdit">
      <el-form-item label="角色编码" prop="role_code">
        <el-input v-model="form.role_code" placeholder="请输入角色编码" :disabled="dialog.isEdit" />
      </el-form-item>
      <el-form-item label="角色名称" prop="role_name">
        <el-input v-model="form.role_name" placeholder="请输入角色名称" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" placeholder="请输入角色描述" />
      </el-form-item>
      <!-- 只在编辑模式下显示状态字段 -->
      <el-form-item v-if="dialog.isEdit" label="状态" prop="status">
        <el-switch
          v-model="form.status"
          :active-value="'active'"
          :inactive-value="'disabled'"
          inline-prompt
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取 消</el-button>
        <el-button type="primary" @click="handleSubmit">确 定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as roleApi from '@/api/role'

// Props 定义，保持不变
const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  initialData: {
    type: Object,
    default: () => ({}),
  },
})

// Emits 定义，确保有 submitSuccess
const emit = defineEmits(['update:modelValue', 'submitSuccess'])

const formRef = ref(null)

// 内部状态管理，与您的用户表单保持一致
const dialog = reactive({
  visible: props.modelValue,
  title: props.isEdit ? '修改角色' : '添加角色',
  isEdit: props.isEdit,
})
const form = ref({})

// 表单校验规则
const baseRules = {
  role_code: [{ required: true, message: '角色编码不能为空', trigger: 'blur' }],
  role_name: [{ required: true, message: '角色名称不能为空', trigger: 'blur' }],
}

const computedRules = computed(() => {
  if (dialog.isEdit) {
    // 编辑时 role_code 通常不可改，且不展示星号，role_name 可选但建议必填
    return {
      role_code: [],
      role_name: [{ required: true, message: '角色名称不能为空', trigger: 'blur' }],
    }
  }
  return baseRules
})

// 监听器，用于在对话框打开时正确设置数据
watch(
  () => props.modelValue,
  (val) => {
    dialog.visible = val
    if (val) {
      dialog.isEdit = props.isEdit
      dialog.title = props.isEdit ? '修改角色' : '添加角色'

      // 根据是否为编辑模式设置不同的初始数据
      if (props.isEdit) {
        // 编辑模式：使用传入的数据，包含status字段
        form.value = { ...props.initialData }
      } else {
        // 添加模式：不包含status字段，让后端使用默认值
        const { status, ...dataWithoutStatus } = props.initialData || {}
        form.value = { ...dataWithoutStatus }
      }

      nextTick(() => {
        formRef.value?.clearValidate()
      })
    }
  },
)

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
}

/**
 * 提交逻辑，完全参照您的用户表单实现
 * 1. 校验表单
 * 2. 调用API (add/update)
 * 3. 显示成功消息
 * 4. 触发 submitSuccess 事件，通知 CrudTable 刷新
 * 5. 关闭对话框
 */
const handleSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) {
      // 校验失败，直接返回
      return
    }

    try {
      // 准备提交数据
      const submitData = { ...form.value }

      if (dialog.isEdit) {
        // 编辑模式：清理不需要的字段
        const cleanData = { ...submitData }
        delete cleanData.id // 移除id字段
        delete cleanData.created_at // 移除创建时间
        delete cleanData.updated_at // 移除更新时间
        delete cleanData.role_code

        console.log('修改角色提交数据:', cleanData)
        await roleApi.updateRole(form.value.id, cleanData)
        ElMessage.success('修改成功')
        // 通知全局：角色信息已更新（刷新角色选项等依赖）
        if (typeof window !== 'undefined') {
          window.dispatchEvent(
            new CustomEvent('entity-changed', { detail: { entityName: '角色', action: 'update' } })
          )
        }
      } else {
        // 添加模式：移除status字段，让后端使用默认值
        delete submitData.status
        console.log('创建角色提交数据:', submitData)
        await roleApi.createRole(submitData)
        ElMessage.success('添加成功')
        // 通知全局：角色信息已新增
        if (typeof window !== 'undefined') {
          window.dispatchEvent(
            new CustomEvent('entity-changed', { detail: { entityName: '角色', action: 'create' } })
          )
        }
      }
      // 【关键】触发此事件来刷新表格
      emit('submitSuccess')
      handleClose()
    } catch (error) {
      // API请求失败，http.js中的拦截器会自动提示错误，这里只需在控制台记录
      console.error('角色表单提交失败:', error)
    }
  })
}
</script>
