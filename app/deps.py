# app/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="无效或过期的 token")
    user = user_service.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user

def require_admin(
   current_user: User = Depends(get_current_user)
) -> User:
   if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
   return current_user
