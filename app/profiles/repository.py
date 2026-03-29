from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.families.model import FamilyMember
from app.profiles.model import Profile


class ProfileRepository:
    """Profile CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        """初始化ProfileRepository。"""
        self.session = session

    # 私有方法：不进行权限过滤，直接查询数据库
    async def _get_by_id(self, profile_id: int) -> Profile | None:
        """处理档案数据访问。"""
        return await self.session.get(Profile, profile_id)

    async def _get_by_name(self, profile_name: str) -> Profile | None:
        """处理档案数据访问。"""
        result = await self.session.execute(
            select(Profile).where(Profile.name == profile_name)
        )
        return result.scalar_one_or_none()

    # 管理员查询 (不进行用户过滤，直接查询数据库)
    async def get_by_id(self, profile_id: int) -> Profile | None:
        """根据 ID 查询档案。"""
        return await self._get_by_id(profile_id)

    async def get_by_name(self, profile_name: str) -> Profile | None:
        """根据名称查询档案。"""
        return await self._get_by_name(profile_name)

    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Profile]:
        """查询全部档案。"""
        query = select(Profile)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Profile.name.ilike(pattern),
                    Profile.description.ilike(pattern),
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
        result = await self.session.execute(paginated_query)
        return list(result.scalars().all())

    # 查询 (根据用户权限)
    async def get_by_id_and_user(
        self,
        profile_id: int,
        user_id: UUID,
    ) -> Profile | None:
        """根据 ID 查询当前用户可访问的档案。"""
        result = await self.session.execute(
            select(Profile).where(Profile.id == profile_id, Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user_or_family(
        self,
        profile_id: int,
        user_id: UUID,
    ) -> Profile | None:
        """根据 ID 查询当前用户及其家庭可访问的档案。"""
        result = await self.session.execute(
            select(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(
                Profile.id == profile_id,
                or_(Profile.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_user(
        self, profile_name: str, user_id: UUID
    ) -> Profile | None:
        """根据名称查询当前用户可访问的档案。"""
        result = await self.session.execute(
            select(Profile).where(
                Profile.name == profile_name, Profile.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_user_or_family(
        self, profile_name: str, user_id: UUID
    ) -> Profile | None:
        """根据名称查询当前用户及其家庭可访问的档案。"""
        result = await self.session.execute(
            select(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(
                Profile.name == profile_name,
                or_(Profile.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: UUID,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Profile]:
        """查询当前用户可访问的档案列表。"""
        query = select(Profile).where(Profile.user_id == user_id)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Profile.name.ilike(pattern),
                    Profile.description.ilike(pattern),
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
        result = await self.session.execute(paginated_query)
        return list(result.scalars().all())

    async def get_all_by_user_or_family(
        self,
        user_id: UUID,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Profile]:
        """查询当前用户及其家庭可访问的档案列表。"""
        query = (
            select(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(or_(Profile.user_id == user_id, FamilyMember.user_id == user_id))
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Profile.name.ilike(pattern),
                    Profile.description.ilike(pattern),
                )
            )

        allowed_sort = {"id", "name", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Profile, order_by, Profile.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    # 增删改：不区分管理员和普通用户，直接执行数据库操作
    async def create(self, profile_data: Mapping[str, Any]) -> Profile:
        """创建档案。"""
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
        """更新档案。"""
        profile = await self._get_by_id(profile_id)
        if not profile:
            return None

        for key, value in profile_data.items():
            setattr(profile, key, value)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def delete(self, profile_id: int) -> bool:
        """删除档案。"""
        profile = await self._get_by_id(profile_id)
        if not profile:
            return False

        await self.session.delete(profile)
        await self.session.commit()
        return True
