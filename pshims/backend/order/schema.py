from webargs import fields, validate

# 通用分页参数
pagination_args = {
    "page": fields.Int(load_default=1, validate=lambda p: p > 0),
    "per_page": fields.Int(load_default=10, validate=lambda p: p > 0),
}

# 订单创建 Schema
order_create_schema = {
    "order_number": fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    ),
    "model": fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    ),
    "part_number": fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    ),
    "serial_number_start": fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    ),
    "serial_number_end": fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    ),
    "remark": fields.Str(
        validate=validate.Length(max=200),
        allow_none=True,
    ),
    "order_created_at": fields.DateTime(
        allow_none=True,
    ),
    "components": fields.List(
        fields.Nested({
            "component_name": fields.Str(
                required=True,
                validate=validate.Length(min=1, max=128)
            ),
            "component_part_number": fields.Str(
                required=True,
                validate=validate.Length(min=1, max=128)
            ),
            "sub_components": fields.List(
                fields.Nested({
                    "sub_component_name": fields.Str(
                        required=True,
                        validate=validate.Length(min=1, max=128)
                    ),
                    "sub_component_part_number": fields.Str(
                        required=True,
                        validate=validate.Length(min=1, max=128)
                    ),
                    "specification": fields.Str(
                        validate=validate.Length(max=100)
                    ),
                    "softwares": fields.List(
                        fields.Nested({
                            "software_name": fields.Str(
                                required=True,
                                validate=validate.Length(min=1, max=128)
                            ),
                            "software_version": fields.Str(
                                validate=validate.Length(max=128)
                            ),
                            "attachment": fields.Str(
                                validate=validate.Length(max=200)
                            )
                        })
                    )
                })
            )
        })
    )
}

# 订单更新 Schema
order_update_schema = {
    "order_number": fields.Str(
        validate=validate.Length(min=1, max=50)
    ),
    "model": fields.Str(
        validate=validate.Length(min=1, max=50)
    ),
    "part_number": fields.Str(
        validate=validate.Length(min=1, max=50)
    ),
    "serial_number_start": fields.Str(
        validate=validate.Length(min=1, max=50)
    ),
    "serial_number_end": fields.Str(
        validate=validate.Length(min=1, max=50)
    ),
    "remark": fields.Str(
        validate=validate.Length(max=200),
        allow_none=True,

    ),
    "order_created_at": fields.DateTime(
        allow_none=True,

    ),
    # 支持嵌套更新：若提供components则视为对整棵子树的替换
    "components": fields.List(
        fields.Nested({
            "component_name": fields.Str(
                required=True,
                validate=validate.Length(min=1, max=128)
            ),
            "component_part_number": fields.Str(
                required=True,
                validate=validate.Length(min=1, max=128)
            ),
            "sub_components": fields.List(
                fields.Nested({
                    "sub_component_name": fields.Str(
                        required=True,
                        validate=validate.Length(min=1, max=128)
                    ),
                    "sub_component_part_number": fields.Str(
                        required=True,
                        validate=validate.Length(min=1, max=128)
                    ),
                    "specification": fields.Str(
                        validate=validate.Length(max=100)
                    ),
                    "softwares": fields.List(
                        fields.Nested({
                            "software_name": fields.Str(
                                required=True,
                                validate=validate.Length(min=1, max=128)
                            ),
                            "software_version": fields.Str(
                                validate=validate.Length(max=128)
                            ),
                            "attachment": fields.Str(
                                validate=validate.Length(max=200)
                            )
                        })
                    )
                })
            )
        })
    )
}

# 订单列表查询参数 Schema
order_list_query_args = {
    # 分页参数
    "page": fields.Int(load_default=1, validate=lambda p: p > 0),
    "per_page": fields.Int(load_default=10, validate=lambda p: p > 0),
    
    # 筛选参数
    "order_number": fields.Str(),
    "part_number": fields.Str(),
    "model": fields.Str(),
    "serial_number": fields.Str(),
    "component_part_number": fields.Str(),
    "sub_component_part_number": fields.Str(),
    
    # 排序参数
    "sort_by": fields.Str(
        load_default='created_at',
        validate=validate.OneOf(['order_number', 'model', 'part_number', 'created_at'])
    ),
    "sort_order": fields.Str(
        load_default='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )
}

# 订单输出 Schema
order_schema = {
    "id": fields.Str(dump_only=True),
    "order_number": fields.Str(dump_only=True),
    "model": fields.Str(dump_only=True),
    "part_number": fields.Str(dump_only=True),
    "serial_number_start": fields.Str(dump_only=True),
    "serial_number_end": fields.Str(dump_only=True),
    "created_at": fields.DateTime(dump_only=True),
    "remark": fields.Str(dump_only=True),
    "order_created_at": fields.DateTime(dump_only=True),
    "appendix": fields.Str(dump_only=True),
    "components": fields.List(
        fields.Nested({
            "id": fields.Str(dump_only=True),
            "component_name": fields.Str(dump_only=True),
            "component_part_number": fields.Str(dump_only=True),
            "created_at": fields.DateTime(dump_only=True),
            "sub_components": fields.List(
                fields.Nested({
                    "id": fields.Str(dump_only=True),
                    "sub_component_name": fields.Str(dump_only=True),
                    "sub_component_part_number": fields.Str(dump_only=True),
                    "specification": fields.Str(dump_only=True),
                    "created_at": fields.DateTime(dump_only=True),
                    "softwares": fields.List(
                        fields.Nested({
                            "id": fields.Str(dump_only=True),
                            "software_name": fields.Str(dump_only=True),
                            "software_version": fields.Str(dump_only=True),
                            "attachment": fields.Str(dump_only=True),
                            "created_at": fields.DateTime(dump_only=True),
                            "appendix": fields.Str(dump_only=True)
                        }),
                        dump_only=True
                    )
                }),
                dump_only=True
            )
        }),
        dump_only=True
    )
}

# 订单列表输出 Schema（简化版，不包含完整的组件信息）
order_list_schema = {
    "id": fields.Str(dump_only=True),
    "order_number": fields.Str(dump_only=True),
    "model": fields.Str(dump_only=True),
    "part_number": fields.Str(dump_only=True),
    "serial_number_start": fields.Str(dump_only=True),
    "serial_number_end": fields.Str(dump_only=True),
    "created_at": fields.DateTime(dump_only=True),
    "component_count": fields.Int(dump_only=True),
    "remark": fields.Str(dump_only=True),
    "order_created_at": fields.DateTime(dump_only=True),
    "appendix": fields.Str(dump_only=True)
}
