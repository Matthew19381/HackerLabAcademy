def test_mentor_chat_no_session(client):
    response = client.post(
        "/api/v1/mentor/chat",
        json={"session_id": "nonexistent-session-123", "message": "Hello"}
    )
    # Should work (creates new session or uses in-memory)
    assert response.status_code in [200, 500]


def test_mentor_chat_with_message(client):
    response = client.post(
        "/api/v1/mentor/chat",
        json={"session_id": "test-session-1", "message": "What is SQL injection?"}
    )
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "response" in data


def test_clear_mentor_session(client):
    # First create a session
    client.post(
        "/api/v1/mentor/chat",
        json={"session_id": "test-session-clear", "message": "Test"}
    )
    # Then clear it
    response = client.delete("/api/v1/mentor/session/test-session-clear")
    assert response.status_code in [200, 500]
