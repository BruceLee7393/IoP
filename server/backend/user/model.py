import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import relationship

from backend.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

    full_name = Column(String(64))
    status = Column(
        Enum('active', 'disabled', name='user_status'),
        nullable=False,
        default='active',
    )
    role_id = Column(String(36), ForeignKey('roles.id'))

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    role = relationship('Role')
