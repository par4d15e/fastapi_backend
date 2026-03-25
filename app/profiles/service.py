from sqlalchemy.exc import IntegrityError

from app.core.exception import AlreadyExistsException, NotFoundException
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate, ProfileResponse, ProfileUpdate


class ProfileService:
    """Profile 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: ProfileRepository) -> None:
        self.repository = repository

    async def get_profile_by_name(
        self,
        profile_name: str,
        current_user_id: str,
    ) -> ProfileResponse:
        profile = await self.repository.get_by_name(profile_name, current_user_id)
        if not profile:
            raise NotFoundException("Profile not found")

        return ProfileResponse.model_validate(profile)

    async def get_profile_by_id(
        self,
        profile_id: int,
        current_user_id: str,
    ) -> ProfileResponse:
        profile = await self.repository.get_by_id_and_user(profile_id, current_user_id)
        if not profile:
            raise NotFoundException("Profile not found")

        return ProfileResponse.model_validate(profile)

    async def list_profiles(
        self,
        current_user_id: str,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ProfileResponse]:
        """查询指定用户的宠物档案"""
        profiles = await self.repository.get_all_by_user(
            current_user_id,
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
        current_user_id: str,
    ) -> ProfileResponse:
        data = profile_data.model_dump()
        data["user_id"] = current_user_id
        try:
            profile = await self.repository.create(data)
            return ProfileResponse.model_validate(profile)
        except IntegrityError as e:
            raise AlreadyExistsException("Profile with this name already exists") from e

    async def update_profile(
        self,
        profile_id: int,
        profile_data: ProfileUpdate,
        current_user_id: str,
    ) -> ProfileResponse:
        existing = await self.repository.get_by_id_and_user(profile_id, current_user_id)
        if not existing:
            raise NotFoundException("Profile not found")

        try:
            update_data = profile_data.model_dump(exclude_unset=True, exclude_none=True)
            updated = await self.repository.update(profile_id, update_data)
            if not updated:
                raise NotFoundException("Profile not found")

            return ProfileResponse.model_validate(updated)
        except IntegrityError as e:
            raise AlreadyExistsException("Profile with this name already exists") from e

    async def delete_profile(self, profile_id: int, current_user_id: str) -> bool:
        existing = await self.repository.get_by_id_and_user(profile_id, current_user_id)
        if not existing:
            raise NotFoundException("Profile not found")

        deleted = await self.repository.delete(profile_id)
        if not deleted:
            raise NotFoundException("Profile not found")

        return True
