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
