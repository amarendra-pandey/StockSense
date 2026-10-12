from fastapi.testclient import TestClient

from app.config import settings
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
