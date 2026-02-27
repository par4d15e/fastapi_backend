import pytest

from app.profiles import repository
from app.profiles.schema import ProfileCreate


@pytest.mark.anyio
async def test_create_and_get(session_factory):
    async with session_factory() as session:
        p_in = ProfileCreate(name="alice", gender="female", variety="v1", birthday=None)
        created = await repository.create(session, p_in)
        assert created.id is not None
        got = await repository.get_by_name(session, "alice")
        assert got and got.id == created.id
