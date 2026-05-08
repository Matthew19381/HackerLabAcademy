def test_get_topic_vocabulary_nonexistent(client):
    response = client.get("/api/v1/vocabulary/topic/nonexistent-slug")
    assert response.status_code == 404


def test_get_topic_resources_nonexistent(client):
    response = client.get("/api/v1/vocabulary/topic/nonexistent-slug/resources")
    assert response.status_code == 404


def test_get_vocabulary_valid_topic(client):
    # Get a valid topic first
    user_resp = client.post("/api/v1/placement/user", json={"name": "Vocab User"})
    user_id = user_resp.json()["user_id"]

    topics_resp = client.get(f"/api/v1/topics/?user_id={user_id}")
    topics = topics_resp.json()
    if len(topics) >0:
        slug = topics[0]["slug"]
        response = client.get(f"/api/v1/vocabulary/topic/{slug}")
        # May return 200 with vocab or 400 if theory not generated
        assert response.status_code in [200, 400]
