import uuid
from backend.extensions import db
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean, ForeignKey


class RolePermission(db.Model):
    """角色权限连接表"""
    __tablename__ = 'role_mapping_permissions'

    role_id = Column(String(36), ForeignKey('roles.id'), primary_key=True, comment='角色ID')
    permission_id = Column(String(36), ForeignKey('permissions.id'), primary_key=True, comment='权限ID')

    def __repr__(self):
        return f'<RolePermission role_id={self.role_id} permission_id={self.permission_id}>'