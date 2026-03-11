from datetime import date

from sqlmodel import Field, SQLModel


class ProfileCreate(SQLModel):
    """创建宠物档案"""

    name: str = Field(..., max_length=100, description="姓名")
    gender: str = Field(..., max_length=20, description="性别")
    variety: str = Field(..., max_length=100, description="品种")
    birthday: date | None = Field(None, description="生日")
    meals_per_day: int = Field(2, ge=1, description="每日餐数")
    is_neutered: bool = Field(False, description="是否绝育")
    activity_level: str = Field(
        "medium", max_length=20, description="活动水平: low/medium/high"
    )
    is_obese: bool = Field(False, description="是否肥胖")


class ProfileUpdate(SQLModel):
    """更新宠物档案（部分可选）"""

    name: str | None = Field(None, max_length=100, description="姓名")
    gender: str | None = Field(None, max_length=20, description="性别")
    variety: str | None = Field(None, max_length=100, description="品种")
    birthday: date | None = Field(None, description="生日")
    meals_per_day: int | None = Field(None, ge=1, description="每日餐数")
    is_neutered: bool | None = Field(None, description="是否绝育")
    activity_level: str | None = Field(
        None, max_length=20, description="活动水平: low/medium/high"
    )
    is_obese: bool | None = Field(None, description="是否肥胖")


class ProfileResponse(SQLModel):
    """宠物档案响应"""

    id: int
    name: str = Field(..., max_length=100, description="姓名")
    gender: str = Field(..., max_length=20, description="性别")
    variety: str = Field(..., max_length=100, description="品种")
    birthday: date | None = Field(None, description="生日")
    meals_per_day: int = Field(2, ge=1, description="每日餐数")
    is_neutered: bool = Field(False, description="是否绝育")
    activity_level: str = Field(
        "medium", max_length=20, description="活动水平: low/medium/high"
    )
    is_obese: bool = Field(False, description="是否肥胖")
