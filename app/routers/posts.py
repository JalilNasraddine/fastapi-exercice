from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=List[schemas.PostOut])
def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    author_id: Optional[int] = Query(None, description="Filter by author (user) id"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    is_published: Optional[bool] = Query(None, description="Filter by publication status"),
    order_by: str = Query("created_at", pattern="^(created_at|title|id)$"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    posts, _ = crud.list_posts(
        db,
        skip=skip,
        limit=limit,
        author_id=author_id,
        search=search,
        is_published=is_published,
        order_by=order_by,
        order_dir=order_dir,
    )
    return posts

@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post

@router.put("/{post_id}", response_model=schemas.PostOut)
def update_post(post_id: int, payload: schemas.PostUpdate, db: Session = Depends(get_db)):
    return crud.update_post(db, post_id, payload)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    crud.delete_post(db, post_id)
    return None
