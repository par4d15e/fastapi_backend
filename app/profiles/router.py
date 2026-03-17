from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exception import NotFoundException
from app.profiles.repository import ProfileRepository
from app.profiles.schema import ProfileCreate, ProfileResponse, ProfileUpdate
from app.profiles.service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


# 依赖注入：为路由请求提供 ProfileService
async def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileService:
    repository = ProfileRepository(session)
    return ProfileService(repository)


@router.post("/", response_model=ProfileResponse, status_code=201)
async def create_profile(
    profile_data: ProfileCreate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    new_profile = await service.create_profile(profile_data)
    return new_profile


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(
    service: Annotated[ProfileService, Depends(get_profile_service)],
    search: Annotated[str | None, Query(description="搜索关键词")] = None,
    order_by: Annotated[str, Query(description="排序字段")] = "id",
    direction: Annotated[str, Query(description="排序方向 asc/desc")] = "asc",
    limit: Annotated[int, Query(ge=1, le=500, description="每页数量")] = 10,
    offset: Annotated[int, Query(ge=0, description="偏移量")] = 0,
):
    return await service.list_profiles(
        search=search,
        order_by=order_by,
        direction=direction,
        limit=limit,
        offset=offset,
    )


@router.get("/{profile_name}", response_model=ProfileResponse)
async def get_profile(
    profile_name: Annotated[str, Path(..., description="宠物名称")],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    profile = await service.get_profile_by_name(profile_name)
    if not profile:
        raise NotFoundException("Profile not found")
    return profile


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    profile: ProfileUpdate,
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    return await service.update_profile(profile_id, profile)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: Annotated[int, Path(..., description="宠物ID")],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    await service.delete_profile(profile_id)
    return None
