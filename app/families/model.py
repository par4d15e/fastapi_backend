from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import Base, DateTimeMixin

if TYPE_CHECKING:
    from app.auth.model import User
    from app.foods.model import Food
    from app.profiles.model import Profile


class Family(DateTimeMixin, Base):
    __tablename__ = "families"

    __table_args__ = (
        Index("idx_families_created_at_desc", desc("created_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="家庭ID")
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="家庭名称"
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), index=True, comment="家庭创建者ID"
    )
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="家庭描述"
    )

    owner: Mapped[User | None] = relationship("User", back_populates="owned_families")
    members: Mapped[list[FamilyMember]] = relationship(
        "FamilyMember",
        back_populates="family",
        cascade="all, delete-orphan",
    )
    foods: Mapped[list[Food]] = relationship("Food", back_populates="family")
    profiles: Mapped[list[Profile]] = relationship("Profile", back_populates="family")


class FamilyMember(DateTimeMixin, Base):
    __tablename__ = "family_members"

    __table_args__ = (
        UniqueConstraint(
            "family_id",
            "user_id",
            name="uk_family_members_family_id_user_id",
        ),
        Index("idx_family_members_created_at_desc", desc("created_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="家庭成员ID")
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id"), index=True, comment="家庭ID"
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), index=True, comment="用户ID"
    )
    role: Mapped[str] = mapped_column(
        String(20), default="member", comment="成员角色"
    )

    family: Mapped[Family | None] = relationship("Family", back_populates="members")
    user: Mapped[User | None] = relationship(
        "User", back_populates="family_memberships"
    )


class FamilyInvite(DateTimeMixin, Base):
    __tablename__ = "family_invites"

    __table_args__ = (
        UniqueConstraint("token", name="uk_family_invites_token"),
        Index("idx_family_invites_family_id", "family_id"),
        Index("idx_family_invites_created_at_desc", desc("created_at")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, comment="家庭邀请ID")
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id"), index=True, comment="家庭ID"
    )
    inviter_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), index=True, comment="邀请人ID"
    )
    token: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, comment="邀请令牌"
    )
    accepted_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True, comment="接受邀请的用户ID"
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="接受时间"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="过期时间"
    )

    family: Mapped[Family | None] = relationship("Family")
    inviter: Mapped[User | None] = relationship("User", foreign_keys=[inviter_id])
    accepted_user: Mapped[User | None] = relationship(
        "User", foreign_keys=[accepted_user_id]
    )
