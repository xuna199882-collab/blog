# tests/test_user_service.py
import pytest

from app.services import user_service
from app.schemas.user import UserRegister
from app.core.exceptions import ConflictError
from app.core.security import verify_password


def test_register_success(db_session):
    data = UserRegister(name="Alice", email="alice@example.com", password="12345678")
    user = user_service.register(db_session, data)

    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.password_hash != "12345678"          # 存的不是明文
    assert verify_password("12345678", user.password_hash)   # 哈希能验证


def test_register_duplicate_email(db_session):
    data = UserRegister(name="Alice", email="alice@example.com", password="12345678")
    user_service.register(db_session, data)

    with pytest.raises(ConflictError):
        user_service.register(db_session, data)      # 同一邮箱再注册，抛冲突


def test_authenticate_success(db_session):
    data = UserRegister(name="Alice", email="alice@example.com", password="12345678")
    user_service.register(db_session, data)

    user = user_service.authenticate(db_session, "alice@example.com", "12345678")
    assert user is not None
    assert user.email == "alice@example.com"


def test_authenticate_wrong_password(db_session):
    data = UserRegister(name="Alice", email="alice@example.com", password="12345678")
    user_service.register(db_session, data)

    user = user_service.authenticate(db_session, "alice@example.com", "wrong")
    assert user is None


def test_authenticate_nonexistent_user(db_session):
    user = user_service.authenticate(db_session, "nobody@example.com", "12345678")
    assert user is None