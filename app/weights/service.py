from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.auth.model import User
from app.core.exception import NotFoundException
from app.weights.repository import WeightRecordRepository
from app.weights.schema import (
    WeightRecordCreate,
    WeightRecordResponse,
    WeightRecordUpdate,
)


class WeightRecordService:
    """WeightRecord 服务层：封装业务逻辑并调用 repository"""

    def __init__(self, repository: WeightRecordRepository) -> None:
        self.repository = repository

    def _is_superuser(self, user: User) -> bool:
        return bool(getattr(user, "is_superuser", False))

    async def get_record_by_id(
        self,
        record_id: int,
        current_user: User,
    ) -> WeightRecordResponse:
        if self._is_superuser(current_user):
            record = await self.repository.get_by_id(record_id)
        else:
            record = await self.repository.get_by_id_and_user(
                record_id, current_user.id
            )
        if not record:
            raise NotFoundException("WeightRecord not found")
        return WeightRecordResponse.model_validate(record)

    async def list_records_by_profile(
        self,
        profile_id: int,
        current_user: User,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecordResponse]:
        """查询指定宠物的体重记录列表"""
        if self._is_superuser(current_user):
            records = await self.repository.get_by_profile_id(
                profile_id,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            records = await self.repository.get_by_profile_id_and_user(
                profile_id,
                current_user.id,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        return [WeightRecordResponse.model_validate(r) for r in records]

    async def list_records(
        self,
        current_user: User,
        *,
        order_by: str = "measured_at",
        direction: str = "desc",
        limit: int = 10,
        offset: int = 0,
    ) -> list[WeightRecordResponse]:
        """查询所有体重记录"""
        if self._is_superuser(current_user):
            records = await self.repository.get_all(
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        else:
            records = await self.repository.get_all_by_user(
                current_user.id,
                order_by=order_by,
                direction=direction,
                limit=limit,
                offset=offset,
            )
        return [WeightRecordResponse.model_validate(r) for r in records]

    async def create_record(
        self,
        record_data: WeightRecordCreate,
        current_user: User,
    ) -> WeightRecordResponse:
        data = record_data.model_dump()
        if data.get("measured_at") is None:
            data["measured_at"] = datetime.now(tz=timezone.utc)

        if not self._is_superuser(current_user):
            owner = await self.repository.get_by_profile_id_and_user(
                data["profile_id"],
                current_user.id,
                limit=1,
            )
            if not owner:
                raise NotFoundException("Profile not found")

        try:
            record = await self.repository.create(data)
            return WeightRecordResponse.model_validate(record)
        except IntegrityError as e:
            raise NotFoundException("Profile not found") from e

    async def update_record(
        self,
        record_id: int,
        record_data: WeightRecordUpdate,
        current_user: User,
    ) -> WeightRecordResponse:
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(record_id)
        else:
            existing = await self.repository.get_by_id_and_user(
                record_id, current_user.id
            )
        if not existing:
            raise NotFoundException("WeightRecord not found")

        update_data = record_data.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self.repository.update(record_id, update_data)
        if not updated:
            raise NotFoundException("WeightRecord not found")
        return WeightRecordResponse.model_validate(updated)

    async def delete_record(self, record_id: int, current_user: User) -> bool:
        if self._is_superuser(current_user):
            existing = await self.repository.get_by_id(record_id)
        else:
            existing = await self.repository.get_by_id_and_user(
                record_id, current_user.id
            )
        if not existing:
            raise NotFoundException("WeightRecord not found")

        deleted = await self.repository.delete(record_id)
        if not deleted:
            raise NotFoundException("WeightRecord not found")
        return True
