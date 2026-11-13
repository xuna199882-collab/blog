import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app
from app import models   # noqa: F401 触发所有模型注册

@pytest.fixture
def db_session():
    """每个测试用独立的内存 SQLite，测完销毁"""
    engine = create_engine(
        "sqlite:///:memory:",
         poolclass=StaticPool,
        connect_args={"check_same_thread": False},   # TestClient 用线程池，需要关掉这个检查
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def client(db_session):
    """覆盖 get_db 依赖，让接口用测试数据库"""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    
@pytest.fixture
def auth_headers(client):
    """注册并登录一个测试用户，返回带 token 的请求头"""
    client.post("/auth/register", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "12345678",
    })
    res = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "12345678",
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}