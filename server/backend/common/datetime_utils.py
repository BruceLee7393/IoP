from __future__ import annotations

from datetime import datetime, timezone

from backend.common.exceptions import InvalidUsageError


_UTC = timezone.utc


def _from_unix_timestamp(value: float) -> datetime:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000_000_000:
        value = value / 1_000_000_000
    elif abs_value >= 1_000_000_000_000_000:
        value = value / 1_000_000
    elif abs_value >= 1_000_000_000_000:
        value = value / 1_000
    return datetime.fromtimestamp(value, tz=_UTC)


def _parse_datetime_string(value: str) -> datetime:
    normalized = value.strip()
    if not normalized:
        raise ValueError("empty datetime string")

    if normalized.isdigit() or (
        normalized.startswith("-") and normalized[1:].isdigit()
    ):
        return _from_unix_timestamp(float(normalized))

    iso_candidate = normalized.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate)
    except ValueError:
        pass

    fallback_formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    )
    for fmt in fallback_formats:
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue

    raise ValueError("unsupported datetime format")


def parse_to_utc_datetime(raw_value, field_name: str, required: bool = False):
    if raw_value is None:
        if required:
            raise InvalidUsageError(f"{field_name} 是必填项")
        return None

    if isinstance(raw_value, datetime):
        dt = raw_value
    elif isinstance(raw_value, (int, float)):
        dt = _from_unix_timestamp(float(raw_value))
    else:
        value = str(raw_value).strip()
        if not value:
            if required:
                raise InvalidUsageError(f"{field_name} 是必填项")
            return None
        try:
            dt = _parse_datetime_string(value)
        except ValueError as exc:
            raise InvalidUsageError(
                f"{field_name} 格式错误，需为时间戳或可解析的时间字符串"
            ) from exc

    if dt.tzinfo is None:
        # 对无时区时间按 UTC 解释，保证入库基准一致。
        dt = dt.replace(tzinfo=_UTC)

    return dt.astimezone(_UTC).replace(tzinfo=None)


def format_datetime_to_utc_z(value):
    if not value:
        return None

    if value.tzinfo is None:
        dt = value.replace(tzinfo=_UTC)
    else:
        dt = value.astimezone(_UTC)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
