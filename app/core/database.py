from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.base_model import Base
from app.core.config import settings


class Database:
    def __init__(self, url: str, **engine_options) -> None:
        """初始化数据库管理器。"""
        self.engine = create_async_engine(url, **engine_options)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """创建并返回一个异步数据库会话。"""
        async with self.session_factory() as session:
            yield session

    async def create_tables(self) -> None:
        """创建所有数据库表。"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        """释放数据库连接资源。"""
        await self.engine.dispose()


# 单例，用作应用级依赖
db = Database(settings.database_url, **settings.engine_options)

# 方便导入：在其它模块仍可以直接 `from app.core.database import db` 或 `from app.core.database import db as database`
get_session = db.get_session  # 用于 FastAPI Depends(get_session)
