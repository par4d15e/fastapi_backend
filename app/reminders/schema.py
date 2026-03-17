from datetime import datetime

from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    """创建提醒"""

    title: str = Field(..., max_length=100, description="提醒事项标题")
    type: str = Field(..., max_length=50, description="提醒事项类型")
    due_date: datetime = Field(..., description="到期时间")
    is_done: bool = Field(False, description="是否完成")
    description: str | None = Field(None, description="提醒事项描述")
    profile_id: int = Field(..., description="宠物ID")


class ReminderUpdate(BaseModel):
    """更新提醒（部分可选）"""

    title: str | None = Field(None, max_length=100, description="提醒事项标题")
    type: str | None = Field(None, max_length=50, description="提醒事项类型")
    due_date: datetime | None = Field(None, description="到期时间")
    is_done: bool | None = Field(None, description="是否完成")
    description: str | None = Field(None, description="提醒事项描述")
    profile_id: int | None = Field(None, description="宠物ID")


class ReminderResponse(BaseModel):
    """提醒响应"""

    model_config = {"from_attributes": True}

    id: int
    title: str = Field(..., max_length=100, description="提醒事项标题")
    type: str = Field(..., max_length=50, description="提醒事项类型")
    due_date: datetime = Field(..., description="到期时间")
    is_done: bool = Field(False, description="是否完成")
    description: str | None = Field(None, description="提醒事项描述")
    profile_id: int = Field(..., description="宠物ID")
