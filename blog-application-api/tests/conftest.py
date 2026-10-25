import os
import sys
import pytest

# Ensure blog-application-api root is always in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.extensions import mongo


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        # Clear mock collections before and after test runs
        mongo.users.drop()
        mongo.posts.drop()
        mongo.comments.drop()

        yield app

        mongo.users.drop()
        mongo.posts.drop()
        mongo.comments.drop()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Fixture that registers and logs in a test user, returning JWT auth headers."""
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "Password123!",
        },
    )
    token = login_res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
