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


def test_set_ai_provider_valid(client):
    """Test setting valid AI provider."""
    # Test openrouter
    response = client.post(
        "/api/v1/ai-config/provider",
        json={"provider": "openrouter"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "openrouter"

    # Test gemini
    response = client.post(
        "/api/v1/ai-config/provider",
        json={"provider": "gemini"}
    )
    assert response.status_code == 200
    assert response.json()["provider"] == "gemini"


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
