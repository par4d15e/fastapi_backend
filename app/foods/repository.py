from typing import Any, Mapping

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.foods.model import Food


class FoodRepository:
    """Food CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, food_id: int) -> Food | None:
        food = await self.session.get(Food, food_id)
        if not food:
            return None

        return food

    async def get_by_name(self, food_name: str) -> Food | None:
        result = await self.session.execute(select(Food).where(Food.name == food_name))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Food]:
        """获取所有数据"""
        query = select(Food)

        # 1. 搜索
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Food.name.ilike(pattern),
                    Food.description.ilike(pattern),
                )
            )

        # 2. 排序
        allowed_sort = {"id", "name", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Food, order_by, Food.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        # 3. 分页
        limit = min(limit, 500)
        offset = max(offset, 0)
        paginated_query = query.offset(offset).limit(limit)
        result = await self.session.execute(paginated_query)
        return list(result.scalars().all())

    async def create(self, food_data: Mapping[str, Any]) -> Food:
        food = Food(**food_data)
        self.session.add(food)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(food)
        return food

    async def update(
        self,
        food_id: int,
        food_data: Mapping[str, Any],
    ) -> Food | None:
        food = await self.get_by_id(food_id)
        if not food:
            return None

        for key, value in food_data.items():
            setattr(food, key, value)
        await self.session.commit()
        await self.session.refresh(food)
        return food

    async def delete(self, food_id: int) -> bool:
        food = await self.get_by_id(food_id)
        if not food:
            return False

        await self.session.delete(food)
        await self.session.commit()
        return True
