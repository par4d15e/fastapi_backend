from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate, ProfileUpdate


async def test_profile_repository_crud(session_factory):
    async with session_factory() as session:
        repo = ProfileRepository(session)

        # create
        # include all fields to satisfy static type checker defaults
        p_in = ProfileCreate(
            name="charlie",
            gender="male",
            variety="v-test",
            birthday=None,
            meals_per_day=2,
            is_neutered=False,
            activity_level="medium",
            is_obese=False,
        )  # type: ignore[arg-type]

        created = await repo.create(p_in.model_dump())
        assert created.id is not None

        # get by name
        got = await repo._get_by_name("charlie")
        assert got and got.id == created.id

        # list all
        all_list = await repo.get_all()
        assert any(item.id == created.id for item in all_list)

        # update
        # explicitly pass None for optional fields to satisfy Pylance
        update_payload = ProfileUpdate(
            variety="v-updated",
            name=None,
            gender=None,
            birthday=None,
            meals_per_day=None,
            is_neutered=None,
            activity_level=None,
            is_obese=None,
        )  # type: ignore[arg-type]

        updated = await repo.update(
            created.id,
            update_payload.model_dump(exclude_unset=True, exclude_none=True),
        )
        assert updated and updated.variety == "v-updated"

        # delete
        deleted = await repo.delete(created.id)
        assert deleted is True

        # verify deletion with a fresh session (avoid identity-map caching)
        async with session_factory() as s:
            repo2 = ProfileRepository(s)
            got_after = await repo2._get_by_id(created.id)
            assert got_after is None
