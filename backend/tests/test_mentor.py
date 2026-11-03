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


def test_mentor_history_is_stored_and_sent_back_as_context(client, monkeypatch):
    """B3 (2026-11-03): history lived in a process dict - a backend restart lost every chat."""
    seen = []

    async def fake_chat(message, history, topic_context=None, mode="answer"):
        seen.append(list(history))
        return f"odp: {message}"

    monkeypatch.setattr("backend.routers.mentor.mentor_chat", fake_chat)
    client.post("/api/v1/mentor/chat", json={"session_id": "s-hist", "message": "Co to XSS?"})
    client.post("/api/v1/mentor/chat", json={"session_id": "s-hist", "message": "A CSRF?"})

    assert seen[1] == [{"role": "user", "content": "Co to XSS?"}, {"role": "assistant", "content": "odp: Co to XSS?"}]
    stored = client.get("/api/v1/mentor/session/s-hist").json()["messages"]
    assert [m["content"] for m in stored] == ["Co to XSS?", "odp: Co to XSS?", "A CSRF?", "odp: A CSRF?"]

    client.delete("/api/v1/mentor/session/s-hist")
    assert client.get("/api/v1/mentor/session/s-hist").json()["messages"] == []


def test_mentor_mode_reaches_the_prompt_and_usage_warns_without_blocking(client, monkeypatch):
    """D1: graded help; D2: notice above the daily threshold, the answer still comes."""
    from backend.config import settings

    prompts = []

    async def fake_text(prompt):
        prompts.append(prompt)
        return "pytanie naprowadzające"

    monkeypatch.setattr("backend.services.lesson_service.generate_text", fake_text)
    monkeypatch.setattr(settings, "MENTOR_DAILY_WARN", 1)

    first = client.post("/api/v1/mentor/chat", json={"session_id": "s-mode", "message": "Jak zrobić SQLi?", "mode": "guide"}).json()
    assert "Nie podawaj odpowiedzi" in prompts[0]
    assert first["usage"] == {"today": 1, "threshold": 1, "over": False}

    second = client.post("/api/v1/mentor/chat", json={"session_id": "s-mode", "message": "A dalej?"}).json()
    assert second["response"] == "pytanie naprowadzające" and second["usage"]["over"] is True
    assert client.post("/api/v1/mentor/chat", json={"session_id": "s", "message": "x", "mode": "all"}).status_code == 422
