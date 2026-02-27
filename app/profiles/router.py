from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel.ext.asyncio.session import AsyncSession

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
    profile_data: Annotated[ProfileCreate, Depends()],
    service: Annotated[ProfileService, Depends(get_profile_service)],
):
    new_profile = await service.create_profile(profile_data)
    return new_profile


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
