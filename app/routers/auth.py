# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.user import UserRegister, UserResponse, TokenResponse
from app.core.security import create_access_token
from app.services import user_service
from app.schemas.user import UserLogin
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return user_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return TokenResponse(access_token=create_access_token(user.id))

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
def login_for_swagger(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # form.username 就是邮箱
    user = user_service.authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return TokenResponse(access_token=create_access_token(user.id))