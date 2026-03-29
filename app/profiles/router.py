from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.user_manager import current_active_user
from app.core.database import get_session
from app.families.repository import FamilyRepository
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate, ProfileResponse, ProfileUpdate
from app.profiles.service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


# 依赖注入：为路由请求提供 ProfileService
async def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileService:
    """获取档案服务依赖。"""
    repository = ProfileRepository(session)
    family_repository = FamilyRepository(session)
    return ProfileService(repository, family_repository)


@router.post("/", response_model=ProfileResponse, status_code=201)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    """创建档案。"""
    new_profile = await service.create_profile(profile_data, current_user.id)
    return new_profile


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    search: Annotated[str | None, Query(description="搜索关键词")] = None,
    order_by: Annotated[str, Query(description="排序字段")] = "id",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "asc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    """列出档案列表。"""
    return await service.list_profiles(
        current_user,
        search=search,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/{profile_name}", response_model=ProfileResponse)
async def get_profile(
    profile_name: Annotated[str, Path(..., description="宠物名称")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    """获取指定档案。"""
    profile = await service.get_profile_by_name(profile_name, current_user)
    return profile


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    profile: ProfileUpdate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    """更新指定档案。"""
    return await service.update_profile(profile_id, profile, current_user)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    """删除指定档案。"""
    await service.delete_profile(profile_id, current_user)
    return None
