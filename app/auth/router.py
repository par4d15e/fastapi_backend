import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.schemas import (
    RefreshTokenCreate,
    RefreshTokenResponse,
    VerificationCodeCreate,
    VerificationCodeResponse,
    VerificationCodeVerify,
)
from app.auth.service import AuthService
from app.core.database import get_session
from app.users.schema import Token, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


# 依赖注入：使用共享数据库会话提供 AuthService 实例
async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AuthService:
    return AuthService(session)


# ---------- 刷新令牌相关接口 ----------


@router.post(
    "/refresh-tokens",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_refresh_token(
    payload: RefreshTokenCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.create_refresh_token(payload)


@router.get(
    "/refresh-tokens/{token}",
    response_model=RefreshTokenResponse,
)
async def read_refresh_token(
    token: Annotated[str, Path(..., description="refresh token string")],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    result = await service.get_refresh_token(token)
    if not result:
        raise HTTPException(status_code=404, detail="Refresh token not found")
    return result


@router.delete(
    "/refresh-tokens/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_refresh_token(
    token: Annotated[str, Path(..., description="refresh token string")],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    ok = await service.revoke(token)
    if not ok:
        raise HTTPException(status_code=404, detail="Refresh token not found")
    return None


@router.delete(
    "/refresh-tokens/user/{user_id}",
    response_model=int,
)
async def revoke_user_tokens(
    user_id: Annotated[uuid.UUID, Path(..., description="user id")],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.revoke_user_tokens(user_id)


# ---------- 登录接口 ----------


@router.post("/login", response_model=Token)
async def login(
    creds: UserLogin,
    auth_svc: Annotated[AuthService, Depends(get_auth_service)],
):
    # use the new helper on AuthService; it raises NotFoundException on failure
    from app.core.exception import NotFoundException

    try:
        # model_validator on UserLogin guarantees at least one is non-null
        identifier = creds.username if creds.username is not None else creds.email  # type: ignore[assignment]
        assert identifier is not None
        return await auth_svc.login(identifier, creds.password)
    except NotFoundException as e:
        # translate our service-level exception into 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


# ---------- 验证码相关接口 ----------


@router.post(
    "/verification-codes",
    response_model=VerificationCodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_verification_code(
    payload: VerificationCodeCreate,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    # service 负责生成实际验证码和过期时间，此处仅计算并传入有效期分钟数
    expiration_minutes = 60
    try:
        delta = payload.expires_at - datetime.now(timezone.utc)
        expiration_minutes = int(delta.total_seconds() / 60)
    except Exception:
        expiration_minutes = 60

    return await service.create_verification_code(
        user_id=payload.user_id,
        code_type=payload.code_type,
        expiration_minutes=expiration_minutes,
        max_attempts=payload.max_attempts,
    )


@router.post(
    "/verification-codes/verify",
    response_model=VerificationCodeResponse | None,
)
async def verify_code(
    payload: VerificationCodeVerify,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.verify_code(
        user_id=payload.user_id,
        code=payload.code,
        code_type=payload.code_type,
    )


@router.get(
    "/verification-codes/{user_id}/{code_type}",
    response_model=VerificationCodeResponse | None,
)
async def get_latest_code(
    user_id: Annotated[uuid.UUID, Path(..., description="user id")],
    code_type: Annotated[str, Path(..., description="code type")],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.get_latest_code(user_id, code_type)


@router.delete(
    "/verification-codes/{user_id}/{code_type}",
    response_model=int,
)
async def invalidate_codes(
    user_id: Annotated[uuid.UUID, Path(..., description="user id")],
    code_type: Annotated[str, Path(..., description="code type")],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await service.invalidate_user_codes(user_id, code_type)
