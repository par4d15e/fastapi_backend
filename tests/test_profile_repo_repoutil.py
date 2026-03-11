from app.profiles.repo_repoutil import ProfileRepoUtil
from app.profiles.schema import ProfileCreate, ProfileUpdate


async def test_profile_repo_repoutil_crud(session_factory):
    async with session_factory() as session:
        repo = ProfileRepoUtil(session)

        # create
        p_in = ProfileCreate(
            name="charlie", gender="male", variety="v-test", birthday=None
        )
        created = await repo.create(p_in)
        assert created.id is not None

        # get by name
        got = await repo.get_by_name("charlie")
        assert got and got.id == created.id

        # list all
        all_list = await repo.list_all()
        assert any(item.id == created.id for item in all_list)

        # update
        update_payload = ProfileUpdate(variety="v-updated")
        updated = await repo.update(created, update_payload)
        assert updated.variety == "v-updated"

        # delete
        deleted = await repo.delete(created.id)
        assert deleted is True

        # verify deletion with a fresh session (avoid identity-map caching)
        async with session_factory() as s:
            repo2 = ProfileRepoUtil(s)
            got_after = await repo2.get_by_id(created.id)
            assert got_after is None
