from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Index, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class Reminder(DateTimeMixin, SQLModel, table=True):
    __tablename__ = "reminders"  # type: ignore[assignment]

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

    id: int | None = Field(default=None, primary_key=True, description="提醒事项ID")
    title: str = Field(..., max_length=100, description="提醒事项标题")
    type: str = Field(..., max_length=50, description="提醒事项类型")
    due_date: datetime = Field(..., description="到期时间")
    is_done: bool = Field(default=False, nullable=False, description="是否完成")
    description: str | None = Field(
        default=None, max_length=500, description="提醒事项描述"
    )
    profile_id: int = Field(
        foreign_key="profiles.id", nullable=False, index=True, description="宠物ID"
    )

    # 关系属性（非列）
    profile: Optional["Profile"] = Relationship(back_populates="reminders")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Reminder(id={self.id}, title={self.title})>"
