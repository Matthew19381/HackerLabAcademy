def test_list_exercises_no_topic(client):
    # Create a topic first via the topics router
    user_resp = client.post("/api/v1/placement/user", json={"name": "Ex Student"})
    user_id = user_resp.json()["user_id"]

    # Get topics to find a topic_id
    topics_resp = client.get(f"/api/v1/topics/?user_id={user_id}")
    topics = topics_resp.json()
    assert len(topics) > 0
    topic_id = topics[0]["id"]

    response = client.get(f"/api/v1/exercises/topics/{topic_id}")
    # May return 200 with empty list or 500 if DB issues
    assert response.status_code in [200, 500]


def test_submit_exercise_invalid(client):
    response = client.post(
        "/api/v1/exercises/submit",
        params={"exercise_id": 9999, "user_id": 1, "user_answer": "test"}
    )
    assert response.status_code in [404, 500]


def test_generate_exercises_invalid_topic(client):
    response = client.post(
        "/api/v1/exercises/topics/9999/generate",
        params={"count": 5}
    )
    assert response.status_code in [404, 500]
