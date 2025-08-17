from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func
from fastapi import HTTPException, status
from . import models, schemas

# ----- Users -----
def get_user(db: Session, user_id: int):
    return db.get(models.User, user_id)

def get_user_by_email(db: Session, email: str):
    return db.execute(select(models.User).where(models.User.email == email)).scalar_one_or_none()

def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.execute(select(models.User).offset(skip).limit(limit)).scalars().all()

def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, payload: schemas.UserUpdate) -> models.User:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != user.email:
        if get_user_by_email(db, data["email"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    db.delete(user)
    db.commit()

# ----- Posts -----
def get_post(db: Session, post_id: int):
    return db.get(models.Post, post_id)

def list_posts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    author_id: Optional[int] = None,
    search: Optional[str] = None,
    is_published: Optional[bool] = None,
    order_by: str = "created_at",
    order_dir: str = "desc",
) -> Tuple[List[models.Post], int]:
    q = select(models.Post)
    count_q = select(func.count(models.Post.id))
    filters = []
    if author_id is not None:
        filters.append(models.Post.author_id == author_id)
    if search:
        like = f"%{search}%"
        filters.append(or_(models.Post.title.ilike(like), models.Post.content.ilike(like)))
    if is_published is not None:
        filters.append(models.Post.is_published == is_published)
    if filters:
        q = q.where(*filters)
        count_q = count_q.where(*filters)

    order_col = getattr(models.Post, order_by, models.Post.created_at)
    q = q.order_by(order_col.asc() if order_dir.lower() == "asc" else order_col.desc())

    total = db.execute(count_q).scalar_one()
    items = db.execute(q.offset(skip).limit(min(limit, 100))).scalars().all()
    return items, total

def create_post_for_user(db: Session, author_id: int, payload: schemas.PostCreate) -> models.Post:
    user = db.get(models.User, author_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    post = models.Post(author_id=author_id, **payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def update_post(db: Session, post_id: int, payload: schemas.PostUpdate) -> models.Post:
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(post, k, v)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post_id: int) -> None:
    post = get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    db.delete(post)
    db.commit()
