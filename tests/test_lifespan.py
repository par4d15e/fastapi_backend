import pytest

from app.core import config, lifespan


@pytest.mark.anyio
async def test_lifespan_calls(monkeypatch):
    called = {"create": False, "dispose": False}

    async def fake_create():
        called["create"] = True

    async def fake_dispose():
        called["dispose"] = True

    class FakeDB:
        async def create_tables(self):
            await fake_create()

        async def dispose(self):
            await fake_dispose()

    monkeypatch.setattr("app.core.lifespan.db", FakeDB())

    config.settings.debug = True
    # pass a minimal FastAPI instance instead of None to satisfy type checker
    from fastapi import FastAPI

    async with lifespan.lifespan(FastAPI()):
        assert called["create"]
    assert called["dispose"]
