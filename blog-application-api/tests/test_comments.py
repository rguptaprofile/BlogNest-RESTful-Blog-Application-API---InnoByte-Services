def test_add_comment_under_post(client, auth_headers):
    post_res = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Commentable Post", "content": "Post content"},
    )
    post_id = post_res.get_json()["post"]["id"]

    comment_res = client.post(
        f"/api/posts/{post_id}/comments",
        headers=auth_headers,
        json={"content": "Great article!"},
    )
    assert comment_res.status_code == 201
    assert comment_res.get_json()["comment"]["content"] == "Great article!"
    assert comment_res.get_json()["comment"]["author_id"] is not None


def test_create_comment_standalone_endpoint(client, auth_headers):
    post_res = client.post(
        "/api/posts",
        headers=auth_headers,
        json={"title": "Standalone Test", "content": "Post content"},
    )
    post_id = post_res.get_json()["post"]["id"]

    comment_res = client.post(
        "/api/comments",
        headers=auth_headers,
        json={"post_id": post_id, "content": "Comment via /comments"},
    )
    assert comment_res.status_code == 201
    comment_id = comment_res.get_json()["comment"]["id"]

    # Test GET /api/comments/{id}
    get_res = client.get(f"/api/comments/{comment_id}")
    assert get_res.status_code == 200
    assert get_res.get_json()["comment"]["content"] == "Comment via /comments"

    # Test GET /api/comments?post_id=...
    list_res = client.get(f"/api/comments?post_id={post_id}")
    assert list_res.status_code == 200
    assert len(list_res.get_json()["comments"]) >= 1

    # Test PUT /api/comments/{id}
    put_res = client.put(
        f"/api/comments/{comment_id}",
        headers=auth_headers,
        json={"content": "Updated comment content"},
    )
    assert put_res.status_code == 200
    assert put_res.get_json()["comment"]["content"] == "Updated comment content"

    # Test DELETE /api/comments/{id}
    del_res = client.delete(f"/api/comments/{comment_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Ensure deleted
    get_again = client.get(f"/api/comments/{comment_id}")
    assert get_again.status_code == 404


def test_comment_validation_and_unauthorized(client, auth_headers):
    # 401 when creating comment without token
    res_unauth = client.post("/comments", json={"post_id": "671b56b3e9447376c9682702", "content": "Hello"})
    assert res_unauth.status_code == 401

    # 400 when missing post_id or content
    res_no_post_id = client.post("/comments", headers=auth_headers, json={"content": "No post ID"})
    assert res_no_post_id.status_code == 400

    res_no_content = client.post("/comments", headers=auth_headers, json={"post_id": "671b56b3e9447376c9682702", "content": ""})
    assert res_no_content.status_code == 400

    # 404 when referencing non-existent post
    res_fake_post = client.post("/comments", headers=auth_headers, json={"post_id": "000000000000000000000000", "content": "Fake post comment"})
    assert res_fake_post.status_code == 404


def test_comment_rbac_and_errors(client, auth_headers):
    # Create a post
    post_res = client.post("/posts", headers=auth_headers, json={"title": "Test Post", "content": "Content"})
    post_id = post_res.get_json()["post"]["id"]

    # User 1 creates comment
    c_res = client.post("/comments", headers=auth_headers, json={"post_id": post_id, "content": "User 1 Comment"})
    comment_id = c_res.get_json()["comment"]["id"]

    # Register User 2
    reg2 = client.post("/register", json={"username": "user2_c", "email": "user2_c@example.com", "password": "Password123!"})
    token2 = reg2.get_json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 attempts to edit User 1's comment -> 403 Forbidden
    res_edit_forbidden = client.put(f"/comments/{comment_id}", headers=headers2, json={"content": "Hacked comment"})
    assert res_edit_forbidden.status_code == 403

    # User 2 attempts to delete User 1's comment -> 403 Forbidden
    res_del_forbidden = client.delete(f"/comments/{comment_id}", headers=headers2)
    assert res_del_forbidden.status_code == 403

    # 404 for non-existent comment
    res_404 = client.get("/comments/000000000000000000000000")
    assert res_404.status_code == 404

    # 400 for invalid comment ID format
    res_400 = client.get("/comments/invalid-id")
    assert res_400.status_code == 400
