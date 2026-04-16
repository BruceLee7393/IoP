import uuid

from sqlalchemy import Column, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class Permission(db.Model):
    __tablename__ = 'iop_permissions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    permission_code = Column(String(64), unique=True, nullable=False)
    permission_name = Column(String(64), nullable=False)
    description = Column(String(255))

    role_mappings = relationship(
        'RoleMappingPermission',
        primaryjoin='Permission.id == foreign(RoleMappingPermission.permission_id)',
        back_populates='permission',
        cascade='all, delete-orphan',
    )


class RoleMappingPermission(db.Model):
    __tablename__ = 'iop_role_mapping_permissions'
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_iop_role_permission'),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(String(36), nullable=False, index=True)
    permission_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Use string-based joins to avoid physical FKs and circular imports.
    role = relationship(
        'Role',
        primaryjoin='foreign(RoleMappingPermission.role_id) == Role.id',
        viewonly=True,
    )
    permission = relationship(
        'Permission',
        primaryjoin='foreign(RoleMappingPermission.permission_id) == Permission.id',
        back_populates='role_mappings',
    )


__all__ = ['Permission', 'RoleMappingPermission']