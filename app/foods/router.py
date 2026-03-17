from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exception import NotFoundException
from app.foods.repository import FoodRepository
from app.foods.schema import FoodCreate, FoodResponse, FoodUpdate
from app.foods.service import FoodService

router = APIRouter(prefix="/foods", tags=["foods"])


# 依赖注入：为路由请求提供 FoodService
async def get_food_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FoodService:
    repository = FoodRepository(session)
    return FoodService(repository)


@router.post("/", response_model=FoodResponse, status_code=201)
async def create_food(
    food_data: FoodCreate,
    service: Annotated[FoodService, Depends(get_food_service)],
):
    new_food = await service.create_food(food_data)
    return new_food


@router.get("/", response_model=list[FoodResponse])
async def list_foods(
    service: Annotated[FoodService, Depends(get_food_service)],
    search: Annotated[str | None, Query(description="搜索关键词")] = None,
    order_by: Annotated[str, Query(description="排序字段")] = "id",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "asc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.list_foods(
        search=search,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/{food_name}", response_model=FoodResponse)
async def read_food(
    food_name: Annotated[str, Path(..., description="食物名称")],
    service: Annotated[FoodService, Depends(get_food_service)],
):
    food = await service.get_food_by_name(food_name)
    if not food:
        raise NotFoundException("Food not found")
    return food


@router.patch("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: Annotated[int, Path(..., description="食物ID")],
    food: FoodUpdate,
    service: Annotated[FoodService, Depends(get_food_service)],
):
    return await service.update_food(food_id, food)


@router.delete("/{food_id}", status_code=204)
async def delete_food(
    food_id: Annotated[int, Path(..., description="食物ID")],
    service: Annotated[FoodService, Depends(get_food_service)],
):
    await service.delete_food(food_id)
    return None
