from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.nutrition.model import NutritionPreference


class NutritionPreferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        """初始化NutritionPreferenceRepository。"""
        self.session = session

    async def get_by_profile_id(
        self, profile_id: int
    ) -> NutritionPreference | None:
        """根据档案 ID 查询营养偏好。"""
        result = await self.session.execute(
            select(NutritionPreference).where(
                NutritionPreference.profile_id == profile_id
            )
        )
        return result.scalar_one_or_none()

    async def upsert_by_profile_id(
        self, profile_id: int, data: Mapping[str, Any]
    ) -> NutritionPreference:
        """按档案 ID 创建或更新营养偏好。"""
        preference = await self.get_by_profile_id(profile_id)
        if preference is None:
            preference = NutritionPreference(profile_id=profile_id, **data)
            self.session.add(preference)
        else:
            for key, value in data.items():
                setattr(preference, key, value)
        await self.session.commit()
        await self.session.refresh(preference)
        return preference
