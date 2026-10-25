from datetime import datetime, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import mongo


def parse_object_id(val):
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(str(val))
    except Exception:
        return None


class User:
    """MongoDB User Document Repository."""

    @staticmethod
    def create(username: str, email: str, raw_password: str) -> dict:
        now = datetime.now(timezone.utc)
        user_doc = {
            "username": username.strip(),
            "email": email.strip().lower(),
            "password": generate_password_hash(raw_password),
            "created_at": now,
            "updated_at": now,
        }
        res = mongo.users.insert_one(user_doc)
        user_doc["_id"] = res.inserted_id
        return user_doc

    @staticmethod
    def find_by_id(user_id):
        oid = parse_object_id(user_id)
        if not oid:
            return None
        return mongo.users.find_one({"_id": oid})

    @staticmethod
    def find_by_username(username: str):
        return mongo.users.find_one({"username": username.strip()})

    @staticmethod
    def find_by_email(email: str):
        return mongo.users.find_one({"email": email.strip().lower()})

    @staticmethod
    def check_password(user_doc: dict, raw_password: str) -> bool:
        if not user_doc or "password" not in user_doc:
            return False
        return check_password_hash(user_doc["password"], raw_password)

    @staticmethod
    def to_dict(user_doc: dict) -> dict:
        if not user_doc:
            return {}
        created_at = user_doc.get("created_at")
        updated_at = user_doc.get("updated_at")
        return {
            "id": str(user_doc.get("_id")),
            "username": user_doc.get("username"),
            "email": user_doc.get("email"),
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or ""),
            "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else str(updated_at or ""),
        }
