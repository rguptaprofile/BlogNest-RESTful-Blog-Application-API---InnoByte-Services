from datetime import datetime, timezone
from bson import ObjectId
from app.extensions import mongo
from .user import parse_object_id, User


class Post:
    """MongoDB Blog Post Document Repository."""

    @staticmethod
    def create(title: str, content: str, author_id: str) -> dict:
        now = datetime.now(timezone.utc)
        post_doc = {
            "title": title.strip(),
            "content": content.strip(),
            "author_id": str(author_id),
            "created_at": now,
            "updated_at": now,
        }
        res = mongo.posts.insert_one(post_doc)
        post_doc["_id"] = res.inserted_id
        return post_doc

    @staticmethod
    def find_by_id(post_id):
        oid = parse_object_id(post_id)
        if not oid:
            return None
        return mongo.posts.find_one({"_id": oid})

    @staticmethod
    def find(filter_query=None, skip=0, limit=10):
        query = filter_query or {}
        cursor = mongo.posts.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def count(filter_query=None):
        return mongo.posts.count_documents(filter_query or {})

    @staticmethod
    def update_by_id(post_id, updates: dict):
        oid = parse_object_id(post_id)
        if not oid:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        mongo.posts.update_one({"_id": oid}, {"$set": updates})
        return mongo.posts.find_one({"_id": oid})

    @staticmethod
    def delete_by_id(post_id) -> bool:
        oid = parse_object_id(post_id)
        if not oid:
            return False
        res = mongo.posts.delete_one({"_id": oid})
        if res.deleted_count > 0:
            # Cascade delete associated comments
            mongo.comments.delete_many({"post_id": str(post_id)})
            return True
        return False

    @staticmethod
    def to_dict(post_doc: dict) -> dict:
        if not post_doc:
            return {}
        author = User.find_by_id(post_doc.get("author_id"))
        comments_count = mongo.comments.count_documents({"post_id": str(post_doc.get("_id"))})
        created_at = post_doc.get("created_at")
        updated_at = post_doc.get("updated_at")
        return {
            "id": str(post_doc.get("_id")),
            "title": post_doc.get("title"),
            "content": post_doc.get("content"),
            "author_id": str(post_doc.get("author_id")),
            "author": author.get("username") if author else None,
            "comments_count": comments_count,
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at or ""),
            "updated_at": updated_at.isoformat() if hasattr(updated_at, "isoformat") else str(updated_at or ""),
        }
