# tests/test_posts.py
import pytest


@pytest.fixture
def other_user_headers(client):
    """第二个用户，用于测试权限"""
    client.post("/auth/register", json={
        "name": "Bob", "email": "bob@example.com", "password": "12345678",
    })
    res = client.post("/auth/login", json={
        "email": "bob@example.com", "password": "12345678",
    })
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def create_post(client, headers, title="Test Post"):
    res = client.post("/posts", json={
        "title": title, "content": "content",
    }, headers=headers)
    return res.json()


def test_create_post_requires_auth(client):
    res = client.post("/posts", json={"title": "t", "content": "c"})
    assert res.status_code == 401                  # 没 token


def test_create_post_success(client, auth_headers):
    res = client.post("/posts", json={
        "title": "Hello", "content": "World",
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Hello"
    assert data["author_id"] is not None


def test_get_post_not_found(client):
    res = client.get("/posts/999")
    assert res.status_code == 404


def test_list_posts_pagination(client, auth_headers):
    for i in range(15):
        create_post(client, auth_headers, title=f"Post {i}")

    res = client.get("/posts?page=1&size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 15
    assert len(data["items"]) == 10


def test_update_post_by_non_author(client, auth_headers, other_user_headers):
    post = create_post(client, auth_headers)

    res = client.patch(f"/posts/{post['id']}", json={
        "title": "Hacked",
    }, headers=other_user_headers)
    assert res.status_code == 403                  # 非作者，禁止


def test_delete_post_by_non_author(client, auth_headers, other_user_headers):
    post = create_post(client, auth_headers)

    res = client.delete(f"/posts/{post['id']}", headers=other_user_headers)
    assert res.status_code == 403


def test_delete_post_by_author(client, auth_headers):
    post = create_post(client, auth_headers)

    res = client.delete(f"/posts/{post['id']}", headers=auth_headers)
    assert res.status_code == 204
    assert client.get(f"/posts/{post['id']}").status_code == 404