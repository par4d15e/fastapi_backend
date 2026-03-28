from dataclasses import dataclass

from app.auth.model import User
from app.core.exception import NotFoundException
from app.foods.repository import FoodRepository
from app.nutrition.schema import (
    NutritionDailyKcalsResponse,
    NutritionFoodItem,
    NutritionFoodPlan,
    NutritionPlanCreate,
    NutritionPlanResponse,
)
from app.profiles.repository import ProfileRepository
from app.weights.repository import WeightRecordRepository


@dataclass
class _ResolvedFood:
    food_id: int
    name: str
    ratio: float
    kcals_per_g: float
    fixed_grams: float


class NutritionService:
    """Nutrition 服务层：聚合 profile/weight/food 并计算喂食克数"""

    def _is_superuser(self, user: User) -> bool:
        return bool(getattr(user, "is_superuser", False))

    def __init__(
        self,
        food_repository: FoodRepository,
        profile_repository: ProfileRepository,
        weight_repository: WeightRecordRepository,
    ) -> None:
        self.food_repository = food_repository
        self.profile_repository = profile_repository
        self.weight_repository = weight_repository

    async def plan_daily_intake(
        self,
        payload: NutritionPlanCreate,
        current_user: User,
    ) -> NutritionPlanResponse:
        if self._is_superuser(current_user):
            profile = await self.profile_repository.get_by_id(payload.profile_id)
        else:
            profile = await self.profile_repository.get_by_id_and_user(
                payload.profile_id, current_user.id
            )
        if not profile:
            raise NotFoundException("Profile not found")

        weight_kg = await self._resolve_weight_kg(payload, current_user)
        resolved_foods = await self._resolve_foods(payload.foods, current_user)

        # 自动判断或使用覆盖的活动系数
        activity_factor = self._determine_activity_factor(
            payload=payload,
            profile=profile,
        )

        daily_kcals_target = (
            payload.daily_kcals
            if payload.daily_kcals is not None
            else self._estimate_daily_kcals(
                weight_kg=weight_kg,
                activity_factor=activity_factor,
            )
        )

        plans, notes = self._allocate_foods(
            target_kcals=daily_kcals_target,
            foods=resolved_foods,
        )

        total_grams = round(sum(item.grams for item in plans), 2)
        total_kcals = round(sum(item.kcals for item in plans), 2)

        return NutritionPlanResponse(
            profile_id=payload.profile_id,
            weight_kg=weight_kg,
            daily_kcals_target=round(daily_kcals_target, 2),
            total_grams=total_grams,
            total_kcals=total_kcals,
            foods=plans,
            notes=notes,
        )

    async def calculate_daily_kcals(
        self,
        payload: NutritionPlanCreate,
        current_user: User,
    ) -> NutritionDailyKcalsResponse:
        if self._is_superuser(current_user):
            profile = await self.profile_repository.get_by_id(payload.profile_id)
        else:
            profile = await self.profile_repository.get_by_id_and_user(
                payload.profile_id, current_user.id
            )
        if not profile:
            raise NotFoundException("Profile not found")

        weight_kg = await self._resolve_weight_kg(payload, current_user)

        # 目标热量可由前端直接指定，优先级最高
        if payload.daily_kcals is not None:
            return NutritionDailyKcalsResponse(
                profile_id=payload.profile_id,
                daily_kcals_target=round(payload.daily_kcals, 2),
            )

        activity_factor = self._determine_activity_factor(
            payload=payload,
            profile=profile,
        )

        estimated = self._estimate_daily_kcals(
            weight_kg=weight_kg,
            activity_factor=activity_factor,
        )

        return NutritionDailyKcalsResponse(
            profile_id=payload.profile_id,
            daily_kcals_target=round(estimated, 2),
        )

    async def _resolve_weight_kg(
        self, payload: NutritionPlanCreate, current_user: User
    ) -> float:
        if payload.weight_kg_override is not None:
            return payload.weight_kg_override

        if self._is_superuser(current_user):
            latest = await self.weight_repository.get_by_profile_id(
                payload.profile_id,
                order_by="measured_at",
                direction="desc",
                limit=1,
                offset=0,
            )
        else:
            latest = await self.weight_repository.get_by_profile_id_and_user(
                payload.profile_id,
                current_user.id,
                order_by="measured_at",
                direction="desc",
                limit=1,
                offset=0,
            )

        if not latest:
            raise NotFoundException("Weight record not found for profile")

        return latest[0].weight_kg

    async def _resolve_foods(
        self, foods: list[NutritionFoodItem], current_user: User
    ) -> list[_ResolvedFood]:
        resolved: list[_ResolvedFood] = []
        for item in foods:
            if self._is_superuser(current_user):
                food = await self.food_repository.get_by_id(item.food_id)
            else:
                food = await self.food_repository.get_by_id_and_user(
                    item.food_id, current_user.id
                )
            if not food:
                raise NotFoundException(f"Food not found: {item.food_id}")
            if food.id is None:
                raise NotFoundException(f"Food id invalid: {item.food_id}")

            kcals_per_g = (
                item.kcals_per_g_override
                if item.kcals_per_g_override is not None
                else food.metabolic_energy
            )
            if kcals_per_g is None or kcals_per_g <= 0:
                raise NotFoundException(f"Food kcals_per_g missing: {item.food_id}")

            resolved.append(
                _ResolvedFood(
                    food_id=food.id,
                    name=food.name,
                    ratio=item.ratio,
                    kcals_per_g=kcals_per_g,
                    fixed_grams=item.fixed_grams or 0.0,
                )
            )

        return resolved

    def _determine_activity_factor(
        self,
        *,
        payload: NutritionPlanCreate,
        profile,
    ) -> float:
        """根据宠物状态自动判断生活系数（活动系数）"""
        # 优先使用手动覆盖值
        if payload.activity_factor_override is not None:
            return payload.activity_factor_override

        # 哺乳期母犬: 3.0-8.0，取中值 5.5
        if payload.is_lactating:
            return 5.5

        # 妊娠母犬: 2.0-3.0，取中值 2.5
        if payload.is_pregnant:
            return 2.5

        # 肥胖犬: 1.0 （优先使用请求覆盖，其次使用 profile 字段）
        is_obese = (
            payload.is_obese_override
            if payload.is_obese_override is not None
            else profile.is_obese
        )
        if is_obese:
            return 1.0

        # 计算实际月龄 （优先使用请求覆盖，其次从生日计算）
        age_months = payload.age_months_override
        if age_months is None and profile.birthday is not None:
            from datetime import date

            today = date.today()
            age_months = (today.year - profile.birthday.year) * 12 + (
                today.month - profile.birthday.month
            )

        # 幼犬判断
        if age_months is not None:
            if age_months < 4:
                return 3.0  # 幼犬（小于4个月）
            if age_months < 12:
                return 2.0  # 幼犬（4个月以上）

        # 老年犬: 1.2
        is_senior = (
            payload.is_senior_override
            if payload.is_senior_override is not None
            else False  # Profile 暂时没有 is_senior 字段
        )
        if is_senior:
            return 1.2

        # 成年犬根据绝育状态和活动水平
        neutered = (
            payload.neutered_override
            if payload.neutered_override is not None
            else profile.is_neutered
        )
        if neutered:
            # 成年绝育犬: 1.2-1.4，取中值 1.3
            return 1.3

        # 未绝育成年犬，根据活动水平
        activity_level = (
            payload.activity_level_override
            if payload.activity_level_override is not None
            else profile.activity_level
        )
        activity_level = (activity_level or "medium").lower()
        if activity_level == "low":
            return 1.4  # 未绝育成年犬（低活动量）
        if activity_level == "high":
            return 2.0  # 未绝育成年犬（高活动量）或小型犬/高能量犬

        # 默认：未绝育成年犬（中等活动量）: 1.4-1.6，取中值 1.5
        return 1.5

    def _estimate_daily_kcals(
        self,
        *,
        weight_kg: float,
        activity_factor: float,
    ) -> float:
        """按约定公式估算每日所需热量: 70 * 体重(kg)^0.75 * 活动系数。"""
        return 70 * (weight_kg**0.75) * activity_factor

    def _allocate_foods(
        self,
        *,
        target_kcals: float,
        foods: list[_ResolvedFood],
    ) -> tuple[list[NutritionFoodPlan], list[str]]:
        notes: list[str] = []
        fixed_kcals = sum(item.fixed_grams * item.kcals_per_g for item in foods)
        remaining_kcals = max(target_kcals - fixed_kcals, 0)

        ratio_sum = sum(item.ratio for item in foods if item.fixed_grams <= 0)
        if ratio_sum <= 0:
            ratio_sum = float(len(foods))
            notes.append("ratio fallback to equal split")

        plans: list[NutritionFoodPlan] = []
        for item in foods:
            alloc_kcals = 0.0
            if item.fixed_grams <= 0:
                alloc_kcals = remaining_kcals * (item.ratio / ratio_sum)

            total_kcals = (item.fixed_grams * item.kcals_per_g) + alloc_kcals
            grams = total_kcals / item.kcals_per_g if item.kcals_per_g > 0 else 0.0

            plans.append(
                NutritionFoodPlan(
                    food_id=item.food_id,
                    food_name=item.name,
                    kcals_per_g=item.kcals_per_g,
                    grams=round(grams, 2),
                    kcals=round(total_kcals, 2),
                )
            )

        return plans, notes
