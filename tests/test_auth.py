from app.core import security


async def test_login_success(client):
    # create a user via the public users endpoint
    payload = {"username": "john", "email": "john@example.com", "password": "secret123"}
    r = await client.post("/users/", json=payload)
    assert r.status_code == 201

    # attempt login with email
    resp = await client.post(
        "/auth/login", json={"email": "john@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert security.decode_access_token(data["access_token"]) is not None
    # refresh token should also be issued
    assert data.get("refresh_token") is not None

    # verify we can read it back via the auth API
    r2 = await client.get(f"/auth/refresh-tokens/{data['refresh_token']}")
    assert r2.status_code == 200
    info = r2.json()
    # token itself is not exposed, but we should get metadata
    assert "id" in info
    assert info.get("is_active") is True

    # revoke all tokens for this user should affect at least one
    user_id = info["user_id"]
    r3 = await client.delete(f"/auth/refresh-tokens/user/{user_id}")
    assert r3.status_code == 200
    assert isinstance(r3.json(), int)


async def test_login_wrong_password(client):
    payload = {"username": "jane", "email": "jane@example.com", "password": "pw123456"}
    r = await client.post("/users/", json=payload)
    assert r.status_code == 201

    resp = await client.post(
        "/auth/login", json={"email": "jane@example.com", "password": "wrongpassword"}
    )
    assert resp.status_code == 401
