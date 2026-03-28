from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.user_manager import current_active_user
from app.core.database import get_session
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
    reminder_data: ReminderCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    new_reminder = await service.create_reminder(reminder_data, current_user)
    return new_reminder


@router.get("/", response_model=list[ReminderResponse])
async def list_reminders(
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
    search: Annotated[str | None, Query(description="搜索关键词")] = None,
    order_by: Annotated[str, Query(description="排序字段")] = "id",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "asc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.list_reminders(
        current_user,
        search=search,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/by-profile/{profile_id}", response_model=list[ReminderResponse])
async def list_reminders_by_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
    order_by: Annotated[str, Query(description="排序字段")] = "due_date",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "asc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.list_reminders_by_profile(
        profile_id,
        current_user,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=list[ReminderResponse])
async def search_reminders_by_title(
    keyword: Annotated[str, Query(..., description="标题关键词（支持模糊匹配）")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.search_reminders_by_title(
        keyword, current_user, limit=limit, offset=offset
    )


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: Annotated[int, Path(..., description="提醒事项ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    return await service.get_reminder_by_id(reminder_id, current_user)


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: Annotated[int, Path(..., description="提醒事项ID")],
    reminder: ReminderUpdate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    return await service.update_reminder(reminder_id, reminder, current_user)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: Annotated[int, Path(..., description="提醒事项ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ReminderService, Depends(get_reminder_service)],
):
    await service.delete_reminder(reminder_id, current_user)
    return None
