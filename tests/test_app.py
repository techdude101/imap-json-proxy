from fastapi.testclient import TestClient

from src.flaskapp.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}