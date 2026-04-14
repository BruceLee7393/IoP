from webargs import fields, validate


# 定义用户导出查询参数 Schema（复用列表查询的筛选参数，但不需要分页）
user_export_query_args = {
    # 精确筛选参数（完整匹配）
    "role_id": fields.Str(),         # 角色ID
    "status": fields.Str(validate=validate.OneOf(['active', 'disabled'])),  # 用户状态
    "gender": fields.Str(validate=validate.OneOf(['woman', 'man', 'none', 'others'])),  # 性别
    "created_at_start": fields.DateTime(),  # 创建时间起
    "created_at_end": fields.DateTime(),   # 创建时间止

    # 模糊筛选参数（部分匹配）
    "account": fields.Str(),         # 账号（开头匹配）
    "full_name": fields.Str(),       # 姓名（包含匹配）
    "contact_info": fields.Str(),    # 联系方式（开头匹配）
    "address": fields.Str(),         # 地址（包含匹配）

    # 排序参数
    "sort_by": fields.Str(load_default='created_at',validate=validate.OneOf([
        'account', 'full_name', 'contact_info', 'address', 'status',
        'role_name','created_at'
    ])),  # 排序字段
    "sort_order": fields.Str(load_default='desc', validate=validate.OneOf(['asc', 'desc']))  # 排序方向，默认升序
}


# 定义 User 序列化 Schema，用于控制 API 输出
user_schema = {
    "id": fields.Str(dump_only=True),
    "account": fields.Str(dump_only=True),
    "full_name": fields.Str(dump_only=True),
    # 嵌套 Role 的关键信息
    "role": fields.Nested({
        "id": fields.Str(dump_only=True),
        "role_name": fields.Str(dump_only=True)
    }, dump_only=True),
    "contact_info": fields.Str(dump_only=True),
    "address": fields.Str(dump_only=True),
    "status": fields.Str(dump_only=True),
    "gender": fields.Str(dump_only=True),
    "created_at": fields.DateTime(dump_only=True),
}

# User 更新 Schema，用于 API 输入验证
user_update_schema = {
    "password": fields.Str(
        validate=[
            validate.Length(min=4),
            validate.Regexp(
                r'^[a-zA-Z0-9\W_]+$', # 这是一个允许数字、字母、特殊字符但不包括中文的正则表达式
                error="密码不能包含中文字符"
            )
        ]
    ),
    "full_name": fields.Str(),
    "role_id": fields.Str(),
    "contact_info": fields.Str(),
    "address": fields.Str(),
    "gender": fields.Str(validate=validate.OneOf(['woman', 'man', 'none', 'others'])),
    "status": fields.Str(validate=validate.OneOf(['active', 'disabled'])),
}

# User 自助更新 Schema（用户修改自己的信息，不允许改角色/机构/状态等敏感字段）
user_self_update_schema = {
    "password": fields.Str(
        validate=[
            validate.Length(min=4),
            validate.Regexp(
                r'^[a-zA-Z0-9\W_]+$',
                error="密码不能包含中文字符"
            )
        ]
    ),
    "full_name": fields.Str(),
    "contact_info": fields.Str(),
    "address": fields.Str(),
    "gender": fields.Str(validate=validate.OneOf(['woman', 'man', 'none', 'others'])),
}

# 注册 Schema，用于 API 输入验证
user_register_schema = {
    "account": fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^[a-zA-Z][a-zA-Z0-9_]{3,15}$',
            error="账号必须以英文开头，可包含字母、数字和下划线，长度4-16位"
        )
    ),
    "password": fields.Str(
        required=True,
        validate=[
            validate.Length(min=4),
            validate.Regexp(
                r'^[a-zA-Z0-9\W_]+$', # 这是一个允许数字、字母、特殊字符但不包括中文的正则表达式
                error="密码不能包含中文字符"
            )
        ]
    ),
    "full_name": fields.Str(),
    "role_id": fields.Str(),
    "contact_info": fields.Str(),
    "address": fields.Str(),
    "gender": fields.Str(validate=validate.OneOf(['woman', 'man', 'none', 'others'])),
}


# 通用分页参数，可以被其他模块导入使用
pagination_args = {
    "page": fields.Int(load_default=1, validate=lambda p: p > 0),
    "per_page": fields.Int(load_default=10, validate=lambda p: p > 0),
}


# 定义用户列表查询参数 Schema，包含筛选、排序和分页
user_list_query_args = {
    # 分页参数
    "page": fields.Int(load_default=1, validate=lambda p: p > 0),
    "per_page": fields.Int(load_default=10, validate=lambda p: p > 0),
    
    # 精确筛选参数（完整匹配）
    "role_id": fields.Str(),         # 角色ID
    "status": fields.Str(validate=validate.OneOf(['active', 'disabled'])),  # 用户状态
    "gender": fields.Str(validate=validate.OneOf(['woman', 'man', 'none', 'others'])),  # 性别
    "created_at_start": fields.DateTime(),  # 创建时间起
    "created_at_end": fields.DateTime(),   # 创建时间止

    # 模糊筛选参数（部分匹配）
    "account": fields.Str(),         # 账号（开头匹配）
    "full_name": fields.Str(),       # 姓名（包含匹配）
    "contact_info": fields.Str(),    # 联系方式（开头匹配）
    "address": fields.Str(),         # 地址（包含匹配）

    # 排序参数
    "sort_by": fields.Str(load_default='created_at',validate=validate.OneOf([
        'account', 'full_name', 'contact_info', 'address', 'status',
        'role_name','created_at'
    ])),  # 排序字段
    "sort_order": fields.Str(load_default='desc', validate=validate.OneOf(['asc', 'desc']))  # 排序方向，默认升序
}

# 定义批量删除用户的 Schema，用于 API 输入验证
user_batch_delete_schema = {
    "user_ids": fields.List(
        fields.Str(required=True), 
        required=True, 
        validate=validate.Length(min=1, max=100),  # 限制批量删除数量，避免一次删除过多
        error_messages={'required': 'user_ids字段是必需的'}
    )
}

# 定义批量删除结果的 Schema，用于 API 输出序列化
user_batch_delete_result_schema = {
    "total_requested": fields.Int(dump_only=True),
    "successfully_deleted": fields.List(fields.Str(), dump_only=True),
    "not_found": fields.List(fields.Str(), dump_only=True),
    "skipped_ids": fields.List(fields.Str(), dump_only=True),
    "success_count": fields.Int(dump_only=True),
    "not_found_count": fields.Int(dump_only=True),
    "skipped_count": fields.Int(dump_only=True)
}