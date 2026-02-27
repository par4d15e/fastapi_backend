"""令牌与验证码模型定义 - SQLModel 版"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.users.model import User


class RefreshToken(SQLModel, table=True, mixins=[DateTimeMixin]):
    """刷新令牌模型

    用于管理用户刷新令牌，支持：
    - 多设备登录（每个设备一个令牌）
    - 令牌撤销
    - 令牌过期管理
    """

    __tablename__ = "refresh_tokens"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True, index=True)

    # 用户id（外键关联用户表）
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    # 令牌信息
    token: str = Field(max_length=500, unique=True, index=True, nullable=False)
    expires_at: datetime = Field(index=True, nullable=False)

    # 设备信息（可选）
    device_name: str | None = Field(default=None, max_length=100, nullable=True)
    device_type: str | None = Field(
        default=None, max_length=50, nullable=True
    )  # web, mobile, desktop
    ip_address: str | None = Field(default=None, max_length=45, nullable=True)
    user_agent: str | None = Field(default=None, max_length=500, nullable=True)

    # 状态
    is_revoked: bool = Field(default=False, nullable=False, index=True)
    revoked_at: datetime | None = Field(default=None, nullable=True)

    # 最近使用时间
    last_used_at: datetime | None = Field(default=None, nullable=True)

    # 关联关系
    user: "User" = Relationship(back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"

    def is_valid(self) -> bool:
        """检查令牌是否有效"""
        if self.is_revoked:
            return False
        return datetime.now(timezone.utc) < self.expires_at

    def revoke(self) -> None:
        """撤销令牌"""
        self.is_revoked = True
        self.revoked_at = datetime.now(timezone.utc)


class VerificationCode(SQLModel, table=True, mixins=[DateTimeMixin]):
    """验证码模型

    用于管理邮件验证码和密码重置码，支持：
    - 验证码过期管理
    - 验证码使用次数限制
    - 验证码类型区分
    """

    __tablename__ = "verification_codes"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True, index=True)

    # 用户id（外键关联用户表）
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    # 验证码信息
    code: str = Field(max_length=10, nullable=False, index=True)
    code_type: str = Field(max_length=20, nullable=False, index=True)
    expires_at: datetime = Field(DateTime(timezone=True), nullable=False, index=True)

    # 使用状态
    is_used: bool = Field(default=False, nullable=False, index=True)
    used_at: datetime | None = Field(default=None, nullable=True)
    attempts: int = Field(default=0, nullable=False)
    max_attempts: int = Field(default=5, nullable=False)

    # 关联关系
    user: "User" = Relationship(back_populates="verification_codes")

    def __repr__(self) -> str:
        return f"<VerificationCode(id={self.id}, user_id={self.user_id}, code_type={self.code_type})>"

    def is_valid(self) -> bool:
        """检查验证码是否有效"""
        if self.is_used:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return datetime.now(timezone.utc) < self.expires_at

    def increment_attempts(self) -> None:
        """增加尝试次数"""
        self.attempts += 1

    def mark_as_used(self) -> None:
        """标记为已使用"""
        self.is_used = True
        self.used_at = datetime.now(timezone.utc)
