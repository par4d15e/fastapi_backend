import uuid
from datetime import datetime

from pydantic import ConfigDict, EmailStr, model_validator
from sqlmodel import Field, SQLModel

from app.users.model import RoleType


class UserBase(SQLModel):
    """基类"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户创建"""

    password: str = Field(..., min_length=6, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "strongpassword123",
            }
        }
    )  # type: ignore[assignment]


class UserUpdate(UserBase):
    """用户更新"""

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    """用户响应"""

    uid: uuid.UUID
    role: RoleType
    is_active: bool
    is_verified: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)  # type: ignore[assignment]


# 认证相关 Schema
class UserLogin(SQLModel):
    """用户登录"""

    username: str | None = Field(None, description="用户名")
    email: EmailStr | None = Field(None, description="邮箱地址")
    password: str = Field(..., min_length=6)

    @model_validator(mode="after")
    def check_username_or_email(self):
        """Validate that at least username or email is provided"""
        if not self.username and not self.email:
            raise ValueError("Must provide username or email")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "strongpassword123"}
        }
    )  # type: ignore[assignment]


class Token(SQLModel):
    """令牌响应"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )  # type: ignore[assignment]


class TokenData(SQLModel):
    """令牌数据"""

    username: str | None = None
    user_id: int | None = None


class RefreshTokenRequest(SQLModel):
    """刷新令牌请求"""

    refresh_token: str = Field(
        ..., description="Generate user schemas (app/schemas/user.py)"
    )


# Email相关 Schema
class EmailVerificationRequest(SQLModel):
    """Email验证请求"""

    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "john@example.com", "code": "123456"}}
    )  # type: ignore[assignment]


class ResendVerificationRequest(SQLModel):
    """重新发送验证代码请求"""

    email: EmailStr


# 密码相关 Schema
class PasswordResetRequest(SQLModel):
    """密码重置请求"""

    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "john@example.com"}}
    )  # type: ignore[assignment]


class PasswordResetConfirm(SQLModel):
    """密码重置确认"""

    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "code": "123456",
                "new_password": "newstrongpassword123",
            }
        }
    )  # type: ignore[assignment]


class PasswordChange(SQLModel):
    """密码修改"""

    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newstrongpassword123",
            }
        }
    )  # type: ignore[assignment]
