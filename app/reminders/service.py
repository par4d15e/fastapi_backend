from app.auth.model import User
from app.core.exception import NotFoundException
from app.reminders.repository import ReminderRepository
from app.reminders.schema import ReminderCreate, ReminderResponse, ReminderUpdate


class ReminderService:
    """Reminder 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: ReminderRepository) -> None:
        """初始化ReminderService。"""
        self.repository = repository

    def _is_superuser(self, user: User) -> bool:
        """判断当前用户是否为超级管理员。"""
        return bool(getattr(user, "is_superuser", False))

    async def get_reminder_by_id(
        self,
        reminder_id: int,
        current_user: User,
    ) -> ReminderResponse:
        """根据 ID 获取提醒。"""
        if self._is_superuser(current_user):
            reminder = await self.repository.get_by_id(reminder_id)
        else:
            reminder = await self.repository.get_by_id_and_user_or_family(
                reminder_id, current_user.id
            )
        if not reminder:
            raise NotFoundException("Reminder not found")

        return ReminderResponse.model_validate(reminder)

    async def list_reminders(
        self,
        current_user: User,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        """列出当前用户可见的提醒。"""
        if self._is_superuser(current_user):
            reminders = await self.repository.get_all(
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            reminders = await self.repository.get_all_by_user_or_family(
                current_user.id,
                search=search,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )

        return [ReminderResponse.model_validate(reminder) for reminder in reminders]

    async def list_reminders_by_profile(
        self,
        profile_id: int,
        current_user: User,
        *,
        order_by: str = "due_date",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        """列出指定档案的提醒。"""
        if self._is_superuser(current_user):
            reminders = await self.repository.get_by_profile_id(
                profile_id,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            reminders = await self.repository.get_by_profile_id_and_user_or_family(
                profile_id,
                current_user.id,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        return [ReminderResponse.model_validate(reminder) for reminder in reminders]

    async def search_reminders_by_title(
        self,
        keyword: str,
        current_user: User,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        """按标题搜索提醒。"""
        if self._is_superuser(current_user):
            reminders = await self.repository.search_by_title_trgm(
                keyword,
                limit=limit,
                offset=offset,
            )
        else:
            reminders = await self.repository.search_by_title_trgm_and_user_or_family(
                keyword,
                user_id=current_user.id,
                limit=limit,
                offset=offset,
            )
        return [ReminderResponse.model_validate(r) for r in reminders]

    async def create_reminder(
        self,
        reminder_data: ReminderCreate,
        current_user: User,
    ) -> ReminderResponse:
        """创建提醒。"""
        data = reminder_data.model_dump()

        if not self._is_superuser(current_user):
            if not await self.repository.is_profile_accessible_by_user(
                data["profile_id"], current_user.id
            ):
                raise NotFoundException("Profile not found")

        reminder = await self.repository.create(data)
        return ReminderResponse.model_validate(reminder)

    async def update_reminder(
        self,
        reminder_id: int,
        reminder_data: ReminderUpdate,
        current_user: User,
    ) -> ReminderResponse:
        """更新提醒。"""
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(reminder_id)
        else:
            existing = await self.repository.get_by_id_and_user_or_family(
                reminder_id, current_user.id
            )
        if not existing:
            raise NotFoundException("Reminder not found")

        update_data = reminder_data.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self.repository.update(reminder_id, update_data)
        if not updated:
            raise NotFoundException("Reminder not found")

        return ReminderResponse.model_validate(updated)

    async def delete_reminder(self, reminder_id: int, current_user: User) -> bool:
        """删除提醒。"""
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(reminder_id)
        else:
            existing = await self.repository.get_by_id_and_user_or_family(
                reminder_id, current_user.id
            )
        if not existing:
            raise NotFoundException("Reminder not found")

        deleted = await self.repository.delete(reminder_id)
        if not deleted:
            raise NotFoundException("Reminder not found")

        return True
