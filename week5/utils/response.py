from datetime import datetime, timezone
from flask import jsonify


def api_response(data=None, metadata=None, status_code=200):
    """
    API response chuẩn luôn có metadata.

    - data: dữ liệu chính (object hoặc list)
    - metadata: thông tin bổ sung (timestamp, pagination, ...)
    """
    now = datetime.now(timezone.utc).isoformat()
    base_meta = {
        "timestamp": now,
        "success": 200 <= status_code < 300,
    }
    if metadata:
        base_meta.update(metadata)
    return jsonify({
        "data": data,
        "metadata": base_meta,
    }), status_code


def api_error(message: str, status_code=400, metadata=None):
    """Response khi lỗi, vẫn có metadata."""
    now = datetime.now(timezone.utc).isoformat()
    base_meta = {
        "timestamp": now,
        "success": False,
    }
    if metadata:
        base_meta.update(metadata)
    return jsonify({
        "data": None,
        "error": message,
        "metadata": base_meta,
    }), status_code
