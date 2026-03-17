from uuid import uuid4


async def test_auth_cookie_login_success(client):
    email = f"john-{uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "secret123"}

    register_resp = await client.post("/auth/register", json=payload)
    assert register_resp.status_code == 201
    register_data = register_resp.json()
    assert register_data["email"] == email
    assert "id" in register_data

    resp = await client.post(
        "/auth/cookie/login",
        data={"username": email, "password": "secret123"},
    )
    assert resp.status_code in (200, 204)
    assert "set-cookie" in resp.headers


async def test_auth_cookie_login_wrong_password(client):
    email = f"jane-{uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "pw123456"}

    register_resp = await client.post("/auth/register", json=payload)
    assert register_resp.status_code == 201

    resp = await client.post(
        "/auth/cookie/login",
        data={"username": email, "password": "wrongpassword"},
    )
    assert resp.status_code in (400, 401)
