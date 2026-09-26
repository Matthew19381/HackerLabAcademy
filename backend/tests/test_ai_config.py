def test_get_ai_provider(client):
    """Test getting current AI provider config."""
    response = client.get("/api/v1/ai-config/provider")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "available_providers" in data
    assert "models" in data
    assert data["provider"] in data["available_providers"]


def test_set_ai_provider_invalid(client):
    """Test setting invalid AI provider."""
    response = client.post(
        "/api/v1/ai-config/provider",
        json={"provider": "invalid_provider"}
    )
    assert response.status_code == 400


def test_set_ai_provider_valid(client, monkeypatch):
    """Test setting valid AI provider (keys faked: result must not depend on local .env)."""
    from backend.config import settings

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "AI_PROVIDER", settings.AI_PROVIDER)  # restored after test

    response = client.post("/api/v1/ai-config/provider", json={"provider": "openrouter"})
    assert response.status_code == 200
    assert response.json()["provider"] == "openrouter"

    response = client.post("/api/v1/ai-config/provider", json={"provider": "gemini"})
    assert response.status_code == 200
    assert response.json()["provider"] == "gemini"


def test_set_ai_provider_without_key_is_rejected(client, monkeypatch):
    from backend.config import settings

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", None)
    response = client.post("/api/v1/ai-config/provider", json={"provider": "openrouter"})
    assert response.status_code == 400


def test_test_ai_connection(client):
    """Test AI connection endpoint."""
    response = client.get("/api/v1/ai-config/test")
    # May return 200 with success or 500 if API key missing
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "success" in data
        assert "provider" in data


def test_test_specific_provider(client):
    """Test AI connection with specific provider."""
    response = client.get("/api/v1/ai-config/test?provider=gemini")
    assert response.status_code in [200, 500]
