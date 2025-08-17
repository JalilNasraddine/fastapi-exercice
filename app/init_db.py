import os, csv
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from . import models

def parse_bool(v: str) -> bool:
    return str(v).strip().lower() in {"1", "true", "t", "yes", "y"}

def parse_dt(v: Optional[str]) -> Optional[datetime]:
    if not v or str(v).strip() == "":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(v, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None

def seed_from_csv(db: Session, data_dir: str) -> None:
    user_count = db.query(models.User).count()
    post_count = db.query(models.Post).count()
    if user_count > 0 or post_count > 0:
        return  # already seeded

    # Users
    users_csv = os.path.join(data_dir, "users.csv")
    if os.path.exists(users_csv):
        with open(users_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                user = models.User(
                    id=int(row.get("id")) if row.get("id") else None,
                    email=row.get("email"),
                    username=row.get("username") or row.get("name") or row.get("full_name"),
                    first_name=row.get("first_name"),
                    last_name=row.get("last_name"),
                    is_active=parse_bool(row.get("is_active", "true")),
                    created_at=parse_dt(row.get("created_at")) or datetime.utcnow(),
                )
                db.add(user)
        db.commit()

    # Posts
    posts_csv = os.path.join(data_dir, "posts.csv")
    if os.path.exists(posts_csv):
        with open(posts_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                author_id = row.get("author_id") or row.get("user_id") or row.get("userId")
                if not author_id:
                    continue
                post = models.Post(
                    id=int(row.get("id")) if row.get("id") else None,
                    title=row.get("title") or "Untitled",
                    content=row.get("content") or row.get("body") or "",
                    author_id=int(author_id),
                    is_published=parse_bool(row.get("is_published", "true")),
                    created_at=parse_dt(row.get("created_at")) or datetime.utcnow(),
                )
                if db.get(models.User, post.author_id):
                    db.add(post)
        db.commit()
