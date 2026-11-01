def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "securepassword",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "johndoe"


def test_register_duplicate_username(client):
    payload = {
        "username": "janedoe",
        "email": "jane@example.com",
        "password": "securepassword",
    }
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "mypassword",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_register_validation_errors(client):
    # Missing username
    res = client.post("/register", json={"email": "valid@example.com", "password": "password123"})
    assert res.status_code == 400

    # Invalid email format
    res = client.post("/register", json={"username": "testuser", "email": "invalid-email", "password": "password123"})
    assert res.status_code == 400

    # Password too short (< 6 chars)
    res = client.post("/register", json={"username": "testuser", "email": "valid@example.com", "password": "123"})
    assert res.status_code == 400


def test_login_with_username(client):
    client.post(
        "/register",
        json={
            "username": "bobuser",
            "email": "bob@example.com",
            "password": "Password123!",
        },
    )
    # Login using username instead of email
    response = client.post(
        "/login",
        json={"username": "bobuser", "password": "Password123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_get_current_user_profile(client):
    reg = client.post(
        "/register",
        json={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "Password123!",
        },
    )
    token = reg.get_json()["access_token"]

    # 401 without token
    res_no_auth = client.get("/me")
    assert res_no_auth.status_code == 401

    # 200 with valid token
    res_auth = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200
    assert res_auth.get_json()["user"]["username"] == "profileuser"


def test_update_user_profile_picture_and_bio(client):
    reg = client.post(
        "/register",
        json={
            "username": "avatar_user",
            "email": "avatar@example.com",
            "password": "Password123!",
        },
    )
    token = reg.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 401 unauthorized
    res_unauth = client.put("/me", json={"avatar_url": "https://example.com/pic.png"})
    assert res_unauth.status_code == 401

    # 200 update avatar and bio
    res_update = client.put(
        "/me",
        headers=headers,
        json={
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
            "bio": "Staff Systems Architect and Technical Writer.",
        },
    )
    assert res_update.status_code == 200
    user_data = res_update.get_json()["user"]
    assert user_data["avatar_url"] == "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
    assert user_data["bio"] == "Staff Systems Architect and Technical Writer."

    # Verify updated profile on GET /me
    res_get = client.get("/me", headers=headers)
    assert res_get.status_code == 200
    assert res_get.get_json()["user"]["avatar_url"] == "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
