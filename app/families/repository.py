from __future__ import annotations

from typing import Any, Mapping
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.families.model import Family, FamilyInvite, FamilyMember


class FamilyRepository:
    def __init__(self, session: AsyncSession) -> None:
        """初始化FamilyRepository。"""
        self.session = session

    async def get_by_id(self, family_id: int) -> Family | None:
        """根据 ID 查询家庭。"""
        return await self.session.get(Family, family_id)

    async def get_all(self) -> list[Family]:
        """查询全部家庭。"""
        result = await self.session.execute(select(Family))
        return list(result.scalars().all())

    async def get_all_by_user(self, user_id: UUID) -> list[Family]:
        """查询当前用户可访问的家庭列表。"""
        result = await self.session.execute(
            select(Family)
            .join(FamilyMember)
            .where(FamilyMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, data: Mapping[str, Any]) -> Family:
        """创建家庭。"""
        family = Family(**data)
        self.session.add(family)
        await self.session.commit()
        await self.session.refresh(family)
        return family

    async def update(self, family_id: int, data: Mapping[str, Any]) -> Family | None:
        """更新家庭。"""
        family = await self.get_by_id(family_id)
        if not family:
            return None
        for key, value in data.items():
            setattr(family, key, value)
        await self.session.commit()
        await self.session.refresh(family)
        return family

    async def delete(self, family_id: int) -> bool:
        """删除家庭。"""
        family = await self.get_by_id(family_id)
        if not family:
            return False
        await self.session.delete(family)
        await self.session.commit()
        return True

    async def is_user_member(self, family_id: int, user_id: UUID) -> bool:
        """判断用户是否为家庭成员。"""
        result = await self.session.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == family_id, FamilyMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

    async def add_member(
        self, *, family_id: int, user_id: UUID, role: str = "member"
    ) -> FamilyMember:
        """向家庭中添加成员。"""
        member = FamilyMember(family_id=family_id, user_id=user_id, role=role)
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def remove_member(self, family_id: int, user_id: UUID) -> bool:
        """从家庭中移除成员。"""
        result = await self.session.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == family_id, FamilyMember.user_id == user_id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return False
        await self.session.delete(member)
        await self.session.commit()
        return True

    async def create_invite(self, data: Mapping[str, Any]) -> FamilyInvite:
        """创建家庭邀请。"""
        invite = FamilyInvite(**data)
        self.session.add(invite)
        await self.session.commit()
        await self.session.refresh(invite)
        return invite

    async def get_invite_by_token(self, token: str) -> FamilyInvite | None:
        """根据邀请令牌查询邀请。"""
        result = await self.session.execute(
            select(FamilyInvite).where(FamilyInvite.token == token)
        )
        return result.scalar_one_or_none()

    async def accept_invite(
        self, token: str, accepted_user_id: UUID
    ) -> FamilyInvite | None:
        """标记邀请已被接受。"""
        invite = await self.get_invite_by_token(token)
        if not invite or invite.accepted_at is not None:
            return None
        invite.accepted_user_id = accepted_user_id
        invite.accepted_at = datetime.now(tz=timezone.utc)
        await self.session.commit()
        await self.session.refresh(invite)
        return invite
