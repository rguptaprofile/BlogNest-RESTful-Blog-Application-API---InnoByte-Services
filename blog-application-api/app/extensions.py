import copy
from datetime import datetime, timezone
from bson import ObjectId
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

jwt = JWTManager()
cors = CORS()


class MockCursor:
    """Mock MongoDB cursor for test and offline execution."""
    def __init__(self, docs):
        self.docs = docs
        self._skip = 0
        self._limit = None

    def sort(self, key_or_list, direction=1):
        if isinstance(key_or_list, list):
            key = key_or_list[0][0]
            direction = key_or_list[0][1]
        else:
            key = key_or_list
        reverse = direction < 0
        self.docs.sort(key=lambda d: str(d.get(key) or ""), reverse=reverse)
        return self

    def skip(self, n):
        self._skip = n
        return self

    def limit(self, n):
        self._limit = n
        return self

    def __iter__(self):
        sliced = self.docs[self._skip:]
        if self._limit is not None:
            sliced = sliced[:self._limit]
        for d in sliced:
            yield copy.deepcopy(d)

    def __len__(self):
        return len(self.docs)


class MockCollection:
    """In-memory MongoDB collection for testing and instant offline fallback."""
    def __init__(self, name):
        self.name = name
        self.docs = []

    def _matches(self, doc, filter_query):
        if not filter_query:
            return True
        for k, v in filter_query.items():
            if k == "$or" and isinstance(v, list):
                if not any(self._matches(doc, cond) for cond in v):
                    return False
            elif str(doc.get(k)) != str(v):
                return False
        return True

    def find_one(self, filter_query=None):
        filter_query = filter_query or {}
        for d in self.docs:
            if self._matches(d, filter_query):
                return copy.deepcopy(d)
        return None

    def find(self, filter_query=None):
        filter_query = filter_query or {}
        matching = [copy.deepcopy(d) for d in self.docs if self._matches(d, filter_query)]
        return MockCursor(matching)

    def insert_one(self, doc):
        d = copy.deepcopy(doc)
        if "_id" not in d:
            d["_id"] = ObjectId()
        self.docs.append(d)

        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id

        return InsertResult(d["_id"])

    def update_one(self, filter_query, update_doc):
        matched = False
        modified = 0
        for d in self.docs:
            if self._matches(d, filter_query):
                matched = True
                if "$set" in update_doc:
                    for k, v in update_doc["$set"].items():
                        d[k] = copy.deepcopy(v)
                    modified = 1
                break

        class UpdateResult:
            def __init__(self, matched, modified):
                self.matched_count = 1 if matched else 0
                self.modified_count = modified

        return UpdateResult(matched, modified)

    def delete_one(self, filter_query):
        for i, d in enumerate(self.docs):
            if self._matches(d, filter_query):
                del self.docs[i]
                return type("DelResult", (), {"deleted_count": 1})()
        return type("DelResult", (), {"deleted_count": 0})()

    def delete_many(self, filter_query):
        initial = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, filter_query)]
        return type("DelResult", (), {"deleted_count": initial - len(self.docs)})()

    def count_documents(self, filter_query=None):
        filter_query = filter_query or {}
        return sum(1 for d in self.docs if self._matches(d, filter_query))

    def create_index(self, keys, **kwargs):
        return "index_created"

    def drop(self):
        self.docs = []


class MockDatabase:
    """In-memory MongoDB database."""
    def __init__(self, name="blognest_db"):
        self.name = name
        self.collections = {}

    def __getitem__(self, item):
        if item not in self.collections:
            self.collections[item] = MockCollection(item)
        return self.collections[item]

    def __getattr__(self, item):
        return self[item]

    def drop_collection(self, name):
        if name in self.collections:
            self.collections[name].drop()


class MongoDB:
    """MongoDB client wrapper with automatic live connection and offline fallback."""
    def __init__(self, app=None):
        self.client = None
        self.db = None
        self.is_fallback = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/blognest_db")
        mongo_dbname = app.config.get("MONGO_DBNAME", "blognest_db")

        if app.config.get("TESTING") or mongo_uri.startswith("mongodb://mock"):
            self.client = None
            self.db = MockDatabase(mongo_dbname)
            self.is_fallback = False
        else:
            try:
                self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
                # Test connection ping
                self.client.admin.command("ping")
                self.db = self.client[mongo_dbname]
                self.is_fallback = False
                print(f"[MongoDB] Successfully connected to live MongoDB at {mongo_uri}")
            except Exception as e:
                self.client = None
                self.db = MockDatabase(mongo_dbname)
                self.is_fallback = True
                print(f"[MongoDB] Live MongoDB not reachable ({e}). Using In-Memory MongoDB Store for instant preview!")
                self._seed_sample_data()

    def _seed_sample_data(self):
        now = datetime.now(timezone.utc)
        user_id = ObjectId("671b56a1e9447376c9682701")
        self.db["users"].insert_one({
            "_id": user_id,
            "username": "johndoe",
            "email": "john@example.com",
            "password": generate_password_hash("Password123!"),
            "created_at": now,
            "updated_at": now,
        })

        post1_id = ObjectId("671b56b3e9447376c9682702")
        self.db["posts"].insert_one({
            "_id": post1_id,
            "title": "Welcome to BlogNest - RESTful Blog Application API!",
            "content": "BlogNest is a high-performance blogging application API built with Flask, MongoDB, and JWT authentication. It provides full CRUD operations for posts, interactive commenting with cascade deletion, and full OpenAPI / Swagger documentation.",
            "author_id": str(user_id),
            "created_at": now,
            "updated_at": now,
        })

        post2_id = ObjectId("671b56b3e9447376c9682705")
        self.db["posts"].insert_one({
            "_id": post2_id,
            "title": "Mastering REST APIs with Python & MongoDB",
            "content": "Designing RESTful APIs requires clean separation of concerns, strong input validation, and robust role-based access control. MongoDB document collections provide flexible schemas that scale seamlessly.",
            "author_id": str(user_id),
            "created_at": now,
            "updated_at": now,
        })

        self.db["comments"].insert_one({
            "_id": ObjectId("671b56c0e9447376c9682703"),
            "post_id": str(post1_id),
            "content": "Incredible architecture and clean documentation!",
            "author_id": str(user_id),
            "created_at": now,
        })

    @property
    def users(self):
        return self.db["users"]

    @property
    def posts(self):
        return self.db["posts"]

    @property
    def comments(self):
        return self.db["comments"]


mongo = MongoDB()
