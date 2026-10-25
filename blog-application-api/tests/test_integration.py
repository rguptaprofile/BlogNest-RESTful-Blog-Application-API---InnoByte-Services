"""Integration tests verifying complete end-to-end user journeys and component interactions.

Project ID: SCR845NGFF
"""
import pytest


def test_full_blog_lifecycle_integration(client):
    """Verifies complete end-to-end journey:
    1. Register Author (User A) and Reader (User B)
    2. Authenticate both users and acquire JWT tokens
    3. Author creates a post
    4. Reader views the post list and single post
    5. Reader adds a comment to the post
    6. Author also adds a comment to their own post
    7. Reader filters comments by post_id
    8. Reader updates their comment
    9. Author attempts to edit Reader's comment (Forbidden 403)
    10. Reader attempts to edit Author's post (Forbidden 403)
    11. Author updates post
    12. Author deletes post
    13. Verify post is gone and comments are cascade-deleted
    """
    # 1. Register User A and User B
    reg_a = client.post("/register", json={
        "username": "author_user",
        "email": "author@example.com",
        "password": "Password123!"
    })
    assert reg_a.status_code == 201

    reg_b = client.post("/register", json={
        "username": "reader_user",
        "email": "reader@example.com",
        "password": "Password123!"
    })
    assert reg_b.status_code == 201

    # 2. Login both users
    login_a = client.post("/login", json={
        "email": "author@example.com",
        "password": "Password123!"
    })
    assert login_a.status_code == 200
    token_a = login_a.get_json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    login_b = client.post("/login", json={
        "email": "reader@example.com",
        "password": "Password123!"
    })
    assert login_b.status_code == 200
    token_b = login_b.get_json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Author creates a post
    create_post_res = client.post("/posts", headers=headers_a, json={
        "title": "Mastering REST APIs with MongoDB",
        "content": "Deep dive into schema design, indexing, and authentication."
    })
    assert create_post_res.status_code == 201
    post_id = create_post_res.get_json()["post"]["id"]

    # 4. Reader views post list and the created post
    posts_list_res = client.get("/posts")
    assert posts_list_res.status_code == 200
    assert any(p["id"] == post_id for p in posts_list_res.get_json()["posts"])

    get_post_res = client.get(f"/posts/{post_id}")
    assert get_post_res.status_code == 200
    assert get_post_res.get_json()["post"]["title"] == "Mastering REST APIs with MongoDB"

    # 5. Reader creates a comment
    comment_b_res = client.post("/comments", headers=headers_b, json={
        "post_id": post_id,
        "content": "Brilliant writeup! Really helped me understand MongoDB."
    })
    assert comment_b_res.status_code == 201
    comment_b_id = comment_b_res.get_json()["comment"]["id"]

    # 6. Author adds a reply comment
    comment_a_res = client.post("/comments", headers=headers_a, json={
        "post_id": post_id,
        "content": "Thanks for reading, reader_user!"
    })
    assert comment_a_res.status_code == 201

    # 7. Reader queries comments for post
    query_comments_res = client.get(f"/comments?post_id={post_id}")
    assert query_comments_res.status_code == 200
    comments_list = query_comments_res.get_json()["comments"]
    assert len(comments_list) == 2

    # 8. Reader updates their comment
    update_comment_res = client.put(f"/comments/{comment_b_id}", headers=headers_b, json={
        "content": "Updated: Truly brilliant writeup!"
    })
    assert update_comment_res.status_code == 200
    assert update_comment_res.get_json()["comment"]["content"] == "Updated: Truly brilliant writeup!"

    # 9. Role-based check: Author attempts to update Reader's comment (Forbidden 403)
    unauthorized_comment_edit = client.put(f"/comments/{comment_b_id}", headers=headers_a, json={
        "content": "Malicious edit attempt"
    })
    assert unauthorized_comment_edit.status_code == 403

    # 10. Role-based check: Reader attempts to update Author's post (Forbidden 403)
    unauthorized_post_edit = client.put(f"/posts/{post_id}", headers=headers_b, json={
        "title": "Hacked Title"
    })
    assert unauthorized_post_edit.status_code == 403

    # 11. Author updates their post
    update_post_res = client.put(f"/posts/{post_id}", headers=headers_a, json={
        "title": "Mastering REST APIs with MongoDB (2nd Edition)"
    })
    assert update_post_res.status_code == 200
    assert update_post_res.get_json()["post"]["title"] == "Mastering REST APIs with MongoDB (2nd Edition)"

    # 12. Author deletes their post
    delete_post_res = client.delete(f"/posts/{post_id}", headers=headers_a)
    assert delete_post_res.status_code == 200

    # 13. Verify post is 404 and comments are cascade-deleted
    verify_post_gone = client.get(f"/posts/{post_id}")
    assert verify_post_gone.status_code == 404

    verify_comments_gone = client.get(f"/comments?post_id={post_id}")
    assert len(verify_comments_gone.get_json()["comments"]) == 0
