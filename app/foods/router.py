from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel.ext.asyncio.session import AsyncSession

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
    food_data: Annotated[FoodCreate, Depends()],
    service: Annotated[FoodService, Depends(get_food_service)],
):
    new_food = await service.create_food(food_data)
    return new_food


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
