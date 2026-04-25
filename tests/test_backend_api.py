from fastapi.testclient import TestClient

from src.backend.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert "loaded_restaurants" in body


def test_recommend_validation_error() -> None:
    response = client.post("/recommend", json={"locality": "", "min_rating": 3.0})
    assert response.status_code == 400


def test_localities_endpoint() -> None:
    response = client.get("/localities")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    assert isinstance(body["localities"], list)
