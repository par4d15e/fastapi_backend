from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.user_manager import current_active_user
from app.core.database import get_session
from app.families.repository import FamilyRepository
from app.families.schema import (
    FamilyInviteAccept,
    FamilyInviteCreate,
    FamilyInviteResponse,
    FamilyCreate,
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyResponse,
    FamilyUpdate,
)
from app.families.service import FamilyService

router = APIRouter(prefix="/families", tags=["families"])


async def get_family_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FamilyService:
    """获取家庭服务依赖。"""
    return FamilyService(FamilyRepository(session))


@router.post("/", response_model=FamilyResponse, status_code=201)
async def create_family(
    payload: FamilyCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """创建家庭。"""
    return await service.create_family(payload, current_user)


@router.get("/", response_model=list[FamilyResponse])
async def list_families(
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """列出家庭列表。"""
    return await service.list_families(current_user)


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """获取指定家庭。"""
    return await service.get_family(family_id, current_user)


@router.patch("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    payload: FamilyUpdate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """更新指定家庭。"""
    return await service.update_family(family_id, payload, current_user)


@router.delete("/{family_id}", status_code=204)
async def delete_family(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """删除指定家庭。"""
    await service.delete_family(family_id, current_user)
    return None


@router.post("/{family_id}/members", response_model=FamilyMemberResponse, status_code=201)
async def add_family_member(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    payload: FamilyMemberCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """向家庭中添加数据。"""
    return await service.add_member(family_id, payload, current_user)


@router.delete("/{family_id}/members/{user_id}", status_code=204)
async def remove_family_member(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    user_id: Annotated[str, Path(..., description="用户ID")],
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """从家庭中移除数据。"""
    await service.remove_member(family_id, user_id, current_user)
    return None


@router.post(
    "/{family_id}/invites", response_model=FamilyInviteResponse, status_code=201
)
async def create_family_invite(
    family_id: Annotated[int, Path(..., description="家庭ID")],
    payload: FamilyInviteCreate,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """创建家庭。"""
    return await service.create_invite(family_id, payload, current_user)


@router.post("/invites/accept", response_model=FamilyMemberResponse, status_code=201)
async def accept_family_invite(
    payload: FamilyInviteAccept,
    current_user: Annotated[User, Depends(current_active_user)],
    service: Annotated[FamilyService, Depends(get_family_service)],
):
    """接受家庭相关邀请。"""
    return await service.accept_invite(payload, current_user)
