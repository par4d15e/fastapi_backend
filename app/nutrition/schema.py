from pydantic import BaseModel, Field


class NutritionFoodItem(BaseModel):
    """单个候选食品"""

    food_id: int = Field(..., description="食品ID")
    ratio: float = Field(1.0, gt=0, description="配比权重")
    fixed_grams: float | None = Field(
        None, ge=0, description="固定克数（可选，优先满足）"
    )
    kcals_per_g_override: float | None = Field(
        None, gt=0, description="覆盖的卡路里密度(kcal/g)"
    )


class NutritionPlanCreate(BaseModel):
    """营养计划计算请求"""

    profile_id: int = Field(..., description="宠物ID")
    foods: list[NutritionFoodItem] = Field(..., min_length=1, description="候选食品")
    daily_kcals: float | None = Field(
        None, gt=0, description="每日目标热量(kcal)，为空时自动估算"
    )
    weight_g_override: int | None = Field(None, gt=0, description="覆盖体重(克)")
    age_months_override: int | None = Field(
        None, ge=0, description="覆盖月龄（优先使用）"
    )
    neutered_override: bool | None = Field(None, description="覆盖绝育状态（优先使用）")
    activity_level_override: str | None = Field(
        None, description="覆盖活动水平: low/medium/high（优先使用）"
    )
    is_obese_override: bool | None = Field(None, description="覆盖肥胖状态（优先使用）")
    is_pregnant: bool = Field(False, description="是否妊娠（临时状态）")
    is_lactating: bool = Field(False, description="是否哺乳（临时状态）")
    is_senior_override: bool | None = Field(
        None, description="覆盖老年犬状态（优先使用）"
    )
    activity_factor_override: float | None = Field(
        None, ge=0.8, le=8.0, description="手动覆盖活动系数（最高优先级）"
    )


class NutritionFoodPlan(BaseModel):
    food_id: int
    food_name: str
    kcals_per_g: float
    grams: float
    kcals: float


class NutritionPlanResponse(BaseModel):
    profile_id: int
    weight_g: int
    daily_kcals_target: float
    total_grams: float
    total_kcals: float
    foods: list[NutritionFoodPlan]
    notes: list[str]


class NutritionDailyKcalsResponse(BaseModel):
    profile_id: int
    daily_kcals_target: float
