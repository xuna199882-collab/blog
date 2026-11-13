# app/services/comment_service.py
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate
from app.core.exceptions import NotFoundError, PermissionDeniedError


def create(db: Session, post_id: int, data: CommentCreate, author_id: int) -> Comment:
    if not db.get(Post, post_id):
        raise NotFoundError("文章不存在")
    comment = Comment(content=data.content, post_id=post_id, author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_by_post(db: Session, post_id: int) -> list[Comment]:
    return list(db.scalars(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
    ).all())


def delete(db: Session, comment_id: int, user_id: int) -> None:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise NotFoundError("评论不存在")
    post = db.get(Post, comment.post_id)
    if comment.author_id != user_id and post.author_id != user_id:
        raise PermissionDeniedError("无权删除该评论")
    db.delete(comment)
    db.commit()