"""BlogNest — Database Initialization Script.

Project ID: SCR845NGFF
Configures MongoDB collections and unique indexes for users, posts, and comments.
Usage:
    python init_db.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "blog-application-api")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import create_app
from app.extensions import mongo


def init_database():
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        print(f"Connecting to MongoDB at: {app.config['MONGO_URI']}")
        print(f"Target Database: {app.config['MONGO_DBNAME']}")

        # 1. Users collection indexes
        mongo.users.create_index([("username", 1)], unique=True)
        mongo.users.create_index([("email", 1)], unique=True)
        print("  - Index created: users (username [unique], email [unique])")

        # 2. Posts collection indexes
        mongo.posts.create_index([("author_id", 1)])
        mongo.posts.create_index([("created_at", -1)])
        print("  - Index created: posts (author_id, created_at)")

        # 3. Comments collection indexes
        mongo.comments.create_index([("post_id", 1)])
        mongo.comments.create_index([("author_id", 1)])
        mongo.comments.create_index([("created_at", -1)])
        print("  - Index created: comments (post_id, author_id, created_at)")

        print("\nMongoDB database initialization complete! All collections & indexes are ready.")


if __name__ == "__main__":
    init_database()
