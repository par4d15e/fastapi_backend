from typing import Any, Mapping

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.reminders.model import Reminder


class ReminderRepository:
    """Reminder CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, reminder_id: int) -> Reminder | None:
        reminder = await self.session.get(Reminder, reminder_id)
        if not reminder:
            return None

        return reminder

    async def get_by_profile_id(
        self,
        profile_id: int,
        *,
        order_by: str = "due_date",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Reminder]:
        query = select(Reminder).where(Reminder.profile_id == profile_id)

        allowed_sort = {"id", "title", "due_date", "created_at"}
        if order_by not in allowed_sort:
            order_by = "due_date"
        order_column = getattr(Reminder, order_by, Reminder.due_date)
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
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Reminder]:
        """获取所有数据"""
        query = select(Reminder)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Reminder.title.ilike(pattern),
                    Reminder.description.ilike(pattern),
                )
            )

        # 2. 排序
        allowed_sort = {"id", "title", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Reminder, order_by, Reminder.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        # 3. 分页
        limit = min(limit, 500)
        offset = max(offset, 0)
        paginated_query = query.offset(offset).limit(limit)

        result = await self.session.execute(paginated_query)
        return list(result.scalars().all())

    async def search_by_title_trgm(
        self,
        keyword: str,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Reminder]:
        """使用 pg_trgm GIN 索引进行标题模糊搜索（ILIKE）"""
        pattern = f"%{keyword}%"
        statement = (
            select(Reminder)
            .where(Reminder.title.ilike(pattern))
            .offset(max(offset, 0))
            .limit(min(limit, 500))
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create(self, data: Mapping[str, Any]) -> Reminder:
        reminder = Reminder(**data)
        self.session.add(reminder)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def update(
        self, reminder_id: int, data: Mapping[str, Any]
    ) -> Reminder | None:
        reminder = await self.get_by_id(reminder_id)
        if not reminder:
            return None

        for key, value in data.items():
            setattr(reminder, key, value)

        self.session.add(reminder)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(reminder)
        return reminder

    async def delete(self, reminder_id: int) -> bool:
        reminder = await self.get_by_id(reminder_id)
        if not reminder:
            return False

        await self.session.delete(reminder)
        await self.session.commit()
        return True
