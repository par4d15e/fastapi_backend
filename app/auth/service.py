import secrets
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.model import Code, RefreshToken
from app.auth.repository import CodeCRUD, RefreshTokenCRUD
from app.auth.schemas import RefreshTokenCreate
from app.core.exception import NotFoundException


class AuthService:
    """Auth 服务层：封装与令牌/验证码相关的业务逻辑并调用 repository"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        # instantiate repos with the session
        self._refresh_repo = RefreshTokenCRUD(session)
        self._code_repo = CodeCRUD(session)

    # Refresh token related
    async def create_refresh_token(self, payload: RefreshTokenCreate) -> RefreshToken:
        # jti 在服务层生成，调用方无需提供
        jti = secrets.token_urlsafe(16)
        return await self._refresh_repo.create(
            user_id=payload.user_id,
            jti=jti,
            token=payload.token,
            expired_at=payload.expires_at,
        )

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return await self._refresh_repo.get_by_token(token)

    async def revoke(self, token: str) -> bool:
        """通过仓库撤销令牌，若未找到则抛错误。"""
        ok = await self._refresh_repo.revoke(token)
        if not ok:
            raise NotFoundException("Refresh token not found")
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
    ) -> Code:
        # convert to enum before delegating to repo
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.create(
            user_id=user_id,
            code_type=enum_type,
            expiration_minutes=expiration_minutes,
        )

    async def get_verification_code(
        self, user_id: int, code: str, code_type: str
    ) -> Optional[Code]:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.get(user_id, code, enum_type)

    async def verify_code(self, user_id: int, code: str, code_type: str) -> Code | None:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        db_code = await self._code_repo.verify(user_id, code, enum_type)
        if not db_code:
            raise NotFoundException("Verification code not found")
        return db_code

    async def get_latest_code(self, user_id: int, code_type: str) -> Optional[Code]:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.get_latest(user_id, enum_type)

    async def invalidate_user_codes(self, user_id: int, code_type: str) -> int:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.invalidate_user_codes(user_id, enum_type)

    async def cleanup_expired_verification_codes(self) -> int:
        return await self._code_repo.cleanup_expired()
