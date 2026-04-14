from backend.extensions import db
from backend.order.model import Order, Component, SubComponent, Software
from sqlalchemy import func, and_, or_
import uuid

def add_order(order_data):
    """新增订单"""
    # 提取订单基本信息
    order_info = {
        'order_number': order_data['order_number'],
        'model': order_data['model'],
        'part_number': order_data['part_number'],
        'serial_number_start': order_data['serial_number_start'],
        'serial_number_end': order_data['serial_number_end'],
        'remark': order_data.get('remark'),
        'order_created_at': order_data.get('order_created_at')
    }
    
    # 创建订单
    new_order = Order(**order_info)
    db.session.add(new_order)
    
    # 先刷新session以获取订单ID
    db.session.flush()
    
    # 处理组件数据
    if 'components' in order_data:
        for component_data in order_data['components']:
            component = Component(
                component_name=component_data['component_name'],
                component_part_number=component_data['component_part_number'],
                order_id=new_order.id
            )
            db.session.add(component)
            
            # 刷新session以获取组件ID
            db.session.flush()
            
            # 处理子组件数据
            if 'sub_components' in component_data:
                for sub_component_data in component_data['sub_components']:
                    sub_component = SubComponent(
                        sub_component_name=sub_component_data['sub_component_name'],
                        sub_component_part_number=sub_component_data['sub_component_part_number'],
                        specification=sub_component_data.get('specification'),
                        component_id=component.id
                    )
                    db.session.add(sub_component)
                    
                    # 刷新session以获取子组件ID
                    db.session.flush()
                    
                    # 处理软件数据
                    if 'softwares' in sub_component_data:
                        for software_data in sub_component_data['softwares']:
                            software = Software(
                                software_name=software_data['software_name'],
                                software_version=software_data.get('software_version'),
                                attachment=software_data.get('attachment'),
                                sub_component_id=sub_component.id
                            )
                            db.session.add(software)
    
    db.session.commit()
    return new_order

def get_order_by_id(order_id):
    """根据ID查询订单"""
    return Order.query.filter_by(id=order_id).first()

def get_order_by_order_number(order_number):
    """根据订单号查询订单"""
    return Order.query.filter_by(order_number=order_number).first()

def get_all_orders(page, per_page, filter_params=None, sort_by='created_at', sort_order='desc'):
    """获取订单列表，支持筛选、排序和分页"""
    # 构建基础查询，包含组件数量统计
    query = db.session.query(
        Order,
        func.count(db.distinct(Component.id)).label('component_count')
    ).outerjoin(
        Component, Order.id == Component.order_id
    )
    
    # 应用筛选条件
    if filter_params:
        # 订单号模糊筛选
        if 'order_number' in filter_params and filter_params['order_number']:
            query = query.filter(Order.order_number.like(f"%{filter_params['order_number']}%"))
        
        # 料号筛选
        if 'part_number' in filter_params and filter_params['part_number']:
            query = query.filter(Order.part_number.like(f"%{filter_params['part_number']}%"))
        
        # 机型筛选
        if 'model' in filter_params and filter_params['model']:
            query = query.filter(Order.model.like(f"%{filter_params['model']}%"))
        
        # 序列号查询（在范围内任意一个序列号均能查询到订单信息）
        if 'serial_number' in filter_params and filter_params['serial_number']:
            serial_number = filter_params['serial_number']
            query = query.filter(
                or_(
                    and_(Order.serial_number_start <= serial_number, Order.serial_number_end >= serial_number),
                    Order.serial_number_start == serial_number,
                    Order.serial_number_end == serial_number
                )
            )
        
        # 组件料号模糊筛选
        if 'component_part_number' in filter_params and filter_params['component_part_number']:
            query = query.filter(Component.component_part_number.like(f"%{filter_params['component_part_number']}%"))

        # 子组件料号模糊筛选 (需要额外连接 SubComponent 表)
        if 'sub_component_part_number' in filter_params and filter_params['sub_component_part_number']:
            # 动态添加 join
            query = query.join(SubComponent,
                Component.id == SubComponent.component_id
            ).filter(SubComponent.sub_component_part_number.like(f"%{filter_params['sub_component_part_number']}%"))

    # 按订单ID分组，以确保每个订单只返回一次
    query = query.group_by(Order.id)
    
    # 应用排序
    sort_columns = {
        'order_number': Order.order_number,
        'model': Order.model,
        'part_number': Order.part_number,
        'created_at': Order.created_at
    }
    
    sort_column = sort_columns.get(sort_by, Order.created_at)
    query = query.order_by(sort_column.desc() if sort_order == 'desc' else sort_column.asc())
    
    # 分页查询（当前 items 为 (Order, component_count) 的元组）
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 将 items 转换为仅包含 Order 实例，并把 component_count 写入到实例上
    orders_only = []
    for order, component_count in pagination.items:
        # 将统计结果挂到实例，便于序列化
        try:
            order.component_count = int(component_count) if component_count is not None else 0
        except Exception:
            order.component_count = 0
        orders_only.append(order)

    # 覆盖分页结果的 items，保证序列化时拿到的是模型对象
    pagination.items = orders_only

    return pagination

def update_order(order, update_data):
    """更新订单信息
    支持：
    1) 基本字段更新
    2) 若提供 components，则视为对订单下的组件子树进行全量替换：
       - 逻辑删除旧组件（及其子组件、软件会由数据库外键级联删除或我们一并处理）
       - 重建新组件树
    """

    # 1. 基本字段更新（排除 components）
    scalar_fields = {k: v for k, v in update_data.items() if k != 'components'}
    for key, value in scalar_fields.items():
        if hasattr(order, key):
            setattr(order, key, value)

    # 2. 嵌套子树替换
    if 'components' in update_data and update_data['components'] is not None:
        # 2.1 物理删除现有组件子树
        # 说明：数据库外键已设置 ON DELETE CASCADE，直接删除组件会级联删除其子组件与软件
        # 若你的数据库未设置该约束，可在此处先删 softwares -> sub_components -> components
        existing_components = Component.query.filter_by(order_id=order.id).all()
        for comp in existing_components:
            db.session.delete(comp)
        db.session.flush()

        # 2.2 重建新组件树
        for component_data in update_data['components']:
            component = Component(
                component_name=component_data['component_name'],
                component_part_number=component_data['component_part_number'],
                order_id=order.id
            )
            db.session.add(component)
            db.session.flush()

            if 'sub_components' in component_data and component_data['sub_components']:
                for sub_component_data in component_data['sub_components']:
                    sub_component = SubComponent(
                        sub_component_name=sub_component_data['sub_component_name'],
                        sub_component_part_number=sub_component_data['sub_component_part_number'],
                        specification=sub_component_data.get('specification'),
                        component_id=component.id
                    )
                    db.session.add(sub_component)
                    db.session.flush()

                    if 'softwares' in sub_component_data and sub_component_data['softwares']:
                        for software_data in sub_component_data['softwares']:
                            software = Software(
                                software_name=software_data['software_name'],
                                software_version=software_data.get('software_version'),
                                attachment=software_data.get('attachment'),
                                sub_component_id=sub_component.id
                            )
                            db.session.add(software)

    db.session.commit()
    return order

def delete_order(order):
    """物理删除订单"""
    db.session.delete(order)
    db.session.commit()

def get_order_with_details(order_id):
    """获取订单详细信息，包含所有关联的组件、子组件和软件"""
    return Order.query.filter_by(id=order_id).first()

def check_order_number_exists(order_number, exclude_id=None):
    """检查订单号是否已存在"""
    query = Order.query.filter_by(order_number=order_number)
    if exclude_id:
        query = query.filter(Order.id != exclude_id)
    return query.first() is not None

def check_component_part_number_exists(component_part_number, exclude_id=None):
    """检查组件料号是否已存在"""
    query = Component.query.filter_by(component_part_number=component_part_number)
    if exclude_id:
        query = query.filter(Component.id != exclude_id)
    return query.first() is not None

def check_sub_component_part_number_exists(sub_component_part_number, exclude_id=None):
    """检查子组件料号是否已存在"""
    query = SubComponent.query.filter_by(sub_component_part_number=sub_component_part_number)
    if exclude_id:
        query = query.filter(SubComponent.id != exclude_id)
    return query.first() is not None

def check_component_part_number_exists_in_other_orders(component_part_number: str, current_order_id: str) -> bool:
    """检查该组件料号是否存在于其他订单（用于嵌套更新时允许本订单内重建）"""
    return db.session.query(Component.id).filter(
        Component.component_part_number == component_part_number,
        Component.order_id != current_order_id
    ).first() is not None

def check_sub_component_part_number_exists_in_other_orders(sub_component_part_number: str, current_order_id: str) -> bool:
    """检查该子组件料号是否存在于其他订单（用于嵌套更新时允许本订单内重建）"""
    return db.session.query(SubComponent.id).join(Component, SubComponent.component_id == Component.id).filter(
        SubComponent.sub_component_part_number == sub_component_part_number,
        Component.order_id != current_order_id
    ).first() is not None





def get_software_by_id(software_id):
    """根据ID获取软件"""
    return Software.query.filter_by(id=software_id).first()


def update_software(software):
    """更新软件"""
    db.session.commit()


def get_all_orders_for_export(filter_params=None, sort_by='created_at', sort_order='desc'):
    """
    获取所有符合条件的订单用于导出，支持筛选和排序，但不分页。
    :param filter_params: 筛选条件字典
    :param sort_by: 排序字段
    :param sort_order: 排序方向 ('asc' 或 'desc')
    :return: 订单列表
    """
    from sqlalchemy.orm import joinedload

    # 构建基础查询，预加载所有关联数据
    query = db.session.query(Order).options(
        joinedload(Order.components).joinedload(Component.sub_components).joinedload(SubComponent.softwares)
    )

    # 应用筛选条件
    if filter_params:
        # 订单号模糊筛选
        if 'order_number' in filter_params and filter_params['order_number']:
            query = query.filter(Order.order_number.like(f"%{filter_params['order_number']}%"))
        
        # 料号筛选
        if 'part_number' in filter_params and filter_params['part_number']:
            query = query.filter(Order.part_number.like(f"%{filter_params['part_number']}%"))
        
        # 机型筛选
        if 'model' in filter_params and filter_params['model']:
            query = query.filter(Order.model.like(f"%{filter_params['model']}%"))
        
        # 序列号查询
        if 'serial_number' in filter_params and filter_params['serial_number']:
            serial_number = filter_params['serial_number']
            query = query.filter(
                or_(
                    and_(Order.serial_number_start <= serial_number, Order.serial_number_end >= serial_number),
                    Order.serial_number_start == serial_number,
                    Order.serial_number_end == serial_number
                )
            )
        
        # 组件料号模糊筛选
        if 'component_part_number' in filter_params and filter_params['component_part_number']:
            # 需要连接 Component 表
            query = query.join(Component,
                Order.id == Component.order_id
            ).filter(Component.component_part_number.like(f"%{filter_params['component_part_number']}%"))

        # 子组件料号模糊筛选
        if 'sub_component_part_number' in filter_params and filter_params['sub_component_part_number']:
            # 需要连接 Component 和 SubComponent 表
            if 'component_part_number' not in filter_params: # 避免重复 join
                query = query.join(Component,
                    Order.id == Component.order_id
                )
            query = query.join(SubComponent,
                Component.id == SubComponent.component_id
            ).filter(SubComponent.sub_component_part_number.like(f"%{filter_params['sub_component_part_number']}%"))

    # 应用排序
    sort_columns = {
        'order_number': Order.order_number,
        'model': Order.model,
        'part_number': Order.part_number,
        'created_at': Order.created_at
    }
    
    sort_column = sort_columns.get(sort_by, Order.created_at)
    query = query.order_by(sort_column.desc() if sort_order == 'desc' else sort_column.asc())
    
    return query.all()
