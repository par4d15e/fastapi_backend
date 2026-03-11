async def test_create_and_read_profile(client):
    payload = {"name": "bob", "gender": "male", "variety": "v2", "birthday": None}
    r = await client.post("/profiles/", json=payload)
    assert r.status_code in (200, 201)

    r2 = await client.get("/profiles/bob")
    assert r2.status_code == 200
    data = r2.json()
    assert data["name"] == "bob"
