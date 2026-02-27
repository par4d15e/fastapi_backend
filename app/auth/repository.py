"""Token and verification code CRUD operations - sqlmodel"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.models import RefreshToken, VerificationCode


class RefreshTokenCRUD:
    """刷新令牌 CRUD 操作类"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
        device_name: str | None = None,
        device_type: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> RefreshToken:
        """创建新的刷新令牌记录"""
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_name=device_name,
            device_type=device_type,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """根据令牌字符串获取刷新令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def get_user_tokens(
        self, user_id: int, include_revoked: bool = False
    ) -> list[RefreshToken]:
        """获取属于指定用户的所有刷新令牌"""
        statement = select(RefreshToken).where(RefreshToken.user_id == user_id)

        if not include_revoked:
            statement = statement.where(RefreshToken.is_revoked.is_(False))  # type: ignore

        result = await self.session.exec(statement)
        return list(result.all())

    async def update_last_used(self, token_id: int) -> RefreshToken | None:
        """更新令牌的最后使用时间"""
        statement = select(RefreshToken).where(RefreshToken.id == token_id)
        result = await self.session.exec(statement)
        db_token = result.one_or_none()
        if not db_token:
            return None

        db_token.last_used_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(db_token)
        return db_token

    async def revoke(self, token: str) -> bool:
        """撤销刷新令牌"""
        db_token = await self.get_by_token(token)
        if not db_token:
            return False

        db_token.revoke()
        await self.session.commit()
        return True

    async def revoke_user_tokens(self, user_id: int) -> int:
        """撤销用户的所有刷新令牌"""
        tokens = await self.get_user_tokens(user_id, include_revoked=False)

        count = 0
        for token in tokens:
            token.revoke()
            count += 1

        await self.session.commit()
        return count

    async def cleanup_expired(self) -> int:
        """撤销已过期的令牌"""
        statement = select(RefreshToken).where(
            RefreshToken.expires_at < datetime.now(timezone.utc),
            RefreshToken.is_revoked.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        expired_tokens = list(result.all())

        count = 0
        for token in expired_tokens:
            token.revoke()
            count += 1

        await self.session.commit()
        return count


class VerificationCodeCRUD:
    """验证码 CRUD 操作类"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def generate_code(self, length: int = 6) -> str:
        """生成数字验证码"""
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])

    async def create(
        self,
        user_id: int,
        code_type: str,
        expiration_minutes: int = 60,
        max_attempts: int = 5,
    ) -> VerificationCode:
        """创建验证码"""
        code = self.generate_code()

        db_code = VerificationCode(
            user_id=user_id,
            code=code,
            code_type=code_type,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=expiration_minutes),
            max_attempts=max_attempts,
        )

        self.session.add(db_code)
        await self.session.commit()
        await self.session.refresh(db_code)
        return db_code

    async def get(
        self, user_id: int, code: str, code_type: str
    ) -> VerificationCode | None:
        """获取验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code == code,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def verify(
        self, user_id: int, code: str, code_type: str
    ) -> VerificationCode | None:
        """验证验证码"""
        db_code = await self.get(user_id, code, code_type)

        if not db_code:
            return None

        # Increment attempt count
        db_code.increment_attempts()
        await self.session.commit()

        # Check whether valid
        if not db_code.is_valid():
            return None

        # Mark as used
        db_code.mark_as_used()
        await self.session.commit()
        await self.session.refresh(db_code)

        return db_code

    async def get_latest(self, user_id: int, code_type: str) -> VerificationCode | None:
        """获取用户最新的验证码"""
        statement = (
            select(VerificationCode)
            .where(
                VerificationCode.user_id == user_id,
                VerificationCode.code_type == code_type,
            )
            .order_by(VerificationCode.created_at.desc())  # type: ignore
        )
        result = await self.session.exec(statement)
        return result.one_or_none()

    async def invalidate_user_codes(self, user_id: int, code_type: str) -> int:
        """使用户所有未使用的验证码失效"""
        statement = select(VerificationCode).where(
            VerificationCode.user_id == user_id,
            VerificationCode.code_type == code_type,
            VerificationCode.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        codes = list(result.all())

        count = 0
        for code in codes:
            code.mark_as_used()
            count += 1

        await self.session.commit()
        return count

    async def cleanup_expired(self) -> int:
        """清理过期的验证码"""
        statement = select(VerificationCode).where(
            VerificationCode.expires_at < datetime.now(timezone.utc),
            VerificationCode.is_used.is_(False),  # type: ignore
        )
        result = await self.session.exec(statement)
        expired_codes = list(result.all())

        count = 0
        for code in expired_codes:
            code.mark_as_used()
            count += 1

        await self.session.commit()
        return count
