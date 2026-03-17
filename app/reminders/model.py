from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class Reminder(DateTimeMixin, Base):
    __tablename__ = "reminders"

    __table_args__ = (
        # 全文模糊搜索索引（pg_trgm）
        Index(
            "idx_reminders_title_gin_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        # 核心查询索引
        Index("idx_reminders_type", "type"),
        Index("idx_reminders_due_date", "due_date"),
        Index("idx_reminders_is_done", "is_done"),
        # 复合业务索引
        Index(
            "idx_reminders_get_by_title", "profile_id", "is_done"
        ),  # 查询宠物未完成提醒
        Index(
            "idx_reminders_profile_due_date", "profile_id", "is_done", "due_date"
        ),  # 查询宠物即将到期提醒
        Index("idx_reminders_profile_type", "profile_id", "type"),  # 按宠物+类型筛选
        Index(
            "idx_reminders_profile_due_is_done", "profile_id", "due_date", "is_done"
        ),  # 核心查询：宠物未完成且未过期
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="提醒事项ID")
    title: Mapped[str] = mapped_column(pg.VARCHAR(100), comment="提醒事项标题")
    type: Mapped[str] = mapped_column(pg.VARCHAR(50), comment="提醒事项类型")
    due_date: Mapped[datetime] = mapped_column(
        pg.TIMESTAMP(timezone=True), comment="到期时间"
    )
    is_done: Mapped[bool] = mapped_column(default=False, comment="是否完成")
    description: Mapped[str | None] = mapped_column(
        pg.VARCHAR(500), comment="提醒事项描述"
    )
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profiles.id"), index=True, comment="宠物ID"
    )

    profile: Mapped[Profile | None] = relationship(
        "Profile", back_populates="reminders"
    )

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Reminder(id={self.id}, title={self.title})>"
