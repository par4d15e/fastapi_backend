from app.core.exception import NotFoundException
from app.reminders.repository import ReminderRepository
from app.reminders.schema import ReminderCreate, ReminderResponse, ReminderUpdate


class ReminderService:
    """Reminder 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    async def get_reminder_by_id(self, reminder_id: int) -> ReminderResponse:
        reminder = await self.repository.get_by_id(reminder_id)
        if not reminder:
            raise NotFoundException("Reminder not found")

        return ReminderResponse.model_validate(reminder)

    async def list_reminders(
        self,
        *,
        search: str | None = None,
        order_by: str = "id",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        """查询所有提醒"""
        reminders = await self.repository.get_all(
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
        *,
        order_by: str = "due_date",
        direction: str = "asc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        reminders = await self.repository.get_by_profile_id(
            profile_id,
            order_by=order_by,
            direction=direction,
            limit=limit,
            offset=offset,
        )
        return [ReminderResponse.model_validate(reminder) for reminder in reminders]

    async def search_reminders_by_title(
        self,
        keyword: str,
        *,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ReminderResponse]:
        """通过标题关键词模糊搜索提醒（pg_trgm GIN 索引加速）"""
        reminders = await self.repository.search_by_title_trgm(
            keyword,
            limit=limit,
            offset=offset,
        )
        return [ReminderResponse.model_validate(r) for r in reminders]

    async def create_reminder(self, reminder_data: ReminderCreate) -> ReminderResponse:
        data = reminder_data.model_dump()
        reminder = await self.repository.create(data)
        return ReminderResponse.model_validate(reminder)

    async def update_reminder(
        self,
        reminder_id: int,
        reminder_data: ReminderUpdate,
    ) -> ReminderResponse:
        update_data = reminder_data.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self.repository.update(reminder_id, update_data)
        if not updated:
            raise NotFoundException("Reminder not found")

        return ReminderResponse.model_validate(updated)

    async def delete_reminder(self, reminder_id: int) -> bool:
        deleted = await self.repository.delete(reminder_id)
        if not deleted:
            raise NotFoundException("Reminder not found")

        return True
