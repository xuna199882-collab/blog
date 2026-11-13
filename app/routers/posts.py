# app/routers/posts.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    tag: str | None = Query(None, max_length=50),
):
    items, total = post_service.list_posts(db, page, size,tag)
    return PostListResponse(total=total, page=page, size=size, items=items)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    return post_service.get(db, post_id)


@router.post("", response_model=PostResponse, status_code=201)
def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return post_service.create(db, data, current_user.id)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return post_service.update(db, post_id, data, current_user.id)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post_service.delete(db, post_id, current_user.id)