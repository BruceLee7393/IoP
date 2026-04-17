import uuid

from sqlalchemy import CHAR, Column, DateTime, String, func, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class IodUser(db.Model):
    __tablename__ = 'iod_users'

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    user_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(CHAR(36), nullable=True, index=True)
    nfc_uid = Column(String(100), unique=True, nullable=True)
    status = Column(TINYINT, nullable=False, server_default=text('1'))
    creditor_name = Column(String(100), nullable=True)
    bic = Column(String(11), nullable=True)
    iban = Column(String(34), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role = relationship(
        'IodRole',
        primaryjoin='foreign(IodUser.role_id) == IodRole.id',
        back_populates='users',
    )
    user_departments = relationship(
        'IodUserDepartment',
        primaryjoin='foreign(IodUserDepartment.user_id) == IodUser.id',
        back_populates='user',
        cascade='all, delete-orphan',
    )


__all__ = ['IodUser']
