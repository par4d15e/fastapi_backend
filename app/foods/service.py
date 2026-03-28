from sqlalchemy.exc import IntegrityError

from app.auth.model import User
from app.core.exception import AlreadyExistsException, NotFoundException
from app.foods.repository import FoodRepository
from app.foods.schema import FoodCreate, FoodResponse, FoodUpdate


class FoodService:
    """Food 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: FoodRepository) -> None:
        self.repository = repository

    def _is_superuser(self, user: User) -> bool:
        return bool(getattr(user, "is_superuser", False))

    async def get_food_by_name(
        self, food_name: str, current_user: User
    ) -> FoodResponse:
        if self._is_superuser(current_user):
            food = await self.repository.get_by_name(food_name)
        else:
            food = await self.repository.get_by_name_and_user(
                food_name, current_user.id
            )
        if not food:
            raise NotFoundException("Food not found")

        return FoodResponse.model_validate(food)

    async def get_food_by_id(self, food_id: int, current_user: User) -> FoodResponse:
        if self._is_superuser(current_user):
            food = await self.repository.get_by_id(food_id)
        else:
            food = await self.repository.get_by_id_and_user(food_id, current_user.id)
        if not food:
            raise NotFoundException("Food not found")

        return FoodResponse.model_validate(food)

    async def list_foods(
        self,
        current_user: User,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[FoodResponse]:
        """查询所有食物"""
        if self._is_superuser(current_user):
            foods = await self.repository.get_all(
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            foods = await self.repository.get_all_by_user(
                current_user.id,
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )

        return [FoodResponse.model_validate(food) for food in foods]

    async def create_food(
        self, food_data: FoodCreate, current_user: User
    ) -> FoodResponse:
        data = food_data.model_dump()
        data["user_id"] = current_user.id
        try:
            food = await self.repository.create(data)

            return FoodResponse.model_validate(food)
        except IntegrityError as e:
            raise AlreadyExistsException("Food with this name already exists") from e

    async def update_food(
        self,
        food_id: int,
        food_data: FoodUpdate,
        current_user: User,
    ) -> FoodResponse:
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(food_id)
        else:
            existing = await self.repository.get_by_id_and_user(
                food_id, current_user.id
            )
        if not existing:
            raise NotFoundException("Food not found")

        try:
            update_data = food_data.model_dump(exclude_unset=True, exclude_none=True)
            updated = await self.repository.update(food_id, update_data)
            if not updated:
                raise NotFoundException("Food not found")
            return FoodResponse.model_validate(updated)
        except IntegrityError as e:
            raise AlreadyExistsException("Food with this name already exists") from e

    async def delete_food(self, food_id: int, current_user: User) -> bool:
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(food_id)
        else:
            existing = await self.repository.get_by_id_and_user(
                food_id, current_user.id
            )
        if not existing:
            raise NotFoundException("Food not found")

        deleted = await self.repository.delete(food_id)
        if not deleted:
            raise NotFoundException("Food not found")
        return True
