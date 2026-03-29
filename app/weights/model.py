from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class WeightRecord(DateTimeMixin, Base):
    __tablename__ = "weight_records"
    __table_args__ = (
        # 复合索引
        Index(
            "idx_weight_records_get_by_profile_id",
            "profile_id",
            "measured_at",
        ),  # weights/repository.py: get_weight_records_by_profile_id
        # 排序索引
        Index("idx_weight_records_measured_at_desc", desc("measured_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    weight_kg: Mapped[float] = mapped_column(comment="体重 (kg)")
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        comment="测量时间",
    )

    # 外键及关系
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"), index=True, comment="宠物ID"
    )
    profile: Mapped[Profile | None] = relationship(
        "Profile", back_populates="weight_records"
    )

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        """返回体重记录对象的调试字符串。"""
        return f"<WeightRecord(id={self.id}, profile_id={self.profile_id}, weight_kg={self.weight_kg})>"
