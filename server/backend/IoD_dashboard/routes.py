from flask import Blueprint

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoD_dashboard import service as dashboard_service


IoD_dashboard_bp = Blueprint('IoD_dashboard', __name__, url_prefix='/api/iod/dashboard')


@IoD_dashboard_bp.route('/overview', methods=['GET'])
@jwt_required
def get_overview():
    data = dashboard_service.get_overview_stats()
    return ok(data=data, message='获取仪表盘概览成功', status=200)
