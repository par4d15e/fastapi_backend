from uuid import uuid4


async def _register_user(client, *, prefix: str) -> dict[str, str]:
    email = f"{prefix}-{uuid4().hex[:8]}@example.com"
    password = "secret123"

    register_resp = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_resp.status_code == 201

    login_resp = await client.post(
        "/auth/cookie/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code in (200, 204)

    me_resp = await client.get("/users/me")
    assert me_resp.status_code == 200
    return {"email": email, "password": password, "id": me_resp.json()["id"]}


async def test_family_crud_and_membership_routes(client):
    owner = await _register_user(client, prefix="family-route-owner")
    owner_id = owner["id"]
    family_payload = {
        "name": f"family-{uuid4().hex[:8]}",
        "description": "共享家庭",
    }

    created = await client.post("/families/", json=family_payload)
    assert created.status_code == 201
    family = created.json()
    assert family["owner_id"] == owner_id

    listed = await client.get("/families/")
    assert listed.status_code == 200
    assert any(item["id"] == family["id"] for item in listed.json())

    member = await _register_user(client, prefix="family-route-member")
    member_id = member["id"]

    await client.post(
        "/auth/cookie/login",
        data={"username": owner["email"], "password": owner["password"]},
    )

    added = await client.post(
        f"/families/{family['id']}/members",
        json={"user_id": member_id, "role": "member"},
    )
    assert added.status_code == 201
    assert added.json()["user_id"] == member_id

    # 重新登录成员账号，确认可以访问家庭详情
    login_resp = await client.post(
        "/auth/cookie/login",
        data={"username": member["email"], "password": member["password"]},
    )
    assert login_resp.status_code in (200, 204)

    got = await client.get(f"/families/{family['id']}")
    assert got.status_code == 200
    assert got.json()["id"] == family["id"]


async def test_family_invite_acceptance_routes(client):
    await _register_user(client, prefix="family-invite-owner")
    family_payload = {
        "name": f"family-{uuid4().hex[:8]}",
        "description": "邀请加入家庭",
    }

    created = await client.post("/families/", json=family_payload)
    assert created.status_code == 201
    family = created.json()

    invite_resp = await client.post(
        f"/families/{family['id']}/invites",
        json={"expires_in_hours": 24},
    )
    assert invite_resp.status_code == 201
    invite = invite_resp.json()
    assert invite["family_id"] == family["id"]
    assert invite["token"]

    member = await _register_user(client, prefix="family-invite-member")
    login_resp = await client.post(
        "/auth/cookie/login",
        data={"username": member["email"], "password": member["password"]},
    )
    assert login_resp.status_code in (200, 204)

    accepted = await client.post("/families/invites/accept", json={"token": invite["token"]})
    assert accepted.status_code == 201
    assert accepted.json()["family_id"] == family["id"]

    got = await client.get(f"/families/{family['id']}")
    assert got.status_code == 200
    assert got.json()["id"] == family["id"]
