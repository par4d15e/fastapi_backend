from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from app.auth.model import User
from app.core.exception import AlreadyExistsException, ForbiddenException, NotFoundException
from app.families.model import Family, FamilyMember
from app.families.repository import FamilyRepository
from app.families.schema import (
    FamilyInviteAccept,
    FamilyInviteCreate,
    FamilyInviteResponse,
    FamilyCreate,
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyResponse,
    FamilyUpdate,
)


class FamilyService:
    """家庭服务层"""

    def __init__(self, repository: FamilyRepository) -> None:
        """初始化FamilyService。"""
        self.repository = repository

    def _is_superuser(self, user: User) -> bool:
        """判断当前用户是否为超级管理员。"""
        return bool(getattr(user, "is_superuser", False))

    async def _get_owned_family(self, family_id: int, current_user: User) -> Family:
        """获取当前用户拥有的家庭。"""
        family = await self.repository.get_by_id(family_id)
        if not family:
            raise NotFoundException("Family not found")
        if not self._is_superuser(current_user) and family.owner_id != current_user.id:
            raise ForbiddenException("Family access forbidden")
        return family

    async def _get_accessible_family(self, family_id: int, current_user: User) -> Family:
        """获取当前用户可访问的家庭。"""
        family = await self.repository.get_by_id(family_id)
        if not family:
            raise NotFoundException("Family not found")
        if self._is_superuser(current_user):
            return family
        if family.owner_id == current_user.id:
            return family
        if not await self.repository.is_user_member(family_id, current_user.id):
            raise ForbiddenException("Family access forbidden")
        return family

    async def create_family(
        self, payload: FamilyCreate, current_user: User
    ) -> FamilyResponse:
        """创建家庭并将当前用户设为所有者。"""
        try:
            family = Family(
                name=payload.name,
                description=payload.description,
                owner_id=current_user.id,
            )
            self.repository.session.add(family)
            await self.repository.session.flush()
            self.repository.session.add(
                FamilyMember(
                    family_id=family.id,
                    user_id=current_user.id,
                    role="owner",
                )
            )
            await self.repository.session.commit()
            await self.repository.session.refresh(family)
            return FamilyResponse.model_validate(family)
        except IntegrityError as exc:
            await self.repository.session.rollback()
            raise AlreadyExistsException("Family with this name already exists") from exc

    async def list_families(self, current_user: User) -> list[FamilyResponse]:
        """列出当前用户可见的家庭。"""
        families = await self.repository.get_all_by_user(current_user.id)
        if self._is_superuser(current_user):
            families = await self.repository.get_all()
        return [FamilyResponse.model_validate(family) for family in families]

    async def get_family(self, family_id: int, current_user: User) -> FamilyResponse:
        """获取指定家庭详情。"""
        family = await self._get_accessible_family(family_id, current_user)
        return FamilyResponse.model_validate(family)

    async def update_family(
        self, family_id: int, payload: FamilyUpdate, current_user: User
    ) -> FamilyResponse:
        """更新指定家庭信息。"""
        await self._get_owned_family(family_id, current_user)
        try:
            updated = await self.repository.update(
                family_id, payload.model_dump(exclude_unset=True, exclude_none=True)
            )
            if not updated:
                raise NotFoundException("Family not found")
            return FamilyResponse.model_validate(updated)
        except IntegrityError as exc:
            raise AlreadyExistsException("Family with this name already exists") from exc

    async def delete_family(self, family_id: int, current_user: User) -> bool:
        """删除指定家庭。"""
        await self._get_owned_family(family_id, current_user)
        deleted = await self.repository.delete(family_id)
        if not deleted:
            raise NotFoundException("Family not found")
        return True

    async def add_member(
        self, family_id: int, payload: FamilyMemberCreate, current_user: User
    ) -> FamilyMemberResponse:
        """向家庭中添加成员。"""
        await self._get_owned_family(family_id, current_user)
        try:
            member = await self.repository.add_member(
                family_id=family_id,
                user_id=payload.user_id,
                role=payload.role,
            )
            return FamilyMemberResponse.model_validate(member)
        except IntegrityError as exc:
            raise AlreadyExistsException("Family member already exists") from exc

    async def remove_member(
        self, family_id: int, user_id: str, current_user: User
    ) -> bool:
        """从家庭中移除成员。"""
        await self._get_owned_family(family_id, current_user)
        deleted = await self.repository.remove_member(family_id, UUID(user_id))
        if not deleted:
            raise NotFoundException("Family member not found")
        return True

    async def create_invite(
        self, family_id: int, payload: FamilyInviteCreate, current_user: User
    ) -> FamilyInviteResponse:
        """为家庭生成邀请令牌。"""
        await self._get_owned_family(family_id, current_user)
        token = uuid4().hex
        expires_at = None
        if payload.expires_in_hours is not None:
            expires_at = datetime.now(tz=timezone.utc) + timedelta(
                hours=payload.expires_in_hours
            )
        invite = await self.repository.create_invite(
            {
                "family_id": family_id,
                "inviter_id": current_user.id,
                "token": token,
                "expires_at": expires_at,
            }
        )
        return FamilyInviteResponse.model_validate(invite)

    async def accept_invite(
        self, payload: FamilyInviteAccept, current_user: User
    ) -> FamilyMemberResponse:
        """接受家庭邀请并创建成员关系。"""
        invite = await self.repository.get_invite_by_token(payload.token)
        if not invite:
            raise NotFoundException("Family invite not found")
        if invite.expires_at and invite.expires_at <= datetime.now(tz=timezone.utc):
            raise ForbiddenException("Family invite expired")
        if invite.accepted_at is not None:
            raise AlreadyExistsException("Family invite already accepted")
        try:
            accepted = await self.repository.accept_invite(payload.token, current_user.id)
            if not accepted:
                raise NotFoundException("Family invite not found")
            member = await self.repository.add_member(
                family_id=accepted.family_id,
                user_id=current_user.id,
                role="member",
            )
            return FamilyMemberResponse.model_validate(member)
        except IntegrityError as exc:
            raise AlreadyExistsException("Family member already exists") from exc
