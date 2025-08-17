from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# -------- Posts --------
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    is_published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    is_published: Optional[bool] = None

class PostOut(PostBase):
    id: int
    author_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# -------- Users --------
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UserWithPosts(UserOut):
    posts: List[PostOut] = Field(default_factory=list)
