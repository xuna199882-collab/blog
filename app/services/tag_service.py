# app/services/post_service.py
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.models.post import Post, post_tags
from app.schemas.tag import TagCreate,TagResponse,TagListResponse
from app.core.exceptions import NotFoundError, PermissionDeniedError,ConflictError
# app/services/post_service.py 补充
from app.core.cache import get_json, set_json, delete
import logging

logger = logging.getLogger(__name__)



def get(db: Session, tag_id: int) -> Tag:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise NotFoundError("标签不存在")
    return tag

def create(db: Session, data: TagCreate, author_id: int) -> Tag:
    
    if db.scalars(select(Tag).where(Tag.name == data.name)).first():
         raise ConflictError(f"标签 '{data.name}' 已存在")
    tag = Tag(name=data.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def list_with_count(db: Session) -> list[dict]:
    """返回标签列表，每个标签带文章数"""
    stmt = (
        select(Tag.id, Tag.name, func.count(post_tags.c.post_id).label("post_count"))
        .outerjoin(post_tags, Tag.id == post_tags.c.tag_id)
        .group_by(Tag.id, Tag.name)
        .order_by(Tag.name)
    )
    rows = db.execute(stmt).all()
    return [
        {"id": row.id, "name": row.name, "post_count": row.post_count}
        for row in rows
    ]

def add_to_post(db: Session, post_id: int, tag_id: int, user_id: int) -> None:
    post = db.get(Post, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    if post.author_id != user_id:
        raise PermissionDeniedError("只能给自己的文章打标签")
    
    tag = db.get(Tag, tag_id)
    if not tag:
        raise NotFoundError("标签不存在")

    exists = db.execute(
        select(post_tags).where(
            post_tags.c.post_id == post_id,
            post_tags.c.tag_id == tag_id,
        )
    ).first()
    if exists:
        raise ConflictError("该文章已有此标签")
    db.execute(post_tags.insert().values(post_id=post_id, tag_id=tag_id))
    db.commit()

def remove_from_post(db: Session, post_id: int, tag_id: int, user_id: int) -> None:
    post = db.get(Post, post_id)
    if not post:
        raise NotFoundError("文章不存在")
    if post.author_id != user_id:
        raise PermissionDeniedError("只能操作自己的文章")

    result = db.execute(
        post_tags.delete().where(
            post_tags.c.post_id == post_id,
            post_tags.c.tag_id == tag_id,
        )
    )
    if result.rowcount == 0:
        raise NotFoundError("该文章没有此标签")
    db.commit()