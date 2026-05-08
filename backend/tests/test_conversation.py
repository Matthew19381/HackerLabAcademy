def test_start_conversation_invalid_user(client):
    response = client.post(
        "/api/v1/conversation/sessions/start",
        params={"user_id": 9999}
    )
    assert response.status_code == 404


def test_next_question_invalid_session(client):
    response = client.post("/api/v1/conversation/sessions/9999/question")
    assert response.status_code == 404


def test_submit_answer_invalid_session(client):
    response = client.post(
        "/api/v1/conversation/sessions/9999/answer",
        params={"user_answer": "test"}
    )
    assert response.status_code in [404, 500]


def test_end_session_invalid(client):
    response = client.post("/api/v1/conversation/sessions/9999/end")
    assert response.status_code in [404, 500]
