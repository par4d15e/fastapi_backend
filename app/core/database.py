from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


class Database:
    def __init__(self, url: str, **engine_options) -> None:
        self.engine = create_async_engine(url, **engine_options)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def dispose(self) -> None:
        """关闭并清理底层 engine (封装 engine.dispose)

        这是面向对象的 API, 推荐在应用关闭处调用 `await db.dispose()` 而不是直接访问
        `engine`。保留 engine 导出用于兼容测试/现有代码。
        """
        await self.engine.dispose()


# 单例，用作应用级依赖
db = Database(settings.database_url, **settings.engine_options)

# 方便导入：在其它模块仍可以直接 `from app.core.database import db` 或 `from app.core.database import db as database`
get_session = db.get_session  # 用于 FastAPI Depends(get_session)
