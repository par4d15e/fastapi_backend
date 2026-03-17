from typing import Any, Mapping

from sqlalchemy import asc, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.weights.model import WeightRecord


class WeightRecordRepository:
    """WeightRecord CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: int) -> WeightRecord | None:
        return await self.session.get(WeightRecord, record_id)

    async def get_by_profile_id(
        self,
        profile_id: int,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """获取指定宠物的所有体重记录"""
        query = select(WeightRecord).where(WeightRecord.profile_id == profile_id)

        allowed_sort = {"id", "measured_at", "weight_g"}
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

    async def get_all(
        self,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecord]:
        """获取所有体重记录"""
        query = select(WeightRecord)

        allowed_sort = {"id", "measured_at", "weight_g", "profile_id"}
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

    async def create(self, data: Mapping[str, Any]) -> WeightRecord:
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
        record = await self.get_by_id(record_id)
        if not record:
            return None

        for key, value in data.items():
            setattr(record, key, value)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def delete(self, record_id: int) -> bool:
        record = await self.get_by_id(record_id)
        if not record:
            return False

        await self.session.delete(record)
        await self.session.commit()
        return True
