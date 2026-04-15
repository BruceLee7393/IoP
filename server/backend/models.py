import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from backend.extensions import bcrypt, db


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = 'iop_users'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    account = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(60), nullable=False)
    full_name = Column(String(64))
    contact_info = Column(String(32))
    address = Column(String(128))
    status = Column(
        Enum('active', 'disabled', name='iop_user_status'),
        nullable=False,
        default='active',
    )
    role_id = Column(String(36), ForeignKey('iop_roles.id', ondelete='SET NULL', onupdate='CASCADE'))
    extra_data = Column(JSON)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    gender = Column(Enum('woman', 'man', 'none', 'others', name='iop_user_gender'), default='none')

    role = relationship('Role', back_populates='users')

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode('utf-8')

    def verify_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)


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
