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
