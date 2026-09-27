def test_list_articles(client):
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data


def test_get_nonexistent_article(client):
    response = client.get("/api/v1/articles/nonexistent-article")
    assert response.status_code == 404


def test_list_articles_with_category(client):
    response = client.get("/api/v1/articles/?category=Security")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data


def test_read_and_quiz_endpoints_exist_and_grade(client, db_session):
    """Both were called by Articles.jsx but missing (404) until 2026-09-27."""
    import json as _json

    from backend.models.article import Article, ArticleQuiz
    from backend.models.user import User

    user = User(name="reader", total_xp=0)
    art = Article(slug="t-art", title="T", content_md="# T")
    db_session.add_all([user, art])
    db_session.commit()
    q1 = ArticleQuiz(article_id=art.id, question="a?", options=_json.dumps(["x", "y"]), correct_index=1)
    q2 = ArticleQuiz(article_id=art.id, question="b?", options=_json.dumps(["x", "y"]), correct_index=0)
    db_session.add_all([q1, q2])
    db_session.commit()

    detail = client.get("/api/v1/articles/t-art").json()
    assert [q["question"] for q in detail["quiz_questions"]] == ["a?", "b?"]
    assert "correct_index" not in detail["quiz_questions"][0]

    r = client.post("/api/v1/articles/t-art/read", json={"user_id": user.id, "read_time_seconds": 120})
    assert r.status_code == 200 and r.json()["read_time_seconds"] == 120

    body = {"user_id": user.id, "answers": {str(q1.id): 1, str(q2.id): 1}}
    res = client.post("/api/v1/articles/t-art/quiz/submit", json=body).json()
    assert (res["correct"], res["total"], res["score_percent"], res["xp_awarded"]) == (1, 2, 50, 5)
    again = client.post("/api/v1/articles/t-art/quiz/submit", json=body).json()
    assert again["xp_awarded"] == 0  # XP only once
