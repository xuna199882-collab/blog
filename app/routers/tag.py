from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse, TagListResponse
from app.services import tag_service

router = APIRouter(tags=["tags"])
@router.post("/tags", response_model=TagResponse, status_code=201)
def create_tag(
    data: TagCreate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    tag = tag_service.create(db, data)
    return TagResponse(id=tag.id, name=tag.name, post_count=0)

@router.get("/tags", response_model=TagListResponse)
def list_tags(db: Session = Depends(get_db)):
    items = tag_service.list_with_count(db)
    return TagListResponse(total=len(items), items=items)

@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    tag_service.delete(db, tag_id)


@router.post("/posts/{post_id}/tags/{tag_id}", status_code=204)
def add_tag_to_post(
    post_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag_service.add_to_post(db, post_id, tag_id, current_user.id)

@router.delete("/posts/{post_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_post(
    post_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tag_service.remove_from_post(db, post_id, tag_id, current_user.id)