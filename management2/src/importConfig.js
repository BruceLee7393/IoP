// 批量导入配置文件
import { h } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import * as institutionApi from '@/api/institution'
import * as deviceApi from '@/api/device'
import * as orderApi from '@/api/order'

// 订单导入配置
export const getOrderImportConfig = () => {
  const i18nStore = useI18nStore()
  return {
    entityName: '订单',
    importTips: [
      '1. 请下载模板文件，按照模板格式填写订单数据',
      '2. 订单号必须唯一，机型、料号、序列号范围等字段不能为空',
      '3. 序列号格式支持：起始--结束（双横线）或换行分隔',
      '4. 每个订单必须包含至少一个组件，每个组件必须包含至少一个子组件和软件',
      '5. 如有数据错误，系统将返回带有错误信息的Excel文件，修改后可重新导入',
    ],

    // 预览列配置 - 根据订单的层次结构显示
    previewColumns: [
      { prop: 'order_number', label: '订单号', width: 120 },
      { prop: 'model', label: '机型', width: 100 },
      { prop: 'part_number', label: '料号', width: 130 },
      { prop: 'serial_number_range', label: '序列号范围', minWidth: 180 },
      { prop: 'component_count', label: '组件数量', width: 100 },
    ],

    // API配置
    downloadTemplateApi: orderApi.downloadOrderImportTemplate,
    uploadApi: orderApi.uploadOrderImportFile,
  }
}

// 机构导入配置
export const getInstitutionImportConfig = () => {
  const i18nStore = useI18nStore()
  return {
    entityName: i18nStore.t('entities.institution'),
    importTips: [
      i18nStore.t('import.tips.institution.1'),
      i18nStore.t('import.tips.institution.2'),
      i18nStore.t('import.tips.institution.3'),
    ],

    // 预览列配置
    previewColumns: [
      { prop: 'institution_code', label: i18nStore.t('institution.code'), width: 120 },
      { prop: 'institution_name', label: i18nStore.t('institution.name'), width: 120 },
      { prop: 'level', label: i18nStore.t('institution.level'), width: 80 },
      { prop: 'contact_info', label: i18nStore.t('institution.contactInfo'), width: 120 },
      { prop: 'address', label: i18nStore.t('institution.address'), minWidth: 150 },
      { prop: 'status', label: i18nStore.t('common.status'), width: 80 },
    ],
    // API配置
    uploadApi: institutionApi.uploadForValidation, // 上传文件进行验证的API
    importApi: institutionApi.batchImport, // 最终导入API
    downloadTemplateApi: institutionApi.downloadTemplate, // 下载模板API（可选）
  }
}

// 设备导入配置
export const getDeviceImportConfig = () => {
  const i18nStore = useI18nStore()
  return {
    entityName: i18nStore.t('entities.device'),
    importTips: [
      i18nStore.t('import.tips.device.1'),
      i18nStore.t('import.tips.device.2'),
      i18nStore.t('import.tips.device.3'),
      i18nStore.t('import.tips.device.4'),
    ],

    // 使用后端API返回的真实Excel模板文件
    previewColumns: [
      { prop: 'device_id', label: i18nStore.t('device.id'), width: 120 },
      { prop: 'model_name', label: i18nStore.t('device.model'), width: 120 },
      { prop: 'institution_name', label: i18nStore.t('device.institution'), width: 150 },
      { prop: 'description', label: i18nStore.t('common.description'), minWidth: 150 },
    ],
    // API配置
    uploadApi: deviceApi.uploadForValidation, // 上传文件进行验证的API
    importApi: deviceApi.batchImportDevices, // 最终导入API
    downloadTemplateApi: deviceApi.downloadTemplate, // 下载模板API（可选）
  }
}
