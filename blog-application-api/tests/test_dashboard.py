"""Tests for Dashboard Service and Analytics Endpoints.

Verifies that server-side Python calculations correctly compute metrics,
word counts, reading times, response tallies, and author standing.
"""
import pytest


def test_dashboard_unauthorized(client):
    """Ensure dashboard endpoint rejects unauthenticated access."""
    res = client.get("/api/dashboard/me")
    assert res.status_code == 401


def test_dashboard_authenticated_metrics_calculated_in_python(client):
    """Ensure Python computes accurate analytics, word counts, and author tier."""
    # 1. Register an author
    reg = client.post("/register", json={
        "username": "dash_author",
        "email": "dash_author@example.com",
        "password": "Password123!"
    })
    assert reg.status_code == 201
    token = reg.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check initial dashboard (empty author)
    res_initial = client.get("/api/dashboard/me", headers=headers)
    assert res_initial.status_code == 200
    data_initial = res_initial.get_json()["dashboard"]

    assert data_initial["user"]["username"] == "dash_author"
    assert data_initial["metrics"]["total_stories"] == 0
    assert data_initial["metrics"]["total_words"] == 0
    assert data_initial["metrics"]["total_responses_received"] == 0
    assert data_initial["user"]["author_tier"] == "Emerging Tech Scribe"

    # 3. Publish a rich technical story
    story_content = "Python 3.13 introduces significant concurrency improvements and free-threaded execution modes for high-throughput backends."
    post_res = client.post("/posts", headers=headers, json={
        "title": "Exploring Python 3.13 Concurrency Patterns",
        "content": story_content
    })
    assert post_res.status_code == 201
    post_id = post_res.get_json()["post"]["id"]

    # 4. Another user leaves a response
    reg_reader = client.post("/register", json={
        "username": "dash_reader",
        "email": "dash_reader@example.com",
        "password": "Password123!"
    })
    reader_token = reg_reader.get_json()["access_token"]
    reader_headers = {"Authorization": f"Bearer {reader_token}"}

    comment_res = client.post("/comments", headers=reader_headers, json={
        "post_id": post_id,
        "content": "Outstanding explanation of GIL-free Python execution!"
    })
    assert comment_res.status_code == 201

    # 5. Author writes a comment on another post
    author_comment_res = client.post("/comments", headers=headers, json={
        "post_id": post_id,
        "content": "Thank you for the thoughtful feedback!"
    })
    assert author_comment_res.status_code == 201

    # 6. Fetch updated dashboard and verify Python calculations
    res_updated = client.get("/api/dashboard/me", headers=headers)
    assert res_updated.status_code == 200
    data = res_updated.get_json()["dashboard"]

    # Assertions on Python server-computed values
    metrics = data["metrics"]
    assert metrics["total_stories"] == 1
    assert metrics["total_words"] == len(story_content.split())
    assert metrics["total_reading_time_minutes"] >= 1
    assert metrics["total_responses_received"] == 2  # Reader's comment + Author's comment on author's post
    assert metrics["total_responses_written"] == 1   # Author wrote 1 comment
    assert metrics["engagement_score"] > 0

    # Verify story enrichment by Python
    stories = data["stories"]
    assert len(stories) == 1
    assert stories[0]["topic"] == "Python"
    assert stories[0]["word_count"] == len(story_content.split())
    assert "relative_time" in stories[0]

    # Verify comments enrichment by Python
    comments = data["comments"]
    assert len(comments) == 1
    assert comments[0]["post_title"] == "Exploring Python 3.13 Concurrency Patterns"

    # Verify unified activity stream in Python
    activity = data["recent_activity"]
    assert len(activity) >= 2


def test_platform_metrics_endpoint(client, auth_headers):
    """Verify platform-wide statistics endpoint computed in Python."""
    # Seed a post to ensure count >= 1
    client.post("/posts", headers=auth_headers, json={
        "title": "Platform Analytics Baseline",
        "content": "Ensures platform metrics accurately aggregate live posts."
    })

    res = client.get("/api/dashboard/platform")
    assert res.status_code == 200
    data = res.get_json()["platform"]
    assert "total_users" in data
    assert "total_posts" in data
    assert "total_comments" in data
    assert data["total_posts"] >= 1
