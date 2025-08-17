from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[schemas.UserOut])
def list_users(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    return crud.list_users(db, skip=skip, limit=limit)

@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, payload)

@router.get("/{user_id}", response_model=schemas.UserWithPosts)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, payload)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id)
    return None
