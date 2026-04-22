from datetime import datetime

from backend.common.exceptions import InvalidUsageError
from backend.extensions import db
from backend.IoD_upload.model import IoD_upload


def _format_datetime(value):
    if not value:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _upload_item_to_dict(item):
    return {
        "id": item.id,
        "device_id": item.device_id,
        "event_type": item.event_type,
        "event_record": item.event_record,
        "upload_status": item.upload_status,
        "retry_count": item.retry_count,
        "event_time": _format_datetime(item.event_time),
        "last_upload_time": _format_datetime(item.last_upload_time),
        "ack_time": _format_datetime(item.ack_time),
    }


def _parse_event_time(raw_value):
    if isinstance(raw_value, datetime):
        return raw_value

    value = str(raw_value or "").strip()
    if not value:
        raise InvalidUsageError("event_time 是必填项")

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise InvalidUsageError("event_time 格式错误，需为 ISO 时间格式") from exc


def insert_upload_record(payload):
    if not isinstance(payload, dict):
        raise InvalidUsageError("payload 必须是 JSON 对象")

    device_id = str(payload.get("device_id", "")).strip()
    if not device_id:
        raise InvalidUsageError("device_id 是必填项")

    event_type = payload.get("event_type")
    if event_type is None:
        raise InvalidUsageError("event_type 是必填项")

    try:
        event_type = int(event_type)
    except (TypeError, ValueError) as exc:
        raise InvalidUsageError("event_type 必须是整数") from exc

    upload_status = payload.get("upload_status", 0)
    try:
        upload_status = int(upload_status)
    except (TypeError, ValueError) as exc:
        raise InvalidUsageError("upload_status 必须是整数") from exc

    if upload_status not in {0, 1}:
        raise InvalidUsageError("upload_status 仅支持 0 或 1")

    retry_count = payload.get("retry_count", 0)
    try:
        retry_count = int(retry_count)
    except (TypeError, ValueError) as exc:
        raise InvalidUsageError("retry_count 必须是整数") from exc

    event_record = payload.get("event_record")
    if event_record is None:
        raise InvalidUsageError("event_record 是必填项")

    event_time = _parse_event_time(payload.get("event_time"))

    entity = IoD_upload(
        device_id=device_id,
        event_type=event_type,
        event_record=event_record,
        upload_status=upload_status,
        retry_count=retry_count,
        event_time=event_time,
    )
    try:
        db.session.add(entity)
        db.session.commit()
        db.session.refresh(entity)
    except Exception:
        db.session.rollback()
        raise
    return _upload_item_to_dict(entity)


def get_upload_list(query_args):
    page = query_args.get("page", 1, type=int)
    size = query_args.get("size", 10, type=int)
    device_id = query_args.get("device_id", type=str)
    upload_status = query_args.get("upload_status", type=int)

    if page <= 0 or size <= 0:
        raise InvalidUsageError("page 和 size 必须大于 0")
    if upload_status is not None and upload_status not in {0, 1}:
        raise InvalidUsageError("upload_status 仅支持 0 或 1")

    query = IoD_upload.query
    if device_id:
        query = query.filter(IoD_upload.device_id == device_id)
    if upload_status is not None:
        query = query.filter(IoD_upload.upload_status == upload_status)

    paged = query.order_by(IoD_upload.event_time.desc()).paginate(
        page=page,
        per_page=size,
        error_out=False,
    )

    return {
        "total": paged.total,
        "items": [_upload_item_to_dict(item) for item in paged.items],
        "page": paged.page,
        "size": paged.per_page,
    }
