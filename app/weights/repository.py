from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.families.model import FamilyMember
from app.profiles.model import Profile
from app.weights.model import WeightRecord


class WeightRecordRepository:
    """WeightRecord CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        """初始化WeightRecordRepository。"""
        self.session = session

    async def _get_by_id(self, record_id: int) -> WeightRecord | None:
        """处理体重记录数据访问。"""
        return await self.session.get(WeightRecord, record_id)

    async def _get_by_profile_id(
        self,
        profile_id: int,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """处理体重记录数据访问。"""
        query = select(WeightRecord).where(WeightRecord.profile_id == profile_id)

        allowed_sort = {"id", "measured_at", "weight_kg"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    # 管理员查询 (不进行用户过滤，直接查询数据库)
    async def get_by_id(self, record_id: int) -> WeightRecord | None:
        """根据 ID 查询体重记录。"""
        return await self._get_by_id(record_id)

    async def get_by_profile_id(
        self,
        profile_id: int,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """根据档案 ID 查询体重记录。"""
        return await self._get_by_profile_id(
            profile_id,
            order_by=order_by,
            direction=direction,
            limit=limit,
            offset=offset,
        )

    async def get_all(
        self,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """查询全部体重记录。"""
        query = select(WeightRecord)

        allowed_sort = {"id", "measured_at", "weight_kg", "profile_id"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    # 查询 (根据用户权限)
    async def get_by_id_and_user(
        self,
        record_id: int,
        user_id: UUID,
    ) -> WeightRecord | None:
        """根据 ID 查询当前用户可访问的体重记录。"""
        result = await self.session.execute(
            select(WeightRecord)
            .join(Profile)
            .where(WeightRecord.id == record_id, Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def is_profile_accessible_by_user(
        self,
        profile_id: int,
        user_id: UUID,
    ) -> bool:
        """判断档案是否对当前用户可访问。"""
        result = await self.session.execute(
            select(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(
                Profile.id == profile_id,
                or_(Profile.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_by_id_and_user_or_family(
        self,
        record_id: int,
        user_id: UUID,
    ) -> WeightRecord | None:
        """根据 ID 查询当前用户及其家庭可访问的体重记录。"""
        result = await self.session.execute(
            select(WeightRecord)
            .join(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(
                WeightRecord.id == record_id,
                or_(Profile.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_profile_id_and_user(
        self,
        profile_id: int,
        user_id: UUID,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """处理体重记录数据访问。"""
        query = (
            select(WeightRecord)
            .join(Profile)
            .where(WeightRecord.profile_id == profile_id, Profile.user_id == user_id)
        )

        allowed_sort = {"id", "measured_at", "weight_kg"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    async def get_by_profile_id_and_user_or_family(
        self,
        profile_id: int,
        user_id: UUID,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """处理体重记录数据访问。"""
        query = (
            select(WeightRecord)
            .join(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(
                WeightRecord.profile_id == profile_id,
                or_(Profile.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )

        allowed_sort = {"id", "measured_at", "weight_kg"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    async def get_all_by_user(
        self,
        user_id: UUID,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """查询当前用户可访问的体重记录列表。"""
        query = select(WeightRecord).join(Profile).where(Profile.user_id == user_id)

        allowed_sort = {"id", "measured_at", "weight_kg", "profile_id"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    async def get_all_by_user_or_family(
        self,
        user_id: UUID,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """查询当前用户及其家庭可访问的体重记录列表。"""
        query = (
            select(WeightRecord)
            .join(Profile)
            .outerjoin(FamilyMember, FamilyMember.family_id == Profile.family_id)
            .where(or_(Profile.user_id == user_id, FamilyMember.user_id == user_id))
        )

        allowed_sort = {"id", "measured_at", "weight_kg", "profile_id"}
        if order_by not in allowed_sort:
            order_by = "measured_at"
        order_column = getattr(WeightRecord, order_by, WeightRecord.measured_at)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    # 增删改：不区分管理员和普通用户，直接执行数据库操作
    async def create(self, data: Mapping[str, Any]) -> WeightRecord:
        """创建体重记录。"""
        record = WeightRecord(**data)
        self.session.add(record)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(record)
        return record

    async def update(
        self,
        record_id: int,
        data: Mapping[str, Any],
    ) -> WeightRecord | None:
        """更新体重记录。"""
        record = await self._get_by_id(record_id)
        if not record:
            return None

        for key, value in data.items():
            setattr(record, key, value)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def delete(self, record_id: int) -> bool:
        """删除体重记录。"""
        record = await self._get_by_id(record_id)
        if not record:
            return False

        await self.session.delete(record)
        await self.session.commit()
        return True
