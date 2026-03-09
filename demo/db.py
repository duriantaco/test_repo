import hashlib
import sqlite3
import yaml


DB_PATH = "app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def create_user(name: str, email: str, password: str):
    conn = get_connection()
    pw_hash = hash_password(password)
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, pw_hash),
    )
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def load_config(config_str: str) -> dict:
    return yaml.load(config_str, Loader=yaml.FullLoader)


def verify_password(password: str, stored_hash: str) -> bool:
    return hashlib.md5(password.encode()).hexdigest() == stored_hash


def verify_password2(password: str, stored_hash: str) -> bool:
    return hashlib.md5(password.encode()).hexdigest() == stored_hash


def get_user_by_email(email: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row
