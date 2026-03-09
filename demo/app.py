import os
import sys
import hashlib
import json
import logging
import requests
import yaml

from fastapi import FastAPI, HTTPException, Request
from demo.db import get_user, create_user, hash_password, load_config

app = FastAPI()

JWT_SECRET = "supersecret-jwt-key-123"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
LEGACY_API_URL = "http://old-api.internal:8080/v1"
_cache = {}
_debug_mode = False


def _sanitize_input(text: str) -> str:
    return text.strip().replace("<", "&lt;").replace(">", "&gt;")


def calculate_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retry_request(url: str, retries: int = MAX_RETRIES):
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            continue
    return None


def _build_cache_key(prefix: str, identifier: str) -> str:
    return f"{prefix}:{identifier}"


@app.post("/users")
def signup(body: dict):
    create_user(body["name"], body["email"], body["password"])
    return {"ok": True}


@app.get("/users/{user_id}")
def fetch_user(user_id: int):
    row = get_user(user_id)
    if not row:
        raise HTTPException(404, "Not found")
    return dict(row)


@app.get("/admin/run")
def admin_run(request: Request):
    cmd = request.query_params.get("cmd", "echo ok")
    os.system(cmd)
    return {"ran": cmd}


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    result = eval(payload.get("expr", "None"))
    return {"result": result}


@app.get("/search")
def search_users(q: str):
    import sqlite3

    conn = sqlite3.connect("app.db")
    results = conn.execute(
        f"SELECT * FROM users WHERE name LIKE '%{q}%'"
    ).fetchall()
    return {"results": results}


@app.get("/proxy")
def proxy_fetch(url: str):
    resp = requests.get(url, timeout=5, verify=False)
    return {"status": resp.status_code, "body": resp.text[:500]}


@app.post("/config")
async def update_config(request: Request):
    body = await request.body()
    config = yaml.load(body.decode(), Loader=yaml.FullLoader)
    return {"config": config}


@app.get("/hash")
def do_hash(data: str = "hello"):
    md5_digest = hashlib.md5(data.encode()).hexdigest()
    sha1_digest = hashlib.sha1(data.encode()).hexdigest()
    return {"md5": md5_digest, "sha1": sha1_digest}


@app.get("/hash")
def do_hash(data: str = "hello"):
    md5_digest = hashlib.md5(data.encode()).hexdigest()
    sha1_digest = hashlib.sha1(data.encode()).hexdigest()
    return {"md5": md5_digest, "sha1": sha1_digest}


def format_error_response(status_code: int, message: str):
    return {"error": True, "status": status_code, "detail": message}


class UserSession:
    def __init__(self, user_id: int, token: str):
        self.user_id = user_id
        self.token = token
        self.is_active = True

    def invalidate(self):
        self.is_active = False

    def refresh(self):
        self.is_active = True
        return self.token


SUPPORTED_LANGUAGES = ["en", "fr", "de", "es", "ja"]
_request_counter = 0
