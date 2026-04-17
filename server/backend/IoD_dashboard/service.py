from sqlalchemy import func

from backend.IoD_role.model import IodRole
from backend.IoD_user.model import IodUser
from backend.extensions import db


def get_overview_stats():
    total_users = db.session.query(func.count(IodUser.id)).scalar() or 0
    total_roles = db.session.query(func.count(IodRole.id)).scalar() or 0
    enabled_users = db.session.query(func.count(IodUser.id)).filter(IodUser.status == 1).scalar() or 0

    return {
        'total_users': int(total_users),
        'total_roles': int(total_roles),
        'enabled_users': int(enabled_users),
    }
