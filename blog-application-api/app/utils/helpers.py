import re
from bson import ObjectId
from flask import jsonify


def is_valid_object_id(val: str) -> bool:
    """Validate whether a string is a 24-character hexadecimal ObjectId."""
    if not val or not isinstance(val, (str, ObjectId)):
        return False
    if isinstance(val, ObjectId):
        return True
    return bool(re.fullmatch(r"[0-9a-fA-F]{24}", str(val)))


def parse_object_id(val):
    """Safely convert a string to bson.ObjectId or return None."""
    if isinstance(val, ObjectId):
        return val
    try:
        if is_valid_object_id(val):
            return ObjectId(str(val))
    except Exception:
        pass
    return None


def error_response(message: str, status_code: int = 400, details=None):
    """Generate standardized error JSON response."""
    payload = {"error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


def success_response(data=None, message: str = None, status_code: int = 200, **kwargs):
    """Generate standardized success JSON response."""
    payload = {}
    if message:
        payload["message"] = message
    if data is not None:
        if isinstance(data, dict):
            payload.update(data)
        else:
            payload["data"] = data
    payload.update(kwargs)
    return jsonify(payload), status_code
