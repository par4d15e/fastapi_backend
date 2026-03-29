from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate


async def test_create_and_get(session_factory):
    async with session_factory() as session:
        p_in = ProfileCreate(
            name="alice",
            gender="female",
            variety="v1",
            birthday=None,
            meals_per_day=2,
            is_neutered=False,
            activity_level="medium",
            is_obese=False,
        )
        repo = ProfileRepository(session)
        created = await repo.create(p_in.model_dump())
        assert created.id is not None
        got = await repo.get_by_name("alice")
        assert got and got.id == created.id
