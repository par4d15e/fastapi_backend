from datetime import datetime
from enum import IntEnum
from typing import Annotated

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import (
    Column,
    Field,
    Index,
    SQLModel,
    desc,
)

from app.core.base_model import DateTimeMixin


class CodeType(IntEnum):
    verified = 1
    reset = 2


class SocialProvider(IntEnum):
    google = 1
    github = 2


class RefreshToken(SQLModel, table=True, mixins=[DateTimeMixin]):
    """用户刷新令牌表 - 仅存储 refresh token"""

    __tablename__ = "refresh_tokens"  # type: ignore[assignment]

    __table_args__ = (
        # 单列索引
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_is_active", "is_active"),
        Index("idx_refresh_tokens_jti", "jti"),
        Index("idx_refresh_tokens_expired_at", "expired_at"),
        # 复合索引 - 用于高效查询
        Index(
            "idx_refresh_tokens_get_user_tokens", "user_id", "expired_at", "is_active"
        ),  # auth/repository.py: _get_user_tokens
        Index(
            "idx_refresh_tokens_revoke_user_tokens", "user_id", "is_active"
        ),  # auth/repository.py: _revoke_user_tokens
        Index(
            "idx_refresh_tokens_generate_access_token",
            "user_id",
            "jti",
            "is_active",
            "expired_at",
        ),  # auth/repository.py: generate_access_token
        # 排序索引
        Index("idx_refresh_tokens_created_at_desc", desc("created_at")),
    )

    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    user_id: Annotated[
        int,
        Field(foreign_key="users.id", ondelete="CASCADE", nullable=False),
    ]
    jti: Annotated[str, Field(nullable=False, max_length=64, unique=True)]
    token: Annotated[str, Field(nullable=False, max_length=1024)]
    is_active: Annotated[bool, Field(default=True, nullable=True)] = True
    expired_at: Annotated[
        datetime, Field(sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))
    ]

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"


class Code(SQLModel, table=True, mixins=[DateTimeMixin]):
    """验证码表 - 存储邮箱验证码和重置密码码"""

    __tablename__ = "codes"  # type: ignore[assignment]

    __table_args__ = (
        # 单列索引
        Index("idx_codes_user_id", "user_id"),
        Index("idx_codes_type", "type"),
        Index("idx_codes_is_used", "is_used"),
        # 复合索引
        Index(
            "idx_codes_get_valid_code", "user_id", "type", "expires_at", "is_used"
        ),  # auth/repository.py: _get_valid_code
        Index(
            "idx_codes_validate_code",
            "user_id",
            "code",
            "type",
            "expires_at",
            "is_used",
        ),  # auth/repository.py: _validate_code
        # 排序索引
        Index("idx_codes_created_at_desc", desc("created_at")),
        Index("idx_codes_expires_at_desc", desc("expires_at")),
    )

    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    user_id: Annotated[
        int,
        Field(foreign_key="users.id", ondelete="CASCADE", nullable=False),
    ]
    type: Annotated[CodeType, Field(nullable=False)]
    code: Annotated[str, Field(nullable=False, max_length=10, unique=True)]  # 优化长度
    is_used: Annotated[bool, Field(default=False, nullable=False)] = False
    expires_at: Annotated[
        datetime, Field(sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))
    ]

    def __repr__(self):
        return f"<Code(id={self.id}, user_id={self.user_id}, type={self.type.name}, is_used={self.is_used})>"


class Social_Account(SQLModel, table=True, mixins=[DateTimeMixin]):
    """社交账户表 - 存储用户的第三方登录账户信息"""

    __tablename__ = "social_accounts"  # type: ignore[assignment]

    __table_args__ = (
        # 复合索引
        Index(
            "idx_social_accounts_get_social_account",
            "user_id",
            "provider",
            "provider_user_id",
        ),  # auth/repository.py: get_social_account
    )

    id: Annotated[int | None, Field(default=None, primary_key=True)] = None
    user_id: Annotated[
        int,
        Field(foreign_key="users.id", ondelete="CASCADE", nullable=False, index=True),
    ]
    provider: Annotated[SocialProvider, Field(nullable=False)]
    provider_user_id: Annotated[str, Field(nullable=False, max_length=100, unique=True)]
    # 优化长度

    def __repr__(self):
        return f"<Social_Account(id={self.id}, user_id={self.user_id})>"
