from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import update

from app.auth.model import User
from app.foods.repository import FoodRepository
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate
from app.reminders.repository import ReminderRepository
from app.weights.repository import WeightRecordRepository


async def _create_profile_id(session_factory, user_id=None) -> int:
    async with session_factory() as session:
        repo = ProfileRepository(session)
        profile_data = ProfileCreate(
            name=f"pet-{uuid4().hex[:8]}",
            gender="male",
            variety="mixed",
            birthday=None,
            meals_per_day=2,
            is_neutered=False,
            activity_level="medium",
            is_obese=False,
        ).model_dump()
        if user_id is not None:
            profile_data["user_id"] = user_id

        profile = await repo.create(profile_data)
        assert profile.id is not None
        return profile.id


async def _create_user(client):
    email = f"user-{uuid4().hex[:8]}@example.com"
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


async def test_food_repository_crud(session_factory):
    async with session_factory() as session:
        repo = FoodRepository(session)
        food_name = f"food-{uuid4().hex[:8]}"

        created = await repo.create(
            {
                "name": food_name,
                "brand": "brand-a",
                "metabolic_energy": 3.8,
                "price": 19.9,
                "weight": 1.0,
                "description": "balanced kibble",
            }
        )
        assert created.id is not None

        got = await repo.get_by_name(food_name)
        assert got is not None
        assert got.id == created.id

        updated = await repo.update(created.id, {"price": 21.5})
        assert updated is not None
        assert updated.price == 21.5

        deleted = await repo.delete(created.id)
        assert deleted is True


async def test_food_access_requires_owner(client, session_factory):
    # user1 创建食物
    user1 = await _create_user(client)
    profile1 = await _create_profile_id(session_factory, user_id=user1)

    async with session_factory() as session:
        food_repo = FoodRepository(session)
        food = await food_repo.create(
            {
                "name": f"food-{uuid4().hex[:8]}",
                "brand": "brand-x",
                "metabolic_energy": 5.0,
                "price": 20.0,
                "weight": 1.0,
                "description": "private food",
                "user_id": user1,
            }
        )
    assert food.id is not None

    # user2 试图访问 user1 的 food（非超管，应拒绝）
    user2 = await _create_user(client)

    got = await client.get(f"/foods/{food.name}")
    assert got.status_code == 404

    r = await client.post(
        "/nutrition/plans",
        json={
            "profile_id": profile1,
            "foods": [{"food_id": food.id, "ratio": 1.0}],
            "daily_kcals": 120.0,
        },
    )
    assert r.status_code == 404


async def _set_superuser(session_factory, user_id: str) -> None:
    async with session_factory() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(is_superuser=True)
        )
        await session.commit()


async def test_superuser_can_access_other_user_resources(client, session_factory):
    user1 = await _create_user(client)

    # user1 创建资源
    profile_name = f"superuser-profile-{uuid4().hex[:8]}"
    async with session_factory() as session:
        profile_repo = ProfileRepository(session)
        profile = await profile_repo.create(
            {
                "name": profile_name,
                "gender": "female",
                "variety": "tabby",
                "birthday": None,
                "meals_per_day": 3,
                "is_neutered": True,
                "activity_level": "medium",
                "is_obese": False,
                "user_id": user1,
            }
        )
        assert profile.id is not None

        food_repo = FoodRepository(session)
        food = await food_repo.create(
            {
                "name": f"superuser-food-{uuid4().hex[:8]}",
                "brand": "brand-super",
                "metabolic_energy": 4.5,
                "price": 11.5,
                "weight": 1.0,
                "description": "cross-user food",
                "user_id": user1,
            }
        )
        assert food.id is not None

        weight_repo = WeightRecordRepository(session)
        weight = await weight_repo.create(
            {
                "profile_id": profile.id,
                "weight_kg": 7.2,
                "measured_at": datetime.now(tz=timezone.utc),
            }
        )
        assert weight.id is not None

        reminder_repo = ReminderRepository(session)
        reminder = await reminder_repo.create(
            {
                "title": f"superuser-reminder-{uuid4().hex[:8]}",
                "type": "care",
                "due_date": datetime.now(tz=timezone.utc) + timedelta(days=1),
                "is_done": False,
                "description": "superuser crosses boundary",
                "profile_id": profile.id,
            }
        )
        assert reminder.id is not None

    # user2 登录并提升为超管
    user2 = await _create_user(client)
    await _set_superuser(session_factory, user2)

    # 作为超管访问 user1 的资源
    profile_resp = await client.get(f"/profiles/{profile_name}")
    assert profile_resp.status_code == 200
    assert profile_resp.json()["id"] == profile.id

    food_resp = await client.get(f"/foods/{food.name}")
    assert food_resp.status_code == 200
    assert food_resp.json()["id"] == food.id

    weight_resp = await client.get(f"/weights/{weight.id}")
    assert weight_resp.status_code == 200
    assert weight_resp.json()["id"] == weight.id

    reminder_resp = await client.get(f"/reminders/{reminder.id}")
    assert reminder_resp.status_code == 200
    assert reminder_resp.json()["id"] == reminder.id

    # 作为超管可以更新其他用户 profile
    update_profile = await client.patch(
        f"/profiles/{profile.id}", json={"activity_level": "high"}
    )
    assert update_profile.status_code == 200
    assert update_profile.json()["activity_level"] == "high"


async def test_weight_repository_crud(session_factory):
    profile_id = await _create_profile_id(session_factory)

    async with session_factory() as session:
        repo = WeightRecordRepository(session)
        created = await repo.create(
            {
                "profile_id": profile_id,
                "weight_kg": 8.5,
                "measured_at": datetime.now(tz=timezone.utc),
            }
        )
        assert created.id is not None

        got = await repo.get_by_id(created.id)
        assert got is not None
        assert got.profile_id == profile_id

        listed = await repo.get_by_profile_id(profile_id)
        assert any(item.id == created.id for item in listed)

        updated = await repo.update(created.id, {"weight_kg": 8.6})
        assert updated is not None
        assert updated.weight_kg == 8.6

        deleted = await repo.delete(created.id)
        assert deleted is True


async def test_reminder_repository_crud_and_search(session_factory):
    profile_id = await _create_profile_id(session_factory)

    async with session_factory() as session:
        repo = ReminderRepository(session)
        title = f"vaccine-{uuid4().hex[:8]}"

        created = await repo.create(
            {
                "title": title,
                "type": "health",
                "due_date": datetime.now(tz=timezone.utc) + timedelta(days=7),
                "is_done": False,
                "description": "next vaccine",
                "profile_id": profile_id,
            }
        )
        assert created.id is not None

        got = await repo.get_by_id(created.id)
        assert got is not None
        assert got.id == created.id

        searched = await repo.search_by_title_trgm("vaccine")
        assert any(item.id == created.id for item in searched)

        updated = await repo.update(created.id, {"is_done": True})
        assert updated is not None
        assert updated.is_done is True

        deleted = await repo.delete(created.id)
        assert deleted is True


async def test_reminder_get_by_id_endpoint(client, session_factory):
    user_id = await _create_user(client)
    profile_id = await _create_profile_id(session_factory, user_id=user_id)

    payload = {
        "title": f"groom-{uuid4().hex[:8]}",
        "type": "care",
        "due_date": (datetime.now(tz=timezone.utc) + timedelta(days=3)).isoformat(),
        "is_done": False,
        "description": "grooming plan",
        "profile_id": profile_id,
    }
    created = await client.post("/reminders/", json=payload)
    assert created.status_code == 201
    reminder_id = created.json()["id"]

    got = await client.get(f"/reminders/{reminder_id}")
    assert got.status_code == 200
    data = got.json()
    assert data["id"] == reminder_id
    assert data["profile_id"] == profile_id


async def test_nutrition_plan_endpoint(client, session_factory):
    user_id = await _create_user(client)
    profile_id = await _create_profile_id(session_factory, user_id=user_id)

    async with session_factory() as session:
        food_repo = FoodRepository(session)
        weight_repo = WeightRecordRepository(session)

        food = await food_repo.create(
            {
                "name": f"nutri-food-{uuid4().hex[:8]}",
                "brand": "brand-n",
                "metabolic_energy": 4.0,
                "price": 10.0,
                "weight": 1.0,
                "description": "for nutrition plan",
                "user_id": user_id,
            }
        )
        assert food.id is not None

        await weight_repo.create(
            {
                "profile_id": profile_id,
                "weight_kg": 9.0,
                "measured_at": datetime.now(tz=timezone.utc),
            }
        )

    payload = {
        "profile_id": profile_id,
        "foods": [
            {
                "food_id": food.id,
                "ratio": 1.0,
            }
        ],
        "daily_kcals": 120.0,
    }
    resp = await client.post("/nutrition/plans", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["profile_id"] == profile_id
    assert data["daily_kcals_target"] == 120.0
    assert len(data["foods"]) == 1
    assert data["total_kcals"] > 0
