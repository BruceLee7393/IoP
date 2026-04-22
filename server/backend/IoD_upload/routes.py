from flask import Blueprint, request

from backend.common.auth import jwt_required
from backend.common.response import ok
from backend.IoD_upload.dao import get_upload_list


IoD_upload_bp = Blueprint("IoD_upload", __name__, url_prefix="/api/iod")


@IoD_upload_bp.route("/upload-records", methods=["GET"])
@jwt_required
def list_upload_records():
    data = get_upload_list(request.args)
    return ok(data=data, message="获取设备上传记录成功", status=200)
