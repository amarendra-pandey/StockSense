from fastapi.testclient import TestClient

from app.config import Settings, settings
from app.main import app


def test_health_endpoint_returns_status_and_method():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "method": "GET",
        "status_code": 200,
    }


def test_app_uses_configured_settings():
    assert app.title == settings.app_name
    assert app.debug == settings.debug
    assert app.state.environment == settings.environment


def test_database_url_can_be_configured_from_environment(monkeypatch):
    database_url = "postgresql+psycopg://user:password@db.example.com:5432/stocksense"
    monkeypatch.setenv("DATABASE_URL", database_url)

    configured_settings = Settings(_env_file=None)

    assert configured_settings.database_url == database_url
