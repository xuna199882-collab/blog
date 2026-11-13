import pytest


# ---------- 辅助函数 ----------

def create_tag(client, headers, name="python"):
    res = client.post("/tags", json={"name": name}, headers=headers)
    return res


def create_post(client, headers, title="Test Post"):
    res = client.post("/posts", json={
        "title": title, "content": "content",
    }, headers=headers)
    return res.json()


# ---------- 创建标签 ----------

def test_create_tag_admin_success(client, admin_headers):
    res = create_tag(client, admin_headers, "python")
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "python"
    assert data["post_count"] == 0


def test_create_tag_non_admin_forbidden(client, auth_headers):
    res = create_tag(client, auth_headers, "python")
    assert res.status_code == 403


def test_create_tag_duplicate(client, admin_headers):
    create_tag(client, admin_headers, "python")
    res = create_tag(client, admin_headers, "python")
    assert res.status_code == 409


def test_create_tag_empty_name(client, admin_headers):
    res = create_tag(client, admin_headers, "")
    assert res.status_code == 422


# ---------- 删除标签 ----------

def test_delete_tag_admin_success(client, admin_headers):
    tag = create_tag(client, admin_headers, "python").json()
    res = client.delete(f"/tags/{tag['id']}", headers=admin_headers)
    assert res.status_code == 204


def test_delete_tag_non_admin_forbidden(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    res = client.delete(f"/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 403


def test_delete_tag_not_found(client, admin_headers):
    res = client.delete("/tags/999", headers=admin_headers)
    assert res.status_code == 404


# ---------- 标签列表 ----------

def test_list_tags_empty(client):
    res = client.get("/tags")
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_list_tags_with_count(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)

    # 打标签
    client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)

    res = client.get("/tags")
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["post_count"] == 1


def test_list_tags_empty_tag_count_zero(client, admin_headers):
    create_tag(client, admin_headers, "python")
    res = client.get("/tags")
    assert res.json()["items"][0]["post_count"] == 0


# ---------- 打标签 ----------

def test_add_tag_to_post_success(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)

    res = client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_add_tag_to_post_non_author_forbidden(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)

    # 用 admin 的 token 给 auth_headers 用户的文章打标签
    res = client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=admin_headers)
    assert res.status_code == 403


def test_add_tag_to_post_duplicate(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)

    client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)
    res = client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 409


def test_add_tag_not_found(client, auth_headers):
    post = create_post(client, auth_headers)
    res = client.post(f"/posts/{post['id']}/tags/999", headers=auth_headers)
    assert res.status_code == 404


def test_add_tag_post_not_found(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    res = client.post(f"/posts/999/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 404


# ---------- 移除标签 ----------

def test_remove_tag_from_post_success(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)
    client.post(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)

    res = client.delete(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 204


def test_remove_tag_not_associated(client, admin_headers, auth_headers):
    tag = create_tag(client, admin_headers, "python").json()
    post = create_post(client, auth_headers)

    res = client.delete(f"/posts/{post['id']}/tags/{tag['id']}", headers=auth_headers)
    assert res.status_code == 404


# ---------- 按标签筛选 ----------

def test_filter_posts_by_tag(client, admin_headers, auth_headers):
    tag_py = create_tag(client, admin_headers, "python").json()
    tag_fa = create_tag(client, admin_headers, "fastapi").json()

    post_a = create_post(client, auth_headers, "A")
    post_b = create_post(client, auth_headers, "B")
    create_post(client, auth_headers, "C")   # C 不打标签

    client.post(f"/posts/{post_a['id']}/tags/{tag_py['id']}", headers=auth_headers)
    client.post(f"/posts/{post_b['id']}/tags/{tag_py['id']}", headers=auth_headers)
    client.post(f"/posts/{post_b['id']}/tags/{tag_fa['id']}", headers=auth_headers)

    # 不带 tag，3 篇
    assert client.get("/posts").json()["total"] == 3

    # tag=python，2 篇
    res = client.get("/posts?tag=python")
    assert res.json()["total"] == 2

    # tag=fastapi，1 篇
    res = client.get("/posts?tag=fastapi")
    assert res.json()["total"] == 1

    # 不存在的标签，0 篇
    res = client.get("/posts?tag=nonexistent")
    assert res.json()["total"] == 0