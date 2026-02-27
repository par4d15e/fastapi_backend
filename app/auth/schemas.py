from datetime import datetime
from typing import Annotated

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

# ========== 刷新令牌 相关 Schema ==========


class RefreshTokenCreate(SQLModel):
    """刷新令牌创建 Schema"""

    device_name: Annotated[str | None, Field(None, max_length=200)]
    device_type: Annotated[str | None, Field(None, max_length=50)]
    user_id: Annotated[int, Field(...)]
    token: Annotated[str, Field(...)]
    expires_at: Annotated[datetime, Field(...)]
    ip_address: Annotated[str | None, Field(None)]
    user_agent: Annotated[str | None, Field(None, max_length=500)]


class RefreshTokenResponse(SQLModel):
    """刷新令牌响应 Schema"""

    device_name: Annotated[str | None, Field(None, max_length=200)]
    device_type: Annotated[str | None, Field(None, max_length=50)]
    id: int
    user_id: int
    expires_at: datetime
    is_revoked: bool
    created_at: datetime
    last_used_at: datetime | None = None
    ip_address: str | None = None


class RefreshTokenRequest(SQLModel):
    """刷新令牌请求 Schema"""

    refresh_token: Annotated[
        str, Field(..., description="Generate token schemas (app/schemas/token.py)")
    ]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
        }
    )  # type: ignore[assignment]


class RefreshTokenRevoke(SQLModel):
    """撤销刷新令牌 Schema"""

    token: Annotated[
        str | None,
        Field(None, description="生成令牌相关 schema"),
    ]


# ========== 验证码 相关 Schema ==========


class VerificationCodeCreate(SQLModel):
    """验证码创建 Schema"""

    code_type: Annotated[str, Field(..., description="生成令牌相关 schema")]
    user_id: Annotated[int, Field(...)]
    code: Annotated[str, Field(...)]
    expires_at: Annotated[datetime, Field(...)]
    max_attempts: Annotated[int, Field(5)]


class VerificationCodeResponse(SQLModel):
    """验证码响应 Schema"""

    code_type: Annotated[str, Field(..., description="生成令牌相关 schema")]
    id: int
    user_id: int
    expires_at: datetime
    is_used: bool
    attempts: int
    max_attempts: int
    created_at: datetime


class VerificationCodeVerify(SQLModel):
    """验证码验证 Schema"""

    code: Annotated[str, Field(..., min_length=4, max_length=10)]
    code_type: Annotated[str, Field(..., description="生成令牌相关 schema")]

    model_config = ConfigDict(
        json_schema_extra={
            "example": [{"code": "123456", "code_type": "email_verification"}]
        }
    )  # type: ignore[assignment]
