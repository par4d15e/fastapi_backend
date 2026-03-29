from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.user_manager import current_active_user
from app.core.database import get_session
from app.foods.repository import FoodRepository
from app.nutrition.schema import (
    NutritionDailyKcalsResponse,
    NutritionPlanCreate,
    NutritionPlanResponse,
    NutritionPreferenceResponse,
    NutritionPreferenceUpsert,
)
from app.nutrition.repository import NutritionPreferenceRepository
from app.nutrition.service import NutritionPreferenceService, NutritionService
from app.profiles.repository import ProfileRepository
from app.weights.repository import WeightRecordRepository

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


async def get_nutrition_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NutritionService:
    """获取营养服务依赖。"""
    return NutritionService(
        food_repository=FoodRepository(session),
        profile_repository=ProfileRepository(session),
        weight_repository=WeightRecordRepository(session),
    )


async def get_nutrition_preference_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NutritionPreferenceService:
    """获取营养服务依赖。"""
    return NutritionPreferenceService(
        preference_repository=NutritionPreferenceRepository(session),
        profile_repository=ProfileRepository(session),
    )


@router.post("/plans", response_model=NutritionPlanResponse)
async def create_nutrition_plan(
    payload: NutritionPlanCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
):
    """创建营养。"""
    return await service.plan_daily_intake(payload, current_user)


@router.post("/daily-kcals", response_model=NutritionDailyKcalsResponse)
async def calculate_daily_kcals(
    payload: NutritionPlanCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
):
    """计算营养。"""
    return await service.calculate_daily_kcals(payload, current_user)


@router.get("/preferences/{profile_id}", response_model=NutritionPreferenceResponse)
async def get_nutrition_preference(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[NutritionPreferenceService, Depends(get_nutrition_preference_service)],
):
    """获取指定营养。"""
    return await service.get_preference(profile_id, current_user)


@router.put("/preferences/{profile_id}", response_model=NutritionPreferenceResponse)
async def upsert_nutrition_preference(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    payload: NutritionPreferenceUpsert,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[NutritionPreferenceService, Depends(get_nutrition_preference_service)],
):
    """处理营养相关接口。"""
    if payload.profile_id != profile_id:
        payload = NutritionPreferenceUpsert(
            profile_id=profile_id,
            selected_foods=payload.selected_foods,
            daily_kcals_target=payload.daily_kcals_target,
        )
    return await service.upsert_preference(payload, current_user)
