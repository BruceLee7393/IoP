// 订单模板数据
export const orderTemplate = {
  order_number: 'DA25214',
  model: 'PN1.5X',
  part_number: '908010400.008',
  serial_number_start: 'PN15700001',
  serial_number_end: 'PN15700720',
  order_created_at: '',
  remark: '',
  components: [
    {
      component_name: '母板组件',
      component_part_number: '808010400.001',
      sub_components: [
        {
          sub_component_name: '母板',
          sub_component_part_number: '708010400.001',
          specification: 'PCB版本V0.2，DSP平台',
          softwares: [
            {
              software_name: 'USB驱动',
              software_version: 'SET_V1.10_2024108',
              attachment: ''
            },
           
          ]
        },
        {
          sub_component_name: '核心板',
          sub_component_part_number: '708010400.001',
          specification: 'PCB版本V0.7，DSP平台',
          softwares: [
             {
              software_name: 'BOOT',
              software_version: 'SET_V1.165_2024106',
              attachment: ''
            },
            {
              software_name: 'APP',
              software_version: 'P8DD.fV1.008.dV2.051.a0.20200715.CSW',
              attachment: ''
            }
          ]
        }
      ]
    },
    
    {
      component_name: '面板组件',
      component_part_number: '808010400.002',
      sub_components: [
        {
          sub_component_name: '按键控制板',
          sub_component_part_number: '708010400.001',
          specification: 'v.128',
          softwares: [
            {
              software_name: 'BOOT',
              software_version: ' 1.5P_CLCD_Panel_BOOT_V1.007-(2018-09-22).bin',
              attachment: ''
            },
            {
              software_name: 'APP',
              software_version: 'RJ-2-12-2-17(PANEL_20200520)_PN1.5TE-V2.051-CLCD-G+D.CSW',
              attachment: ''
            }
          ]
        }
      ]
    },
    {
      component_name: '网发组件',
      component_part_number: '808010400.002',
      sub_components: [
        {
          sub_component_name: '网络组件',
          sub_component_part_number: '708010400.001',
          specification: 'PCBA名称、版本号',
          softwares: [
            {
              software_name: 'BOOT',
              software_version: 'updateiotBOOT.tar',
              attachment: ''
            },
            {
              software_name: 'APP',
              software_version: 'updateiot.tar',
              attachment: ''
            }
          ]
        }
      ]
    },
    {
      component_name: '厚度组件',
      component_part_number: '808010400.002',
      sub_components: [
        {
          sub_component_name: '厚度组件',
          sub_component_part_number: '708010400.021',
          specification: 'PCBA合格，版本号',
          softwares: [
            {
              software_name: '应用程序',
              software_version: 'RJ-2-15-2-54updateiot.tar',
              attachment: ''
            }
          ]
        }
      ]
    }
  ]
}

// 获取订单模板的函数
export const getOrderTemplate = () => {
  // 返回深拷贝，避免修改原始模板
  return JSON.parse(JSON.stringify(orderTemplate))
}

// 清空订单数据的函数
export const getEmptyOrderData = () => {
  return {
    order_number: '',
    model: '',
    part_number: '',
    serial_number_start: '',
    serial_number_end: '',
    order_created_at: '',
    remark: '',
    components: []
  }
}
