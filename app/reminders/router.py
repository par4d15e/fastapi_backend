from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.exception import NotFoundException
from app.reminders.repository import ReminderRepository
from app.reminders.schema import ReminderCreate, ReminderResponse, ReminderUpdate
from app.reminders.service import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


# 依赖注入：为路由请求提供 ReminderService
async def get_reminder_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReminderService:
    repository = ReminderRepository(session)
    return ReminderService(repository)


@router.post("/", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    reminder_data: Annotated[ReminderCreate, Depends()],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    new_reminder = await service.create_reminder(reminder_data)
    return new_reminder


@router.get("/search", response_model=list[ReminderResponse])
async def search_reminders_by_title(
    keyword: Annotated[str, Query(..., description="标题关键词（支持模糊匹配）")],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.search_reminders_by_title(keyword, limit=limit, offset=offset)


@router.get("/{reminder_title}", response_model=ReminderResponse)
async def get_reminder(
    reminder_title: Annotated[str, Path(..., description="提醒事项标题")],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    reminder = await service.get_reminder_by_title(reminder_title)
    if not reminder:
        raise NotFoundException("Reminder not found")
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: Annotated[int, Path(..., description="提醒事项ID")],
    reminder: ReminderUpdate,
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    return await service.update_reminder(reminder_id, reminder)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: Annotated[int, Path(..., description="提醒事项ID")],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    await service.delete_reminder(reminder_id)
    return None
