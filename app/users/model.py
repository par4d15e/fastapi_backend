from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from app.core.base_model import DateTimeMixin

if TYPE_CHECKING:
    from app.auth.model import RefreshToken, VerificationCode


class User(SQLModel, table=True, mixins=[DateTimeMixin]):
    __tablename__ = "users"  # type: ignore[assignment]

    # 基础字段
    id: int | None = Field(None, primary_key=True, index=True)
    username: str = Field(..., max_length=50, unique=True, index=True)
    email: str = Field(..., max_length=100, unique=True, index=True)
    hashed_password: str = Field(..., max_length=255)
    bio: str | None = Field("这个人很懒，什么都没有留下。", max_length=300)
    city: str | None = Field(None, max_length=100)
    ip_address: str | None = Field(None, max_length=45)

    # 状态
    is_active: bool = Field(True, nullable=False)
    is_superuser: bool = Field(False, nullable=False)
    is_verified: bool = Field(
        False, nullable=False, description="Email whether already validated"
    )
    is_deleted: bool = Field(False, nullable=False)

    # 最后登录时间（保留 timezone）
    last_login_at: datetime | None = Field(
        None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    # 关系
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")
    verification_codes: list["VerificationCode"] = Relationship(back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
