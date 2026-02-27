from datetime import date
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.reminders.model import Reminder


class Profile(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "profiles"  # type: ignore[assignment]

    id: Annotated[
        int | None, Field(default=None, primary_key=True, description="宠物ID")
    ]
    name: Annotated[str, Field(..., max_length=100, unique=True, description="姓名")]
    gender: Annotated[str, Field(..., max_length=20, description="性别")]
    variety: Annotated[str, Field(..., max_length=100, description="品种")]
    birthday: Annotated[date | None, Field(default=None, description="生日")]
    meals_per_day: Annotated[int, Field(default=2, description="每日餐数")]
    description: Annotated[
        str | None, Field(default=None, max_length=255, description="描述")
    ]

    reminders: Annotated[list["Reminder"], Relationship(back_populates="profile")]

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Profile(id={self.id}, name={self.name}, gender={self.gender}, variety={self.variety})>"
