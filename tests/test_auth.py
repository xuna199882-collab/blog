# tests/test_auth.py
def test_register_success(client):
    res = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "12345678",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alice"
    assert "password" not in data                  # 响应不含密码
    assert "password_hash" not in data


def test_register_invalid_email(client):
    res = client.post("/auth/register", json={
        "name": "Alice",
        "email": "not-an-email",
        "password": "12345678",
    })
    assert res.status_code == 422                  # Pydantic 校验失败


def test_register_short_password(client):
    res = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "123",                         # 少于 8 位
    })
    assert res.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "12345678",
    })
    res = client.post("/auth/login", json={
        "email": "alice@example.com", "password": "12345678",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "name": "Alice", "email": "alice@example.com", "password": "12345678",
    })
    res = client.post("/auth/login", json={
        "email": "alice@example.com", "password": "wrong",
    })
    assert res.status_code == 401