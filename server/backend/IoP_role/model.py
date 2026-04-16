import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class Role(db.Model):
    __tablename__ = 'iop_roles'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_code = Column(String(32), unique=True, nullable=False)
    role_name = Column(String(64), nullable=False)
    description = Column(String(255))
    status = Column(
        Enum('active', 'disabled', name='iop_role_status'),
        nullable=False,
        default='active',
    )
    extra_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    users = relationship('User', back_populates='role')
    role_permissions = relationship(
        'RoleMappingPermission',
        back_populates='role',
        cascade='all, delete-orphan',
    )


class Permission(db.Model):
    __tablename__ = 'iop_permissions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    permission_code = Column(String(64), unique=True, nullable=False)
    permission_name = Column(String(64), nullable=False)
    description = Column(String(255))

    role_permissions = relationship(
        'RoleMappingPermission',
        back_populates='permission',
        cascade='all, delete-orphan',
    )


class RoleMappingPermission(db.Model):
    __tablename__ = 'iop_role_mapping_permissions'
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_iop_role_permission'),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(
        String(36),
        ForeignKey('iop_roles.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )
    permission_id = Column(
        String(36),
        ForeignKey('iop_permissions.id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False,
        index=True,
    )

    role = relationship('Role', back_populates='role_permissions')
    permission = relationship('Permission', back_populates='role_permissions')


__all__ = ['Role', 'Permission', 'RoleMappingPermission']
