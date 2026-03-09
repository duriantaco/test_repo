import os
import pytest
from demo.db import (
    get_connection,
    init_db,
    hash_password,
    create_user,
    get_user,
    get_user_by_email,
    verify_password,
    load_config,
)

DB_PATH = "test_app.db"


@pytest.fixture(autouse=True)
def setup_db(monkeypatch, tmp_path):
    db_file = str(tmp_path / "test.db")
    monkeypatch.setattr("demo.db.DB_PATH", db_file)
    init_db()
    yield
    if os.path.exists(db_file):
        os.unlink(db_file)


def test_hash_password_returns_string():
    result = hash_password("mypassword")
    assert isinstance(result, str)
    assert len(result) > 0


def test_hash_password_deterministic():
    assert hash_password("abc") == hash_password("abc")


def test_hash_password_different_inputs():
    assert hash_password("abc") != hash_password("xyz")


def test_create_and_get_user():
    create_user("alice", "alice@example.com", "password123")
    user = get_user(1)
    assert user is not None
    assert user["name"] == "alice"
    assert user["email"] == "alice@example.com"


def test_get_user_not_found():
    user = get_user(999)
    assert user is None


def test_get_user_by_email():
    create_user("bob", "bob@example.com", "secret")
    user = get_user_by_email("bob@example.com")
    assert user is not None
    assert user["name"] == "bob"


def test_get_user_by_email_not_found():
    user = get_user_by_email("nobody@example.com")
    assert user is None


def test_verify_password():
    pw = "testpass"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_load_config():
    config = load_config("name: test\nport: 8080")
    assert config["name"] == "test"
    assert config["port"] == 8080
