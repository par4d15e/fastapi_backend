from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Index, String, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.auth.model import User
    from app.families.model import Family
    from app.reminders.model import Reminder
    from app.weights.model import WeightRecord


class Profile(DateTimeMixin, Base):
    __tablename__ = "profiles"

    __table_args__ = (
        # 复合索引
        Index("idx_profiles_variety_gender", "variety", "gender"),  # 按品种+性别筛选
        Index(
            "idx_profiles_variety_birthday", "variety", "birthday"
        ),  # 按品种+生日筛选
        Index("idx_profiles_gender_name", "gender", "name"),  # 按性别+姓名筛选
        # 排序索引
        Index("idx_profiles_created_at_desc", desc("created_at")),
        Index("idx_profiles_updated_at_desc", desc("updated_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="宠物ID")
    name: Mapped[str] = mapped_column(String(100), unique=True, comment="姓名")
    gender: Mapped[str] = mapped_column(String(20), comment="性别")
    variety: Mapped[str] = mapped_column(String(100), comment="品种")
    birthday: Mapped[date | None] = mapped_column(Date, comment="生日")
    meals_per_day: Mapped[int] = mapped_column(default=2, comment="每日餐数")
    is_neutered: Mapped[bool] = mapped_column(default=False, comment="是否绝育")
    is_obese: Mapped[bool] = mapped_column(default=False, comment="是否肥胖")
    activity_level: Mapped[str] = mapped_column(
        String(20), default="medium", comment="活动水平: 低/中/高"
    )
    description: Mapped[str | None] = mapped_column(String(255), comment="描述")

    # 外键
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), index=True, comment="所属用户ID"
    )
    family_id: Mapped[int | None] = mapped_column(
        ForeignKey("families.id"), index=True, comment="所属家庭ID"
    )

    # 关系
    user: Mapped[User | None] = relationship("User", back_populates="profiles")
    family: Mapped[Family | None] = relationship("Family", back_populates="profiles")
    reminders: Mapped[list[Reminder]] = relationship(
        "Reminder", back_populates="profile"
    )
    weight_records: Mapped[list[WeightRecord]] = relationship(
        "WeightRecord", back_populates="profile"
    )

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        """返回档案对象的调试字符串。"""
        return f"<Profile(id={self.id}, name={self.name})>"
