from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.auth.model import User
from app.core.exception import AlreadyExistsException, NotFoundException
from app.families.repository import FamilyRepository
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate, ProfileResponse, ProfileUpdate


class ProfileService:
    """Profile 服务层：封装业务逻辑并调用 repository"""

    def __init__(
        self, repository: ProfileRepository, family_repository: FamilyRepository
    ) -> None:
        """初始化ProfileService。"""
        self.repository = repository
        self.family_repository = family_repository

    # 判断用户是否是管理员
    def _is_superuser(self, user: User) -> bool:
        """判断当前用户是否为超级管理员。"""
        return bool(getattr(user, "is_superuser", False))

    async def get_profile_by_name(
        self,
        profile_name: str,
        current_user: User,
    ) -> ProfileResponse:
        """根据名称获取档案。"""
        if self._is_superuser(current_user):
            profile = await self.repository.get_by_name(profile_name)
        else:
            profile = await self.repository.get_by_name_and_user_or_family(
                profile_name, current_user.id
            )
        if not profile:
            raise NotFoundException("Profile not found")

        return ProfileResponse.model_validate(profile)

    async def get_profile_by_id(
        self,
        profile_id: int,
        current_user: User,
    ) -> ProfileResponse:
        """根据 ID 获取档案。"""
        if self._is_superuser(current_user):
            profile = await self.repository.get_by_id(profile_id)
        else:
            profile = await self.repository.get_by_id_and_user_or_family(
                profile_id, current_user.id
            )
        if not profile:
            raise NotFoundException("Profile not found")

        return ProfileResponse.model_validate(profile)

    async def list_profiles(
        self,
        current_user: User,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ProfileResponse]:
        """列出当前用户可见的档案。"""
        if self._is_superuser(current_user):
            profiles = await self.repository.get_all(
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            profiles = await self.repository.get_all_by_user_or_family(
                current_user.id,
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )

        return [ProfileResponse.model_validate(profile) for profile in profiles]

    async def create_profile(
        self,
        profile_data: ProfileCreate,
        current_user_id: UUID,
    ) -> ProfileResponse:
        """创建档案。"""
        data = profile_data.model_dump()
        data["user_id"] = current_user_id
        if data.get("family_id") is not None:
            if not await self.family_repository.is_user_member(
                data["family_id"], current_user_id
            ):
                raise NotFoundException("Family not found")
        try:
            profile = await self.repository.create(data)

            return ProfileResponse.model_validate(profile)
        except IntegrityError as e:
            raise AlreadyExistsException("Profile with this name already exists") from e

    async def update_profile(
        self,
        profile_id: int,
        profile_data: ProfileUpdate,
        current_user: User,
    ) -> ProfileResponse:
        """更新档案。"""
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(profile_id)
        else:
            existing = await self.repository.get_by_id_and_user_or_family(
                profile_id, current_user.id
            )

        if not existing:
            raise NotFoundException("Profile not found")

        try:
            update_data = profile_data.model_dump(exclude_unset=True, exclude_none=True)
            if update_data.get("family_id") is not None:
                if not await self.family_repository.is_user_member(
                    update_data["family_id"], current_user.id
                ):
                    raise NotFoundException("Family not found")
            updated = await self.repository.update(profile_id, update_data)
            if not updated:
                raise NotFoundException("Profile not found")

            return ProfileResponse.model_validate(updated)
        except IntegrityError as e:
            raise AlreadyExistsException("Profile with this name already exists") from e

    async def delete_profile(self, profile_id: int, current_user: User) -> bool:
        """删除档案。"""
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(profile_id)
        else:
            existing = await self.repository.get_by_id_and_user_or_family(
                profile_id, current_user.id
            )

        if not existing:
            raise NotFoundException("Profile not found")

        deleted = await self.repository.delete(profile_id)
        if not deleted:
            raise NotFoundException("Profile not found")

        return True
