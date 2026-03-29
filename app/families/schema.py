from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class FamilyCreate(BaseModel):
    """创建家庭"""

    name: str = Field(..., max_length=100, description="家庭名称")
    description: str | None = Field(None, max_length=255, description="家庭描述")


class FamilyUpdate(BaseModel):
    """更新家庭"""

    name: str | None = Field(None, max_length=100, description="家庭名称")
    description: str | None = Field(None, max_length=255, description="家庭描述")


class FamilyResponse(BaseModel):
    """家庭响应"""

    model_config = {"from_attributes": True}

    id: int
    name: str = Field(..., max_length=100, description="家庭名称")
    owner_id: UUID = Field(..., description="家庭创建者ID")
    description: str | None = Field(None, max_length=255, description="家庭描述")


class FamilyMemberCreate(BaseModel):
    """添加家庭成员"""

    user_id: UUID = Field(..., description="用户ID")
    role: str = Field("member", max_length=20, description="成员角色")


class FamilyMemberResponse(BaseModel):
    """家庭成员响应"""

    model_config = {"from_attributes": True}

    id: int
    family_id: int
    user_id: UUID
    role: str = Field(..., max_length=20, description="成员角色")


class FamilyInviteCreate(BaseModel):
    """创建家庭邀请"""

    expires_in_hours: int | None = Field(
        72, ge=1, le=720, description="邀请有效小时数"
    )


class FamilyInviteAccept(BaseModel):
    """接受家庭邀请"""

    token: str = Field(..., min_length=16, max_length=64, description="邀请令牌")


class FamilyInviteResponse(BaseModel):
    """家庭邀请响应"""

    model_config = {"from_attributes": True}

    id: int
    family_id: int
    inviter_id: UUID
    token: str = Field(..., max_length=64, description="邀请令牌")
    accepted_user_id: UUID | None = Field(None, description="接受邀请的用户ID")
    accepted_at: datetime | None = Field(None, description="接受时间")
    expires_at: datetime | None = Field(None, description="过期时间")
