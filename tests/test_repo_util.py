import pytest

from app.core.repo_util import RepoUtil
from app.profiles.model import Profile
from app.profiles.schema import ProfileCreate


@pytest.mark.anyio
async def test_repo_util_crud(session_factory):
    async with session_factory() as session:
        # create via model
        p_in = ProfileCreate(name="bob", gender="male", variety="v2", birthday=None)
        created = await RepoUtil.create_from_model(session, Profile, p_in)
        assert created.id is not None

        # get by id
        got = await RepoUtil.get_by_id(session, Profile, created.id)
        assert got is not None and got.id == created.id

        # get all
        all_list = await RepoUtil.get_all(session, Profile)
        assert any(item.id == created.id for item in all_list)

        # update
        update_data = {"variety": "v3"}
        updated = await RepoUtil.update(session, created, update_data)
        assert updated.variety == "v3"

        # delete
        deleted = await RepoUtil.delete(session, created)
        assert deleted is True

        # verify deletion from a fresh session to avoid identity-map caching
        async with session_factory() as s:
            got_after = await RepoUtil.get_by_id(s, Profile, created.id)
            assert got_after is None


@pytest.mark.anyio
async def test_repo_util_create_instance(session_factory):
    async with session_factory() as session:
        entity = Profile(name="x", gender="female", variety="v4", birthday=None)
        created = await RepoUtil.create(session, entity)
        assert created.id is not None
        # cleanup
        await RepoUtil.delete(session, created)
