from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.profiles.model import Profile


class Reminder(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "reminders"  # type: ignore[assignment]

    id: Annotated[
        int | None,
        Field(default=None, primary_key=True, index=True, description="提醒事项ID"),
    ]
    title: Annotated[str, Field(..., max_length=100, description="提醒事项标题")]
    type: Annotated[str, Field(..., max_length=50, description="提醒事项类型")]
    due_date: Annotated[datetime, Field(..., max_length=20, description="到期时间")]
    is_done: Annotated[
        bool, Field(default=False, nullable=False, description="是否完成")
    ]
    description: Annotated[
        str | None, Field(default=None, max_length=500, description="提醒事项描述")
    ]
    profile_id: Annotated[
        int,
        Field(
            foreign_key="profiles.id", nullable=False, index=True, description="宠物ID"
        ),
    ]

    profile: Annotated["Profile", Relationship(back_populates="reminders")]

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Reminder(id={self.id}, title={self.title}, type={self.type}, due_date={self.due_date}, is_done={self.is_done})>"
