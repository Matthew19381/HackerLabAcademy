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
