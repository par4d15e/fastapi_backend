from datetime import datetime
from typing import Annotated

from sqlmodel import Field, SQLModel


class ReminderCreate(SQLModel):
    """创建提醒"""

    title: Annotated[str, Field(..., max_length=200, description="提醒事项标题")]
    type: Annotated[str, Field(..., max_length=50, description="提醒事项类型")]
    due_date: Annotated[datetime, Field(..., description="到期时间")]
    is_done: Annotated[bool, Field(False, description="是否完成")]
    description: Annotated[str | None, Field(None, description="提醒事项描述")]
    profile_id: Annotated[int, Field(..., description="宠物ID")]


class ReminderUpdate(SQLModel):
    """更新提醒（部分可选）"""

    title: Annotated[
        str | None, Field(None, max_length=200, description="提醒事项标题")
    ]
    type: Annotated[str | None, Field(None, max_length=50, description="提醒事项类型")]
    due_date: Annotated[datetime | None, Field(None, description="到期时间")]
    is_done: Annotated[bool | None, Field(False, description="是否完成")]
    description: Annotated[str | None, Field(None, description="提醒事项描述")]
    profile_id: Annotated[int | None, Field(None, description="宠物ID")]


class ReminderResponse(SQLModel):
    """提醒响应"""

    title: Annotated[str, Field(..., max_length=200, description="提醒事项标题")]
    type: Annotated[str, Field(..., max_length=50, description="提醒事项类型")]
    due_date: Annotated[datetime, Field(..., description="到期时间")]
    is_done: Annotated[bool, Field(False, description="是否完成")]
    description: Annotated[str | None, Field(None, description="提醒事项描述")]
    profile_id: Annotated[int, Field(..., description="宠物ID")]
    id: int
