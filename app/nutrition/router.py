from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.foods.repository import FoodRepository
from app.nutrition.schema import (
    NutritionDailyKcalsResponse,
    NutritionPlanCreate,
    NutritionPlanResponse,
)
from app.nutrition.service import NutritionService
from app.profiles.repository import ProfileRepository
from app.weights.repository import WeightRecordRepository

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


async def get_nutrition_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NutritionService:
    return NutritionService(
        food_repository=FoodRepository(session),
        profile_repository=ProfileRepository(session),
        weight_repository=WeightRecordRepository(session),
    )


@router.post("/plans", response_model=NutritionPlanResponse)
async def create_nutrition_plan(
    payload: NutritionPlanCreate,
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
):
    """根据宠物信息和食品组合计算每日喂食方案"""
    return await service.plan_daily_intake(payload)


@router.post("/daily-kcals", response_model=NutritionDailyKcalsResponse)
async def calculate_daily_kcals(
    payload: NutritionPlanCreate,
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
):
    """只计算并返回每日目标热量（不包含分配方案）。"""
    return await service.calculate_daily_kcals(payload)
