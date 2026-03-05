from datetime import date
from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Index, Relationship, SQLModel, desc

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.reminders.model import Reminder


class Profile(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "profiles"  # type: ignore[assignment]

    __table_args__ = (
        # 复合索引 - 用于高效查询
        Index("idx_profiles_variety_gender", "variety", "gender"),  # 按品种+性别筛选
        Index(
            "idx_profiles_variety_birthday", "variety", "birthday"
        ),  # 按品种+生日筛选（年龄分布）
        # 排序索引
        Index("idx_profiles_created_at_desc", desc("created_at")),
        Index("idx_profiles_updated_at_desc", desc("updated_at")),
    )

    id: Annotated[
        int | None, Field(default=None, primary_key=True, description="宠物ID")
    ] = None
    name: Annotated[str, Field(..., max_length=100, unique=True, description="姓名")]
    gender: Annotated[str, Field(..., max_length=20, description="性别")]
    variety: Annotated[str, Field(..., max_length=100, description="品种")]
    birthday: Annotated[date | None, Field(default=None, description="生日")] = None
    meals_per_day: Annotated[int, Field(default=2, description="每日餐数")] = 2
    description: Annotated[
        str | None, Field(default=None, max_length=255, description="描述")
    ] = None

    reminders: Annotated[list["Reminder"], Relationship(back_populates="profile")] = []

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<Profile(id={self.id}, name={self.name})>"
