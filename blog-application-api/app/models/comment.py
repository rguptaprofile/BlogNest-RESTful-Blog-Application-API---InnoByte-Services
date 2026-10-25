from datetime import datetime, timezone
from bson import ObjectId
from app.extensions import mongo
from .user import parse_object_id, User


class Comment:
    """MongoDB Comment Document Repository."""

    @staticmethod
    def create(post_id: str, content: str, author_id: str) -> dict:
        now = datetime.now(timezone.utc)
        comment_doc = {
            "post_id": str(post_id),
            "content": content.strip(),
            "author_id": str(author_id),
            "created_at": now,
        }
        res = mongo.comments.insert_one(comment_doc)
        comment_doc["_id"] = res.inserted_id
        return comment_doc

    @staticmethod
    def find_by_id(comment_id):
        oid = parse_object_id(comment_id)
        if not oid:
            return None
        return mongo.comments.find_one({"_id": oid})

    @staticmethod
    def find(filter_query=None, skip=0, limit=20):
        query = filter_query or {}
        cursor = mongo.comments.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def count(filter_query=None):
        return mongo.comments.count_documents(filter_query or {})

    @staticmethod
    def update_by_id(comment_id, updates: dict):
        oid = parse_object_id(comment_id)
        if not oid:
            return None
        mongo.comments.update_one({"_id": oid}, {"$set": updates})
        return mongo.comments.find_one({"_id": oid})

    @staticmethod
    def delete_by_id(comment_id) -> bool:
        oid = parse_object_id(comment_id)
        if not oid:
            return False
        res = mongo.comments.delete_one({"_id": oid})
        return res.deleted_count > 0

    @staticmethod
    def delete_by_post_id(post_id) -> int:
        res = mongo.comments.delete_many({"post_id": str(post_id)})
        return res.deleted_count

    @staticmethod
    def to_dict(comment_doc: dict) -> dict:
        if not comment_doc:
            return {}
        author = User.find_by_id(comment_doc.get("author_id"))
        created_at = comment_doc.get("created_at")
        return {
            "id": str(comment_doc.get("_id")),
            "post_id": str(comment_doc.get("post_id")),
            "content": comment_doc.get("content"),
            "author_id": str(comment_doc.get("author_id")),
            "author": author.get("username") if author else None,
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or ""),
        }
