import os
from fastapi.testclient import TestClient

# Use an in-memory SQLite DB (single-connection pool handled in app.database)
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DATA_DIR"] = os.path.abspath("data")  # optional: seeding not required for tests

from app.database import Base, engine
from app.main import app  # import after env vars

# Ensure tables exist for the test DB
Base.metadata.create_all(bind=engine)

def test_health():
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

def test_user_flow():
    with TestClient(app) as client:
        # create user
        payload = {
            "email": "new.user@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "is_active": True
        }
        r = client.post("/users", json=payload)
        assert r.status_code == 201, r.text
        user = r.json()
        user_id = user["id"]

        # create a post for that user
        r = client.post(f"/users/{user_id}/posts", json={"title": "Hello", "content": "World", "is_published": True})
        assert r.status_code == 201
        post = r.json()

        # list posts with filter
        r = client.get("/posts", params={"author_id": user_id, "search": "Hell"})
        assert r.status_code == 200
        assert any(p["id"] == post["id"] for p in r.json())

        # update post
        r = client.put(f"/posts/{post['id']}", json={"title": "Hello 2"})
        assert r.status_code == 200
        assert r.json()["title"] == "Hello 2"

        # delete post then user
        assert client.delete(f"/posts/{post['id']}").status_code == 204
        assert client.delete(f"/users/{user_id}").status_code == 204