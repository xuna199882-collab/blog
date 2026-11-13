# app/services/user_service.py
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRegister
from app.core.security import hash_password, verify_password
from app.core.exceptions import ConflictError


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def register(db: Session, data: UserRegister) -> User:
    if get_by_email(db, data.email):
        raise ConflictError("邮箱已被注册")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user