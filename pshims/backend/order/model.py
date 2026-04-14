import string
import uuid
from backend.extensions import db
from sqlalchemy import Column, String, DateTime, Boolean, column, func, ForeignKey, Text
from sqlalchemy.orm import relationship

class Order(db.Model):
    """订单模型"""
    
    __tablename__ = 'orders'

    # 核心字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False, comment='订单号，唯一')
    model = Column(String(50), nullable=False, comment='机型')
    part_number = Column(String(50), nullable=False, comment='料号')
    serial_number_start = Column(String(50), nullable=False, comment='序列号起始')
    serial_number_end = Column(String(50), nullable=False, comment='序列号结束')
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')
    
    #新增部分
    remark = Column(String(200), comment='备注')
    order_created_at = Column(DateTime, comment='订单创建时间')
    #新增附件
    appendix = Column(String(128), comment='附件，存储下载地址')
    # 关系定义
    components = relationship('Component', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.order_number}>'


class Component(db.Model):
    """组件模型"""
    
    __tablename__ = 'components'

    # 核心字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    component_name = Column(String(128), nullable=False, comment='组件名称，可重复')
    component_part_number = Column(String(128),  nullable=False, comment='组件料号')
    
    # 外键关联
    order_id = Column(String(36), ForeignKey('orders.id'), nullable=False, comment='关联订单ID')
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')

    # 关系定义
    order = relationship('Order', back_populates='components')
    sub_components = relationship('SubComponent', back_populates='component', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Component {self.component_part_number}>'


class SubComponent(db.Model):
    """子组件模型"""
    
    __tablename__ = 'sub_components'

    # 核心字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sub_component_name = Column(String(50), nullable=False, comment='子组件名称，可重复')
    sub_component_part_number = Column(String(50), nullable=False, comment='子组件料号')
    specification = Column(String(100), comment='规格型号')
    
    # 外键关联
    component_id = Column(String(36), ForeignKey('components.id'), nullable=False, comment='关联父组件ID')
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')

    # 关系定义
    component = relationship('Component', back_populates='sub_components')
    softwares = relationship('Software', back_populates='sub_component', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SubComponent {self.sub_component_part_number}>'


class Software(db.Model):
    """软件模型"""
    
    __tablename__ = 'softwares'

    # 核心字段
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    software_name = Column(String(128), nullable=False, comment='软件名称，可重复')
    software_version = Column(String(128), comment='软件版本号，可重复')
    attachment = Column(String(200), comment='附件名称或路径，可重复')
    
    # 外键关联
    sub_component_id = Column(String(36), ForeignKey('sub_components.id'), nullable=False, comment='关联子组件ID')
    
    # 审计字段
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')

    #新增附件
    appendix = Column(String(128), comment='附件，存储下载地址')

    # 关系定义
    sub_component = relationship('SubComponent', back_populates='softwares')

    def __repr__(self):
        return f'<Software {self.software_name}>'
