from typing import Any, Mapping

from sqlalchemy.exc import IntegrityError
from sqlmodel import asc, col, desc, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.profiles.model import Profile


class ProfileRepository:
    """Profile CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, profile_id: int) -> Profile | None:
        profile = await self.session.get(Profile, profile_id)
        if not profile:
            return None

        return profile

    async def get_by_name(self, profile_name: str) -> Profile | None:
        statement = select(Profile).where(Profile.name == profile_name)
        result = await self.session.exec(statement)
        profile = result.one_or_none()
        return profile

    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Profile]:
        """获取所有数据"""
        query = select(Profile)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    col(Profile.name).ilike(pattern),
                    col(Profile.description).ilike(pattern),
                )
            )

        # 2. 排序
        allowed_sort = {"id", "name", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Profile, order_by, Profile.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        # 3. 分页
        limit = min(limit, 500)
        offset = max(offset, 0)
        paginated_query = query.offset(offset).limit(limit)
        profiles = list(await self.session.exec(paginated_query))

        return profiles

    async def create(self, profile_data: Mapping[str, Any]) -> Profile:
        profile = Profile(**profile_data)
        self.session.add(profile)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(profile)
        return profile

    async def update(
        self,
        profile_id: int,
        profile_data: Mapping[str, Any],
    ) -> Profile | None:
        profile = await self.get_by_id(profile_id)
        if not profile:
            return None

        for key, value in profile_data.items():
            setattr(profile, key, value)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def delete(self, profile_id: int) -> bool:
        profile = await self.get_by_id(profile_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.commit()
        return True
