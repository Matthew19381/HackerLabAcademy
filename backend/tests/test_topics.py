def test_list_topics(client):
    # Create user first
    user_resp = client.post("/api/v1/placement/user", json={"name": "Topic User"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/topics/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check topic structure
    topic = data[0]
    assert "slug" in topic
    assert "name" in topic
    assert "category" in topic
    assert "difficulty" in topic


def test_get_topic_theory(client):
    # First get list to find a slug
    user_resp = client.post("/api/v1/placement/user", json={"name": "Topic Reader"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/topics/?user_id={user_id}")
    topics = response.json()
    assert len(topics) > 0
    slug = topics[0]["slug"]

    # Get theory (this is how you get topic detail)
    response = client.get(f"/api/v1/topics/{slug}/theory?user_id={user_id}")
    # May return 200 with content or 503 if Gemini fails
    assert response.status_code in [200, 503]


def test_get_nonexistent_topic(client):
    user_resp = client.post("/api/v1/placement/user", json={"name": "Test"})
    user_id = user_resp.json()["user_id"]

    response = client.get(f"/api/v1/topics/nonexistent-slug-123/theory?user_id={user_id}")
    assert response.status_code == 404


def test_get_topic_progress_no_user(client):
    response = client.get("/api/v1/topics/http-basics/progress/9999")
    assert response.status_code == 404
