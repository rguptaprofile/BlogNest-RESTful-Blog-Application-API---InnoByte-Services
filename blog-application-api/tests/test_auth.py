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


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
