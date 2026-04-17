import uuid

from sqlalchemy import CHAR, Column, DateTime, String, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class IodPermission(db.Model):
    __tablename__ = 'iod_permissions'

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    app_code = Column(String(50), unique=True, nullable=False)
    app_name = Column(String(100), nullable=False)
    type = Column(TINYINT, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role_permissions = relationship(
        'IodRolePermission',
        primaryjoin='IodPermission.id == foreign(IodRolePermission.permission_id)',
        back_populates='permission',
        cascade='all, delete-orphan',
    )


class IodRolePermission(db.Model):
    __tablename__ = 'iod_role_permissions'

    role_id = Column(CHAR(36), primary_key=True, nullable=False, index=True)
    permission_id = Column(CHAR(36), primary_key=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role = relationship(
        'IodRole',
        primaryjoin='foreign(IodRolePermission.role_id) == IodRole.id',
        back_populates='role_permissions',
        viewonly=True,
    )
    permission = relationship(
        'IodPermission',
        primaryjoin='foreign(IodRolePermission.permission_id) == IodPermission.id',
        back_populates='role_permissions',
        viewonly=True,
    )


class IodUserDepartment(db.Model):
    __tablename__ = 'iod_user_departments'

    user_id = Column(CHAR(36), primary_key=True, nullable=False, index=True)
    dept_id = Column(CHAR(36), primary_key=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship(
        'IodUser',
        primaryjoin='foreign(IodUserDepartment.user_id) == IodUser.id',
        back_populates='user_departments',
        viewonly=True,
    )
    department = relationship(
        'IodDepartment',
        primaryjoin='foreign(IodUserDepartment.dept_id) == IodDepartment.id',
        back_populates='user_departments',
        viewonly=True,
    )


__all__ = ['IodPermission', 'IodRolePermission', 'IodUserDepartment']
