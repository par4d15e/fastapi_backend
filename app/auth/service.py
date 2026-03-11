import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.model import Code, RefreshToken
from app.auth.repository import CodeCRUD, RefreshTokenCRUD
from app.auth.schemas import RefreshTokenCreate
from app.core.exception import NotFoundException
from app.core.security import create_access_token
from app.users.repository import UserRepository
from app.users.schema import Token as TokenSchema


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

    async def revoke_user_tokens(self, user_id: "uuid.UUID") -> int:
        return await self._refresh_repo.revoke_user_tokens(user_id)

    async def cleanup_expired_refresh_tokens(self) -> int:
        return await self._refresh_repo.cleanup_expired()

    # Verification code related
    async def create_verification_code(
        self,
        user_id: "uuid.UUID",
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
        self, user_id: "uuid.UUID", code: str, code_type: str
    ) -> Optional[Code]:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.get(user_id, code, enum_type)

    async def verify_code(
        self, user_id: "uuid.UUID", code: str, code_type: str
    ) -> Code | None:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        db_code = await self._code_repo.verify(user_id, code, enum_type)
        if not db_code:
            raise NotFoundException("Verification code not found")
        return db_code

    async def get_latest_code(
        self, user_id: "uuid.UUID", code_type: str
    ) -> Optional[Code]:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.get_latest(user_id, enum_type)

    async def invalidate_user_codes(self, user_id: "uuid.UUID", code_type: str) -> int:
        from app.auth.model import CodeType

        enum_type = CodeType[code_type] if isinstance(code_type, str) else code_type
        return await self._code_repo.invalidate_user_codes(user_id, enum_type)

    async def cleanup_expired_verification_codes(self) -> int:
        return await self._code_repo.cleanup_expired()

    # ---- authentication shortcut ----
    async def login(self, username_or_email: str, password: str) -> TokenSchema:
        """Validate credentials, emit a JWT token.

        This helper centralizes the traditional "login" flow.  It will
        issue both an access token and a persistent refresh token.
        """
        # use user repository directly to avoid circular imports
        user = await UserRepository(self._session).authenticate(
            username_or_email, password
        )
        if not user:
            # repository returns None on failure
            raise NotFoundException("Invalid username or password")

        # create access token using the uuid string as subject
        subject = str(user.uid)
        access = create_access_token(subject)

        # create a refresh token and persist it
        refresh_str = secrets.token_urlsafe(32)
        # expiration: use 30 days for now, can come from settings later
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        # `uid` is the primary key and should always be set after the user has been
        # loaded from the database, but help the type checker by asserting.
        assert user.uid is not None
        await self.create_refresh_token(
            RefreshTokenCreate(user_id=user.uid, token=refresh_str, expires_at=expires)
        )

        return TokenSchema(access_token=access, refresh_token=refresh_str)
