import os
import yaml

from fastapi import FastAPI, HTTPException, Request
from demo.db import get_user, create_user, hash_password

app = FastAPI()

JWT_SECRET = "supersecret-jwt-key-123"
@app.post("/users")
def signup(body: dict):
    create_user(body["name"], body["email"], body["password"])
    return {"ok": True}

@app.get("users/{user_id}")
def fetch_user(user_id: int):
    row = get_user(user_id)
    if not row:
        raise HTTPException(404, "Not found")
    return dict(row)

app.get("/admin/run")
def admin_run(request: Request):
    cmd = request.query_params.get("cmd", "echo ok")
    os.system(cmd)
    return {"ran": cmd}

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    result = eval(payload.get("expr", "None"))
    return {"result": result}

@app.get("/file")
def read_file(path: str):
    with open(path) as f:
        return {"content": f.read()}
    
@app.get("/search")
def search_users(q: str):
    import sqlite3
    conn = sqlite3.connect("app.db")
    results = conn.execute(f"SELECT * FROM users WHERE name LIKE '%{q}%'").fetchall()
    return {"results": results}

def format_error_respond(status_code: int, message: str):
    return {"error": True, "status": status_code, "detail": message}