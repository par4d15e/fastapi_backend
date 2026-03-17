from datetime import datetime, timezone

from pydantic import BaseModel, Field


class WeightRecordCreate(BaseModel):
    """创建体重记录"""

    profile_id: int = Field(..., description="宠物ID")
    weight_g: int = Field(..., gt=0, description="体重 (克)")
    measured_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), description="测量时间"
    )


class WeightRecordUpdate(BaseModel):
    """更新体重记录（部分可选）"""

    weight_g: int | None = Field(None, gt=0, description="体重 (克)")
    measured_at: datetime | None = Field(None, description="测量时间")


class WeightRecordResponse(BaseModel):
    """体重记录响应"""

    model_config = {"from_attributes": True}

    id: int
    profile_id: int = Field(..., description="宠物ID")
    weight_g: int = Field(..., description="体重 (克)")
    measured_at: datetime = Field(..., description="测量时间")
