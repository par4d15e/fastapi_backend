from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.auth.models import RefreshToken, VerificationCode


class User(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "users"  # type: ignore[assignment]

    # 基础字段
    id: int | None = Field(default=None, primary_key=True, index=True)
    username: str = Field(..., max_length=50, unique=True, index=True)
    email: str = Field(..., max_length=100, unique=True, index=True)
    hashed_password: str = Field(..., max_length=255)

    # 状态
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    is_verified: bool = Field(
        default=False, nullable=False, description="Email whether already validated"
    )

    # 最后登录时间（保留 timezone）
    last_login_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # 关系
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    verification_codes: list["VerificationCode"] = Relationship(back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
