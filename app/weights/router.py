from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.user_manager import current_active_user
from app.core.database import get_session
from app.weights.repository import WeightRecordRepository
from app.weights.schema import (
    WeightRecordCreate,
    WeightRecordResponse,
    WeightRecordUpdate,
)
from app.weights.service import WeightRecordService

router = APIRouter(prefix="/weights", tags=["weights"])


async def get_weight_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WeightRecordService:
    return WeightRecordService(WeightRecordRepository(session))


@router.post("/", response_model=WeightRecordResponse, status_code=201)
async def create_weight_record(
    record_data: WeightRecordCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
):
    """创建体重记录"""
    return await service.create_record(record_data, current_user)


@router.get("/", response_model=list[WeightRecordResponse])
async def list_weight_records(
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
    order_by: Annotated[str, Query(description="排序字段")] = "measured_at",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "desc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    """获取所有体重记录"""
    return await service.list_records(
        current_user,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/by-profile/{profile_id}", response_model=list[WeightRecordResponse])
async def list_weight_records_by_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
    order_by: Annotated[str, Query(description="排序字段")] = "measured_at",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "desc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    """获取指定宠物的体重记录列表"""
    return await service.list_records_by_profile(
        profile_id,
        current_user,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=WeightRecordResponse)
async def get_weight_record(
    record_id: Annotated[int, Path(..., description="体重记录ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
):
    """根据ID获取体重记录"""
    return await service.get_record_by_id(record_id, current_user)


@router.patch("/{record_id}", response_model=WeightRecordResponse)
async def update_weight_record(
    record_id: Annotated[int, Path(..., description="体重记录ID")],
    record_data: WeightRecordUpdate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
):
    """更新体重记录"""
    return await service.update_record(record_id, record_data, current_user)


@router.delete("/{record_id}", status_code=204)
async def delete_weight_record(
    record_id: Annotated[int, Path(..., description="体重记录ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[WeightRecordService, Depends(get_weight_service)],
):
    """删除体重记录"""
    await service.delete_record(record_id, current_user)
    return None
