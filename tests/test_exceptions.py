import pytest


@pytest.mark.anyio
async def test_404_for_missing(client):
    email = "dummy@example.com"
    password = "secret123"
    await client.post("/auth/register", json={"email": email, "password": password})
    await client.post(
        "/auth/cookie/login",
        data={"username": email, "password": password},
    )

    r = await client.get("/profiles/nonexistent")
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body
    assert body["detail"] == "Profile not found"
