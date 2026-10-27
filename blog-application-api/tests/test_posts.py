def test_create_post(client, auth_headers):
    response = client.post(
        "/api/posts",
        headers=auth_headers,
        json={
            "title": "First Blog Post",
            "content": "This is the content of my first blog post.",
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["post"]["title"] == "First Blog Post"
    assert "author_id" in data["post"]


def test_get_posts(client, auth_headers):
    client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Post 1", "content": "Content 1"},
    )
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["posts"]) >= 1


def test_get_single_post(client, auth_headers):
    post_res = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Detail Post", "content": "Content here"},
    )
    post_id = post_res.get_json()["post"]["id"]

    response = client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200
    assert response.get_json()["post"]["title"] == "Detail Post"


def test_update_post(client, auth_headers):
    post_res = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Original Title", "content": "Original Content"},
    )
    post_id = post_res.get_json()["post"]["id"]

    update_res = client.put(
        f"/api/posts/{post_id}",
        headers=auth_headers,
        json={"title": "Updated Title"},
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["post"]["title"] == "Updated Title"


def test_delete_post(client, auth_headers):
    post_res = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "To Delete", "content": "Content to delete"},
    )
    post_id = post_res.get_json()["post"]["id"]

    del_res = client.delete(f"/api/posts/{post_id}", headers=auth_headers)
    assert del_res.status_code == 200

    get_res = client.get(f"/api/posts/{post_id}")
    assert get_res.status_code == 404


def test_create_post_unauthorized_and_validation(client, auth_headers):
    # 401 when no token is passed
    res_unauth = client.post("/posts", json={"title": "Test", "content": "Test"})
    assert res_unauth.status_code == 401

    # 400 when title or content is missing/empty
    res_empty_title = client.post("/posts", headers=auth_headers, json={"title": "", "content": "Valid Content"})
    assert res_empty_title.status_code == 400

    res_empty_content = client.post("/posts", headers=auth_headers, json={"title": "Valid Title", "content": ""})
    assert res_empty_content.status_code == 400


def test_post_rbac_and_not_found(client, auth_headers):
    # Create post with User 1
    post_res = client.post(
        "/posts",
        headers=auth_headers,
        json={"title": "User 1 Post", "content": "Content"},
    )
    post_id = post_res.get_json()["post"]["id"]

    # Register User 2
    reg2 = client.post(
        "/register",
        json={"username": "user2", "email": "user2@example.com", "password": "Password123!"},
    )
    token2 = reg2.get_json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 attempts to update User 1's post -> 403 Forbidden
    res_update = client.put(f"/posts/{post_id}", headers=headers2, json={"title": "Hacked Title"})
    assert res_update.status_code == 403

    # User 2 attempts to delete User 1's post -> 403 Forbidden
    res_delete = client.delete(f"/posts/{post_id}", headers=headers2)
    assert res_delete.status_code == 403

    # 404 for non-existent post
    res_404 = client.get("/posts/000000000000000000000000")
    assert res_404.status_code == 404

    # 400 for invalid post id format
    res_400 = client.get("/posts/invalid-id")
    assert res_400.status_code == 400
