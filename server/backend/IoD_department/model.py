import uuid

from sqlalchemy import CHAR, Column, DateTime, String, func, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship

from backend.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class IodDepartment(db.Model):
    __tablename__ = 'iod_departments'

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    dept_name = Column(String(100), unique=True, nullable=False)
    status = Column(TINYINT, nullable=False, server_default=text('1'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user_departments = relationship(
        'IodUserDepartment',
        primaryjoin='foreign(IodUserDepartment.dept_id) == IodDepartment.id',
        back_populates='department',
        cascade='all, delete-orphan',
    )


__all__ = ['IodDepartment']
