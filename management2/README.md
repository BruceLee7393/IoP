# Order 模块


订单管理模块，提供完整的订单生命周期管理功能。

## 功能特性

- ✅ 新增订单（包含组件、子组件、软件信息）
- ✅ 修改订单基本信息
- ✅ 删除订单（逻辑删除）
- ✅ 查询订单列表（支持筛选、排序、分页）
- ✅ 查询订单详情（包含完整的组件层级信息）

## 数据库表结构

### orders 表
- `id`: UUID主键
- `order_number`: 订单号（唯一）
- `model`: 机型
- `part_number`: 料号
- `serial_number_start`: 序列号起始
- `serial_number_end`: 序列号结束
- `created_at`: 创建时间
- `is_deleted`: 逻辑删除标记

### components 表
- `id`: UUID主键
- `component_name`: 组件名称
- `component_part_number`: 组件料号（唯一）
- `order_id`: 关联订单ID
- `created_at`: 创建时间
- `is_deleted`: 逻辑删除标记

### sub_components 表
- `id`: UUID主键
- `component_id`: 关联父组件ID
- `sub_component_name`: 子组件名称
- `sub_component_part_number`: 子组件料号（唯一）
- `specification`: 规格型号
- `created_at`: 创建时间
- `is_deleted`: 逻辑删除标记

### softwares 表
- `id`: UUID主键
- `sub_component_id`: 关联子组件ID
- `software_name`: 软件名称
- `software_version`: 软件版本号
- `attachment`: 附件名称或路径
- `created_at`: 创建时间
- `is_deleted`: 逻辑删除标记

## API 接口

### 1. 新增订单
```
POST /api/orders
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "order_number": "ORDER001",
  "model": "Model-A",
  "part_number": "PART001",
  "serial_number_start": "SN001",
  "serial_number_end": "SN100",
  "components": [
    {
      "component_name": "Component-1",
      "component_part_number": "COMP001",
      "sub_components": [
        {
          "sub_component_name": "Sub-Component-1",
          "sub_component_part_number": "SUB001",
          "specification": "Spec-1",
          "softwares": [
            {
              "software_name": "Software-1",
              "software_version": "v1.0",
              "attachment": "attachment1.pdf"
            }
          ]
        }
      ]
    }
  ]
}
```

### 2. 查询订单列表
```
GET /api/orders?page=1&per_page=10&order_number=ORDER&part_number=PART001&model=Model-A&serial_number=SN050&sort_by=created_at&sort_order=desc
Authorization: Bearer <JWT_TOKEN>
```

**查询参数说明：**
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认10）
- `order_number`: 订单号模糊筛选
- `part_number`: 料号精确筛选
- `model`: 机型精确筛选
- `serial_number`: 序列号查询（在范围内任意一个序列号均能查询到订单信息）
- `sort_by`: 排序字段（order_number, model, part_number, created_at）
- `sort_order`: 排序方向（asc, desc）

### 3. 查询订单详情
```
GET /api/orders/{order_id}
Authorization: Bearer <JWT_TOKEN>
```

### 4. 修改订单
```
PUT /api/orders/{order_id}
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

仅改基本字段（不动组件树）
{
  "order_number": "ORDERTEST-001-REV1",
  "model": "Model-X1-RevA",
  "part_number": "PN-X1-001-REV1",
  "serial_number_start": "SNX1005",
  "serial_number_end": "SNX1150"
}



全量替换整棵组件树（会删除旧树后重建）
{
  "order_number": "ORDERTEST-001-REV2",
  "model": "Model-X1-RevB",
  "part_number": "PN-X1-001-REV2",
  "serial_number_start": "SNX1200",
  "serial_number_end": "SNX1299",
  "components": [
    {
      "component_name": "MainBoard-V2",
      "component_part_number": "COMP-X1-101",
      "sub_components": [
        {
          "sub_component_name": "CPU-Module-V2",
          "sub_component_part_number": "SUB-X1-CPU-101",
          "specification": "ARMv9-A",
          "softwares": [
            {
              "software_name": "Bootloader",
              "software_version": "1.1.0",
              "attachment": "bootloader_1.1.0.bin"
            },
            {
              "software_name": "DiagTool",
              "software_version": "0.9.0",
              "attachment": "diag_0.9.0.exe"
            }
          ]
        }
      ]
    },
    {
      "component_name": "I/O-Board",
      "component_part_number": "COMP-X1-IO-201",
      "sub_components": [
        {
          "sub_component_name": "USB-Controller",
          "sub_component_part_number": "SUB-X1-USB-201",
          "specification": "USB3.2",
          "softwares": [
            {
              "software_name": "USBFW",
              "software_version": "3.0.0",
              "attachment": "usbfw_3.0.0.bin"
            }
          ]
        }
      ]
    }
  ]
}


### 5. 删除订单
```
DELETE /api/orders/{order_id}
Authorization: Bearer <JWT_TOKEN>
```

## 权限要求

- 新增订单：需要 `OrderManagement` 权限
- 修改订单：需要 `OrderManagement` 权限
- 删除订单：需要 `OrderManagement` 权限
- 查询订单：需要有效的JWT token

## 特殊功能

### 序列号范围查询
支持通过任意序列号查询订单，只要该序列号在订单的序列号范围内即可：
- 序列号范围：`serial_number_start` 到 `serial_number_end`
- 查询逻辑：`serial_number_start <= query_serial_number <= serial_number_end`

### 组件数量统计
订单列表查询会自动统计每个订单包含的组件数量，返回在 `component_count` 字段中。

## 错误处理

模块使用统一的异常处理机制：
- `DuplicateResourceError`: 资源重复（如订单号、料号重复）
- `ResourceNotFoundError`: 资源不存在
- `InvalidUsageError`: 参数验证失败或其他业务逻辑错误



## 注意事项

1. 所有删除操作都是逻辑删除，不会物理删除数据
2. 组件料号和子组件料号必须唯一
3. 订单号必须唯一
4. 序列号范围查询支持字符串比较，请确保序列号格式一致
5. 创建订单时会自动生成UUID作为主键
6. 所有时间字段使用UTC时间
