from uuid import UUID, uuid4

from app.families.model import Family, FamilyMember
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate


async def _create_user(client) -> str:
    email = f"family-{uuid4().hex[:8]}@example.com"
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
    return me_resp.json()["id"]


async def test_family_tables_and_profile_family_binding(client, session_factory):
    owner_id = await _create_user(client)

    async with session_factory() as session:
        family = Family(
            name=f"family-{uuid4().hex[:8]}",
            owner_id=owner_id,
            description="共享家庭",
        )
        session.add(family)
        await session.commit()
        await session.refresh(family)

        member = FamilyMember(
            family_id=family.id,
            user_id=owner_id,
            role="owner",
        )
        session.add(member)
        await session.commit()
        await session.refresh(member)

        profile_repo = ProfileRepository(session)
        profile_data = ProfileCreate(
            name=f"pet-{uuid4().hex[:8]}",
            gender="female",
            variety="mix",
            birthday=None,
            meals_per_day=2,
            is_neutered=False,
            activity_level="medium",
            is_obese=False,
        )
        payload = profile_data.model_dump()
        payload["user_id"] = owner_id
        payload["family_id"] = family.id
        profile = await profile_repo.create(payload)

    assert family.id is not None
    assert member.id is not None
    assert member.family_id == family.id
    assert member.user_id == UUID(owner_id)
    assert profile.family_id == family.id
