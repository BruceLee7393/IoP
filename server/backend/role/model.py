from sqlalchemy import Column, String

from backend.extensions import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = Column(String(36), primary_key=True)
    role_name = Column(String(64), nullable=False)
    status = Column(String(16), nullable=False, default='active')
