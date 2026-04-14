<template>
  <el-dialog
    :title="dialog.title"
    v-model="dialog.visible"
    width="600px"
    v-if="dialog.visible"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="formRules" label-width="80px" :hide-required-asterisk="dialog.isEdit">
      <el-form-item label="账号" prop="account">
        <el-input v-model="form.account" placeholder="请输入账号" :disabled="dialog.isEdit" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="form.password"
          type="password"
          show-password
          :placeholder="dialog.isEdit ? '留空则不修改密码' : '请输入密码'"
        />
      </el-form-item>
      <el-form-item label="用户姓名" prop="full_name">
        <el-input v-model="form.full_name" placeholder="请输入用户姓名" />
      </el-form-item>
      <el-form-item label="性别" prop="gender">
        <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%" clearable>
          <el-option
            v-for="option in genderOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="角色" prop="role_id">
        <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%" clearable>
          <el-option
            v-for="role in roleOptions.filter((r) => r.id != null)"
            :key="role.id"
            :label="role.role_name"
            :value="role.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="联系方式" prop="contact_info">
        <el-input v-model="form.contact_info" placeholder="请输入联系方式" />
      </el-form-item>
      <el-form-item label="地址" prop="address">
        <el-input v-model="form.address" type="textarea" placeholder="请输入地址" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取 消</el-button>
      <el-button type="primary" @click="handleSubmit">确 定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'

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
  roleOptions: {
    type: Array,
    default: () => [],
  },

  // 性别选项 prop
  genderOptions: {
    type: Array,
    default: () => [],
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'submitSuccess'])

const formRef = ref(null)
const dialog = reactive({
  visible: props.modelValue,
  title: props.isEdit ? '修改用户' : '添加用户',
  isEdit: props.isEdit,
})
const form = ref({})

const formRules = reactive({
  account: [{ required: true, message: '账号不能为空', trigger: 'blur' }],
  password: [{ required: !props.isEdit, message: '密码不能为空', trigger: 'blur' }],
  full_name: [{ required: true, message: '用户姓名不能为空', trigger: 'blur' }],

})

// 数据转换函数：处理编辑时的嵌套对象
const transformUserData = (userData) => {
  if (!userData) return {}

  console.log('UserFormDialog - 原始数据:', userData)

  // 创建转换后的数据副本
  const transformedData = { ...userData }

  // 处理角色数据：如果是对象，提取ID
  if (userData.role && typeof userData.role === 'object') {
    transformedData.role_id = userData.role.id
    console.log('UserFormDialog - 转换角色对象为ID:', userData.role.id)
  } else if (userData.role_id) {
    // 如果已经是ID格式，保持不变
    transformedData.role_id = userData.role_id
  }



  console.log('UserFormDialog - 转换后的数据:', transformedData)
  return transformedData
}

// 监听props变化，更新内部状态
watch(
  () => props.modelValue,
  (val) => {
    dialog.visible = val
    if (val) {
      // 更新组件内部的响应式状态
      dialog.isEdit = props.isEdit
      dialog.title = props.isEdit ? '修改用户' : '添加用户'

      // 转换数据格式，确保角色字段是ID而不是对象
      form.value = transformUserData(props.initialData)

      // 动态更新密码验证规则
      formRules.password = [{ required: !props.isEdit, message: '密码不能为空', trigger: 'blur' }]

      console.log('UserFormDialog opened with transformed data:', form.value)
      console.log('UserFormDialog isEdit:', props.isEdit)
      nextTick(() => {
        formRef.value?.clearValidate()
      })
    }
  },
)

const handleClose = () => {
  emit('update:modelValue', false)
}

const handleSubmit = () => {
  formRef.value.validate((valid) => {
    if (!valid) {
      console.log('UserFormDialog validation failed')
      return
    }

    // 准备提交数据，确保只传递ID值
    const submitData = { ...form.value }

    // 确保角色字段是ID格式
    if (submitData.role_id) {
      // 如果role_id存在，确保它是字符串ID
      submitData.role_id = String(submitData.role_id)
    }

    // 移除可能存在的嵌套对象字段和不存在的字段
    delete submitData.role
    delete submitData.role_name
    delete submitData.created_at



    console.log('UserFormDialog submitting cleaned form data:', submitData)
    console.log('UserFormDialog isEdit:', dialog.isEdit)

    // 发送提交事件给父组件处理
    emit('submit', submitData)
  })
}
</script>
