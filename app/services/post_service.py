# app/services/post_service.py
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.core.exceptions import NotFoundError, PermissionDeniedError
# app/services/post_service.py 补充
from app.core.cache import get_json, set_json, delete
import logging

logger = logging.getLogger(__name__)

CACHE_KEY_HOT = "posts:hot:{page}:{size}"

def get(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    return post


def list_posts(db: Session, page: int, size: int,tag: str | None = None,) -> tuple[list[Post], int]:
    total = db.scalar(select(func.count()).select_from(Post))
    items = db.scalars(
        select(Post).order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    return list(items), total


def list_by_author(db: Session, author_id: int, page: int, size: int) -> tuple[list[Post], int]:
    base = select(Post).where(Post.author_id == author_id)
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    items = db.scalars(
        base.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size)
    ).all()
    return list(items), total


def create(db: Session, data: PostCreate, author_id: int) -> Post:
    post = Post(title=data.title, content=data.content, author_id=author_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update(db: Session, post_id: int, data: PostUpdate, user_id: int) -> Post:
    post = get(db, post_id)
    if post.author_id != user_id:
        raise PermissionDeniedError("只能修改自己的文章")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


def delete(db: Session, post_id: int, user_id: int) -> None:
    post = get(db, post_id)
    if post.author_id != user_id:
        raise PermissionDeniedError("只能删除自己的文章")
    db.delete(post)
    db.commit()

def list_hot_posts(db: Session, page: int, size: int) -> tuple[list[dict], int]:
    key = CACHE_KEY_HOT.format(page=page, size=size)
    cached = get_json(key)
    if cached:
        logger.info("缓存命中: %s", key)
        return cached["items"], cached["total"]

    items, total = list_posts(db, page, size)
    data = {
        "items": [PostResponse.model_validate(p).model_dump(mode="json") for p in items],
        "total": total,
    }
    set_json(key, data, expire=60)
    return data["items"], total