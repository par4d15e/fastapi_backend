from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.families.model import FamilyMember
from app.foods.model import Food


class FoodRepository:
    """Food CRUD"""

    def __init__(self, session: AsyncSession) -> None:
        """初始化FoodRepository。"""
        self.session = session

    # 私有方法：不进行权限过滤，直接查询数据库
    async def _get_by_id(self, food_id: int) -> Food | None:
        """处理食物数据访问。"""
        food = await self.session.get(Food, food_id)
        if not food:
            return None

        return food

    async def _get_by_name(self, food_name: str) -> Food | None:
        """处理食物数据访问。"""
        result = await self.session.execute(select(Food).where(Food.name == food_name))
        return result.scalar_one_or_none()

    # 管理员查询 (不进行用户过滤，直接查询数据库)
    async def get_by_id(self, food_id: int) -> Food | None:
        """根据 ID 查询食物。"""
        return await self._get_by_id(food_id)

    async def get_by_name(self, food_name: str) -> Food | None:
        """根据名称查询食物。"""
        return await self._get_by_name(food_name)

    async def get_all(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Food]:
        """查询全部食物。"""
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

    # 查询 (根据用户权限)
    async def get_by_id_and_user(self, food_id: int, user_id: UUID) -> Food | None:
        """根据 ID 查询当前用户可访问的食物。"""
        result = await self.session.execute(
            select(Food).where(Food.id == food_id, Food.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user_or_family(
        self, food_id: int, user_id: UUID
    ) -> Food | None:
        """根据 ID 查询当前用户及其家庭可访问的食物。"""
        result = await self.session.execute(
            select(Food)
            .outerjoin(FamilyMember, FamilyMember.family_id == Food.family_id)
            .where(
                Food.id == food_id,
                or_(Food.user_id == user_id, FamilyMember.user_id == user_id),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_user(self, food_name: str, user_id: UUID) -> Food | None:
        """根据名称查询当前用户可访问的食物。"""
        result = await self.session.execute(
            select(Food).where(Food.name == food_name, Food.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_user_or_family(
        self, food_name: str, user_id: UUID
    ) -> Food | None:
        """根据名称查询当前用户及其家庭可访问的食物。"""
        result = await self.session.execute(
            select(Food)
            .outerjoin(FamilyMember, FamilyMember.family_id == Food.family_id)
            .where(
                Food.name == food_name,
                or_(Food.user_id == user_id, FamilyMember.user_id == user_id),
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
    ) -> list[Food]:
        """查询当前用户可访问的食物列表。"""
        query = select(Food).where(Food.user_id == user_id)

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

    async def get_all_by_user_or_family(
        self,
        user_id: UUID,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[Food]:
        """查询当前用户及其家庭可访问的食物列表。"""
        query = (
            select(Food)
            .outerjoin(FamilyMember, FamilyMember.family_id == Food.family_id)
            .where(or_(Food.user_id == user_id, FamilyMember.user_id == user_id))
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(
                    Food.name.ilike(pattern),
                    Food.description.ilike(pattern),
                )
            )

        allowed_sort = {"id", "name", "created_at"}
        if order_by not in allowed_sort:
            order_by = "id"
        order_column = getattr(Food, order_by, Food.id)
        query = query.order_by(
            desc(order_column) if direction == "desc" else asc(order_column)
        )

        limit = min(limit, 500)
        offset = max(offset, 0)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all())

    # 增删改：不区分管理员和普通用户，直接执行数据库操作
    async def create(self, food_data: Mapping[str, Any]) -> Food:
        """创建食物。"""
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
        """更新食物。"""
        food = await self._get_by_id(food_id)
        if not food:
            return None

        for key, value in food_data.items():
            setattr(food, key, value)
        await self.session.commit()
        await self.session.refresh(food)
        return food

    async def delete(self, food_id: int) -> bool:
        """删除食物。"""
        food = await self._get_by_id(food_id)
        if not food:
            return False

        await self.session.delete(food)
        await self.session.commit()
        return True
