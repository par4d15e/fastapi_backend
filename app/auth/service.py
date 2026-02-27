from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.models import RefreshToken, VerificationCode
from app.auth.repository import RefreshTokenCRUD, VerificationCodeCRUD
from app.auth.schemas import RefreshTokenCreate
from app.core.exception import NotFoundException


class AuthService:
    """Auth 服务层：封装与令牌/验证码相关的业务逻辑并调用 repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        # instantiate repos with the session
        self._refresh_repo = RefreshTokenCRUD(session)
        self._code_repo = VerificationCodeCRUD(session)

    # Refresh token related
    async def create_refresh_token(self, payload: RefreshTokenCreate) -> RefreshToken:
        # 这里不强制去重 token（token 应由调用方保证唯一），直接创建
        return await self._refresh_repo.create(
            user_id=payload.user_id,
            token=payload.token,
            expires_at=payload.expires_at,
            device_name=payload.device_name,
            device_type=payload.device_type,
            ip_address=payload.ip_address,
            user_agent=payload.user_agent,
        )

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return await self._refresh_repo.get_by_token(token)

    async def revoke(self, token: str) -> bool:
        db_token = await self._refresh_repo.get_by_token(token)
        if not db_token:
            raise NotFoundException("Refresh token not found")
        db_token.revoke()
        await self._session.commit()
        return True

    async def revoke_user_tokens(self, user_id: int) -> int:
        return await self._refresh_repo.revoke_user_tokens(user_id)

    async def cleanup_expired_refresh_tokens(self) -> int:
        return await self._refresh_repo.cleanup_expired()

    # Verification code related
    async def create_verification_code(
        self,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        return await self._code_repo.create(
            user_id=user_id,
            code_type=code_type,
            expiration_minutes=expiration_minutes,
            max_attempts=max_attempts,
        )

    async def get_verification_code(
        self, user_id: int, code: str, code_type: str
    ) -> Optional[VerificationCode]:
        return await self._code_repo.get(user_id, code, code_type)

    async def verify_code(
        self, user_id: int, code: str, code_type: str
    ) -> VerificationCode | None:
        db_code = await self._code_repo.get(user_id, code, code_type)
        if not db_code:
            raise NotFoundException("Verification code not found")

        # increment attempts and check validity inside repo/service
        db_code.increment_attempts()
        await self._session.commit()

        if not db_code.is_valid():
            return None

        db_code.mark_as_used()
        await self._session.commit()
        await self._session.refresh(db_code)
        return db_code

    async def get_latest_code(
        self, user_id: int, code_type: str
    ) -> Optional[VerificationCode]:
        return await self._code_repo.get_latest(user_id, code_type)

    async def invalidate_user_codes(self, user_id: int, code_type: str) -> int:
        return await self._code_repo.invalidate_user_codes(user_id, code_type)

    async def cleanup_expired_verification_codes(self) -> int:
        return await self._code_repo.cleanup_expired()
