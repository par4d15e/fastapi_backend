from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Index, Relationship, SQLModel, desc

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class WeightRecord(DateTimeMixin, SQLModel, table=True):
    __tablename__ = "weight_records"  # type: ignore[assignment]
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

    id: int | None = Field(default=None, primary_key=True)  # type: ignore[assignment]
    profile_id: int = Field(foreign_key="profiles.id", nullable=False, index=True)
    weight_g: int = Field(..., description="体重 (克)")
    measured_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    profile: Optional["Profile"] = Relationship(back_populates="weight_records")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<WeightRecord(id={self.id}, profile_id={self.profile_id}, weight_g={self.weight_g})>"
