import pytest
from fastapi.testclient import TestClient
from demo.db import init_db
from demo.app import app, format_error_response


@pytest.fixture(autouse=True)
def setup_db(monkeypatch, tmp_path):
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr("demo.db.DB_PATH", db_file)
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_signup(client):
    resp = client.post("/users", json={
        "name": "alice",
        "email": "alice@test.com",
        "password": "pass123",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_fetch_user(client):
    client.post("/users", json={
        "name": "bob",
        "email": "bob@test.com",
        "password": "secret",
    })
    resp = client.get("/users/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "bob"


def test_fetch_user_not_found(client):
    resp = client.get("/users/999")
    assert resp.status_code == 404


def test_format_error_response():
    result = format_error_response(400, "bad request")
    assert result["error"] is True
    assert result["status"] == 400
    assert result["detail"] == "bad request"


def test_do_hash(client):
    resp = client.get("/hash?data=hello")
    assert resp.status_code == 200
    data = resp.json()
    assert "md5" in data
    assert "sha1" in data
