from app import create_app
from app.routes import auth


def test_auth_protects_analysis_and_allows_valid_session(monkeypatch):
    monkeypatch.setattr(auth, "AUTH_ENABLED", True)
    monkeypatch.setattr(auth, "AUTH_USERNAME", "demo")
    monkeypatch.setattr(auth, "AUTH_PASSWORD", "secret")
    monkeypatch.setattr(auth, "SECRET_KEY", "test-secret")
    client = create_app().test_client()

    assert client.post("/api/market/classify", json={}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "demo", "password": "secret"}).status_code == 200
    assert client.post("/api/market/classify", json={"source": "local"}).status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.post("/api/market/classify", json={}).status_code == 401


def test_auth_rejects_default_configuration(monkeypatch):
    monkeypatch.setattr(auth, "AUTH_ENABLED", True)
    monkeypatch.setattr(auth, "AUTH_PASSWORD", "")
    monkeypatch.setattr(auth, "SECRET_KEY", "change-me-in-production")
    response = create_app().test_client().post("/api/auth/login", json={})
    assert response.status_code == 503