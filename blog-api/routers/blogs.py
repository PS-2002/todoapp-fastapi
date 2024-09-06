from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Post
from database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix='/blogs',
    tags=['blogs']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



class BlogRequest(BaseModel):
    title: str = Field(min_length=3)
    content: str = Field(min_length=3)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Post).filter(Post.owner_id == user.get('id')).all()


@router.get("/blog/{blog_id}", status_code=status.HTTP_200_OK)
async def read_blog(user:user_dependency, db: db_dependency, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    blog_model = db.query(Post).filter(Post.id == blog_id).first()
    if blog_model is not None:
        return blog_model
    raise HTTPException(status_code=404, detail='Blog not found.')


@router.post("/blog", status_code=status.HTTP_201_CREATED)
async def create_blog(user:user_dependency, db: db_dependency, blog_request: BlogRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    blog_model = Post(**blog_request.model_dump(), owner_id=user.get('id'))

    db.add(blog_model)
    db.commit()


@router.put("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog(user: user_dependency, db:db_dependency, blog_request: BlogRequest, blog_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed.")
    
    blog_model = db.query(Post).filter(Post.id == blog_id).filter(Post.owner_id == user.get('id')).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail="Blog not found.")
    blog_model.title = blog_request.title
    blog_model.content = blog_model.content

    db.add(blog_model)
    db.commit()



@router.delete("/blog/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(user: user_dependency, db: db_dependency, blog_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    blog_model = db.query(Post).filter(Post.id == blog_id).filter(Post.owner_id == user.get('id')).first()
    if blog_model is None:
        raise HTTPException(status_code=404, detail="Blog not found.")
    db.query(Post).filter(Post.id == blog_id).filter(Post.owner_id == user.get('id')).delete()

    db.commit()
    