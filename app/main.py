import os
from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import schemas
from .routers import users as users_router
from .routers import posts as posts_router
from .init_db import seed_from_csv

DESCRIPTION = '''
A simple blog API built with FastAPI + SQLAlchemy + SQLite.
- Users & Posts with 1-to-many
- Pagination & filtering on posts
- Validation via Pydantic
- Auto-seeding from CSV on startup
'''

app = FastAPI(
    title="FastAPI Blog API",
    version="0.1.0",
    description=DESCRIPTION,
)

app.include_router(users_router.router)
app.include_router(posts_router.router)

# Nested route: create a post for a given user
@app.post("/users/{user_id}/posts", response_model=schemas.PostOut, tags=["Posts"], status_code=status.HTTP_201_CREATED)
def create_post_for_user(user_id: int, payload: schemas.PostCreate, db: Session = Depends(get_db)):
    from . import crud
    return crud.create_post_for_user(db, author_id=user_id, payload=payload)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    data_dir = os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))
    # get_db() is a generator; use next() to grab a session for seeding
    seed_from_csv(next(get_db()), data_dir=os.path.abspath(data_dir))

@app.get("/", tags=["Health"])
def health():
    return {"status": "ok"}
