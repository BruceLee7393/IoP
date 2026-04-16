import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, JSON, String, func
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


__all__ = ['User']
