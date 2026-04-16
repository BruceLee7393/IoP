import uuid

from sqlalchemy import Column, DateTime, Enum, JSON, String, func
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
__all__ = ['Role']
