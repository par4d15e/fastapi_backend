from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class WeightRecordCreate(SQLModel):
    """创建体重记录"""

    profile_id: int = Field(..., description="宠物ID")
    weight_g: int = Field(..., gt=0, description="体重 (克)")
    measured_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), description="测量时间"
    )


class WeightRecordUpdate(SQLModel):
    """更新体重记录（部分可选）"""

    weight_g: int | None = Field(None, gt=0, description="体重 (克)")
    measured_at: datetime | None = Field(None, description="测量时间")


class WeightRecordResponse(SQLModel):
    """体重记录响应"""

    id: int
    profile_id: int = Field(..., description="宠物ID")
    weight_g: int = Field(..., description="体重 (克)")
    measured_at: datetime = Field(..., description="测量时间")
