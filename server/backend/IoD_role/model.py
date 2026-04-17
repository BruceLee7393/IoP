import uuid

from sqlalchemy import Boolean, CHAR, Column, DateTime, String, func, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class IodRole(db.Model):
    __tablename__ = 'iod_roles'

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_preset = Column(Boolean, nullable=False, server_default=text('0'))
    status = Column(TINYINT, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    users = relationship(
        'IodUser',
        primaryjoin='foreign(IodUser.role_id) == IodRole.id',
        back_populates='role',
    )
    role_permissions = relationship(
        'IodRolePermission',
        primaryjoin='foreign(IodRolePermission.role_id) == IodRole.id',
        back_populates='role',
        cascade='all, delete-orphan',
    )


__all__ = ['IodRole']
