async def test_create_and_read_profile(client):
    email = "bob@example.com"
    password = "secret123"

    register_resp = await client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert register_resp.status_code == 201

    login_resp = await client.post(
        "/auth/cookie/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code in (200, 204)

    payload = {"name": "bob", "gender": "male", "variety": "v2", "birthday": None}
    r = await client.post("/profiles/", json=payload)
    assert r.status_code == 201

    r2 = await client.get("/profiles/bob")
    assert r2.status_code == 200
    data = r2.json()
    assert data["name"] == "bob"
