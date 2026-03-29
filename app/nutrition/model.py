from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class NutritionPreference(DateTimeMixin, Base):
    __tablename__ = "nutrition_preferences"
    __table_args__ = (
        UniqueConstraint("profile_id", name="uk_nutrition_preferences_profile_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="营养偏好ID")
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"), index=True, comment="宠物ID"
    )
    selected_foods: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False, comment="最近一次选择的食品配置"
    )
    daily_kcals_target: Mapped[float | None] = mapped_column(
        nullable=True, comment="最近一次目标热量"
    )

    profile: Mapped[Profile | None] = relationship("Profile")
