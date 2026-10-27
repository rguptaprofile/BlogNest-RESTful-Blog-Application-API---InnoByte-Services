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
