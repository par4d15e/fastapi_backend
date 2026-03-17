from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.foods.repository import FoodRepository
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate
from app.reminders.repository import ReminderRepository
from app.weights.repository import WeightRecordRepository


async def _create_profile_id(session_factory) -> int:
    async with session_factory() as session:
        repo = ProfileRepository(session)
        profile = await repo.create(
            ProfileCreate(
                name=f"pet-{uuid4().hex[:8]}",
                gender="male",
                variety="mixed",
                birthday=None,
                meals_per_day=2,
                is_neutered=False,
                activity_level="medium",
                is_obese=False,
            ).model_dump()
        )
        assert profile.id is not None
        return profile.id


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


async def test_weight_repository_crud(session_factory):
    profile_id = await _create_profile_id(session_factory)

    async with session_factory() as session:
        repo = WeightRecordRepository(session)
        created = await repo.create(
            {
                "profile_id": profile_id,
                "weight_g": 8500,
                "measured_at": datetime.now(tz=timezone.utc),
            }
        )
        assert created.id is not None

        got = await repo.get_by_id(created.id)
        assert got is not None
        assert got.profile_id == profile_id

        listed = await repo.get_by_profile_id(profile_id)
        assert any(item.id == created.id for item in listed)

        updated = await repo.update(created.id, {"weight_g": 8600})
        assert updated is not None
        assert updated.weight_g == 8600

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
    profile_id = await _create_profile_id(session_factory)

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
    profile_id = await _create_profile_id(session_factory)

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
            }
        )
        assert food.id is not None

        await weight_repo.create(
            {
                "profile_id": profile_id,
                "weight_g": 9000,
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
        "goal": {
            "daily_kcals": 120.0,
        },
    }
    resp = await client.post("/nutrition/plans", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["profile_id"] == profile_id
    assert data["daily_kcals_target"] == 120.0
    assert len(data["foods"]) == 1
    assert data["total_kcals"] > 0
