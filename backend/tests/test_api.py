"""Tests for the public Milestone 1 routes."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.headers["X-Request-ID"]


def test_version():
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["data"] == {"version": "0.1.0"}


def test_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
